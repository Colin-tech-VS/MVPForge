"""Stripe Checkout — frais de mise en ligne et achats MVP."""

from __future__ import annotations

from flask import url_for

from constants import LISTING_FEE_CENTS
from models.mvp import MvpProject
from models.purchase import MvpPurchase
from utils.listing_fee import listing_fee_label


def stripe_enabled() -> bool:
    from flask import current_app

    return bool(current_app.config.get("STRIPE_SECRET_KEY"))


def _stripe():
    import stripe
    from flask import current_app

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    return stripe


def retrieve_checkout_session(session_id: str) -> dict | None:
    if not stripe_enabled():
        return None
    stripe = _stripe()
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return None
    return {
        "id": session.id,
        "payment_status": session.payment_status,
        "payment_intent": session.payment_intent,
        "metadata": dict(session.metadata or {}),
    }


def _session_paid(session_id: str, kind: str, **meta_match) -> bool:
    data = retrieve_checkout_session(session_id)
    if not data or data.get("payment_status") != "paid":
        return False
    meta = data.get("metadata") or {}
    if meta.get("mvpforge_kind") != kind:
        return False
    for key, value in meta_match.items():
        if meta.get(key) != value:
            return False
    return True


def session_paid_for_listing(session_id: str, project_id: str) -> bool:
    return _session_paid(session_id, "listing_fee", project_id=project_id)


def session_paid_for_purchase(session_id: str, purchase_id: str) -> bool:
    return _session_paid(session_id, "project_purchase", purchase_id=purchase_id)


def create_listing_checkout_session(project: MvpProject, customer_email: str) -> dict:
    stripe = _stripe()
    success_url = (
        url_for(
            "account.listing_payment_success",
            project_id=project.id,
            _external=True,
        )
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = url_for(
        "account.listing_payment",
        project_id=project.id,
        _external=True,
    )

    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=customer_email,
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": "eur",
                    "unit_amount": LISTING_FEE_CENTS,
                    "product_data": {
                        "name": f"Mise en ligne — {project.title}",
                        "description": (
                            f"Publication sur le catalogue MVPForge "
                            f"({listing_fee_label()} TTC · en ligne ou hors ligne)"
                        ),
                    },
                },
            }
        ],
        metadata={
            "mvpforge_kind": "listing_fee",
            "project_id": project.id,
        },
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"session_id": session.id, "url": session.url}


def create_purchase_checkout_session(
    purchase: MvpPurchase, customer_email: str
) -> dict:
    stripe = _stripe()
    project = purchase.project
    success_url = (
        url_for(
            "purchases.purchase_success",
            purchase_id=purchase.id,
            _external=True,
        )
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = url_for(
        "purchases.purchase_checkout",
        purchase_id=purchase.id,
        _external=True,
    )

    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=customer_email,
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": "eur",
                    "unit_amount": purchase.amount_cents,
                    "product_data": {
                        "name": f"Achat MVP — {project.title}",
                        "description": (
                            f"{project.tagline[:200]} — "
                            "Transfert sécurisé après paiement."
                        ),
                    },
                },
            }
        ],
        metadata={
            "mvpforge_kind": "project_purchase",
            "purchase_id": purchase.id,
            "project_id": project.id,
            "buyer_id": purchase.buyer_id,
        },
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"session_id": session.id, "url": session.url}
