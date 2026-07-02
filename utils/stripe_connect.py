"""Stripe Connect — comptes vendeurs, séquestre et reversement.

Modèle : l'acheteur paie sur le compte plateforme (Checkout classique). Les
fonds sont détenus en séquestre jusqu'à confirmation de la passation par
l'acheteur, puis reversés au vendeur (moins la commission) via un Transfer
vers son compte Connect.

Tout est neutralisé tant que STRIPE_SECRET_KEY n'est pas configurée.
"""

from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app

from constants import (
    PLATFORM_COMMISSION_PCT,
    PURCHASE_STATUS_REFUNDED,
    PURCHASE_STATUS_RELEASED,
)
from extensions import db
from utils.stripe_checkout import _stripe, stripe_enabled


def connect_enabled() -> bool:
    return stripe_enabled()


def compute_split(amount_cents: int) -> tuple[int, int]:
    """Retourne (commission_plateforme, montant_vendeur) en centimes."""
    fee = amount_cents * PLATFORM_COMMISSION_PCT // 100
    return fee, amount_cents - fee


def create_or_get_account(user) -> str:
    """Crée (ou réutilise) le compte Connect Express du vendeur."""
    if user.stripe_account_id:
        return user.stripe_account_id
    stripe = _stripe()
    account = stripe.Account.create(
        type="express",
        email=user.email,
        capabilities={"transfers": {"requested": True}},
        business_type="individual",
        metadata={"mvpforge_user_id": user.id},
    )
    user.stripe_account_id = account.id
    db.session.commit()
    return account.id


def create_account_link(user, refresh_url: str, return_url: str) -> str:
    stripe = _stripe()
    account_id = create_or_get_account(user)
    link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )
    return link.url


def refresh_account_status(user) -> bool:
    """Interroge Stripe et met à jour user.stripe_onboarded. Retourne l'état."""
    if not user.stripe_account_id or not stripe_enabled():
        return False
    stripe = _stripe()
    try:
        account = stripe.Account.retrieve(user.stripe_account_id)
    except Exception:
        return user.stripe_onboarded
    ready = bool(
        getattr(account, "details_submitted", False)
        and getattr(account, "payouts_enabled", False)
    )
    if ready != user.stripe_onboarded:
        user.stripe_onboarded = ready
        db.session.commit()
    return ready


def release_to_seller(purchase) -> bool:
    """Reverse le montant vendeur (séquestre → compte Connect). Idempotent."""
    if purchase.status == PURCHASE_STATUS_RELEASED:
        return True
    if not stripe_enabled():
        return False

    seller = purchase.project.seller if purchase.project else None
    if not seller or not seller.can_receive_payouts():
        return False

    seller_amount = purchase.seller_amount_cents
    if not seller_amount or not purchase.stripe_payment_intent_id:
        return False

    stripe = _stripe()
    try:
        intent = stripe.PaymentIntent.retrieve(purchase.stripe_payment_intent_id)
        charge_id = getattr(intent, "latest_charge", None)
        transfer = stripe.Transfer.create(
            amount=seller_amount,
            currency="eur",
            destination=seller.stripe_account_id,
            source_transaction=charge_id,
            metadata={"mvpforge_purchase_id": purchase.id},
        )
    except Exception:
        return False

    purchase.stripe_transfer_id = transfer.id
    purchase.status = PURCHASE_STATUS_RELEASED
    purchase.released_at = datetime.now(timezone.utc)
    db.session.commit()
    return True


def refund_purchase(purchase) -> bool:
    if not stripe_enabled() or not purchase.stripe_payment_intent_id:
        return False
    stripe = _stripe()
    try:
        stripe.Refund.create(payment_intent=purchase.stripe_payment_intent_id)
    except Exception:
        return False
    purchase.status = PURCHASE_STATUS_REFUNDED
    db.session.commit()
    return True
