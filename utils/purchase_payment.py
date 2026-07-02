"""Finalisation achat MVP après paiement Stripe."""

from datetime import datetime, timezone

from constants import PROJECT_STATUS_SOLD, PURCHASE_STATUS_PAID
from extensions import db
from models.purchase import MvpPurchase
from utils.stripe_connect import compute_split


def get_or_create_pending_purchase(project, buyer_id: str) -> MvpPurchase | None:
    if not project.is_purchasable():
        return None
    if project.user_id == buyer_id:
        return None

    existing = (
        MvpPurchase.query.filter_by(
            project_id=project.id,
            buyer_id=buyer_id,
            status="pending",
        )
        .order_by(MvpPurchase.created_at.desc())
        .first()
    )
    if existing:
        return existing

    purchase = MvpPurchase(
        project_id=project.id,
        buyer_id=buyer_id,
        amount_cents=project.price * 100,
        status="pending",
    )
    db.session.add(purchase)
    db.session.commit()
    return purchase


def fulfill_project_purchase(
    purchase: MvpPurchase,
    *,
    session_id: str | None = None,
    payment_intent: str | None = None,
) -> bool:
    # Déjà payé (fonds en séquestre) ou reversé : rien à refaire.
    if purchase.status in (PURCHASE_STATUS_PAID, "released"):
        return True

    project = purchase.project
    if not project or not project.is_purchasable():
        return False

    now = datetime.now(timezone.utc)
    purchase.status = PURCHASE_STATUS_PAID  # fonds détenus en séquestre
    purchase.paid_at = now
    if session_id:
        purchase.stripe_checkout_session_id = session_id
    if payment_intent:
        purchase.stripe_payment_intent_id = payment_intent

    fee, seller_amount = compute_split(purchase.amount_cents)
    purchase.platform_fee_cents = fee
    purchase.seller_amount_cents = seller_amount

    project.status = PROJECT_STATUS_SOLD
    project.buyer_id = purchase.buyer_id
    project.sold_at = now

    db.session.commit()

    _notify_fulfilled(purchase)
    return True


def _notify_fulfilled(purchase: MvpPurchase) -> None:
    try:
        from utils.email import notify_buyer_handover, notify_sale

        notify_sale(purchase)
        notify_buyer_handover(purchase)
    except Exception:
        pass


def confirm_and_release(purchase: MvpPurchase) -> bool:
    """L'acheteur confirme la réception : déclenche le reversement au vendeur."""
    from utils.stripe_connect import release_to_seller

    if purchase.buyer_confirmed_at is None:
        purchase.buyer_confirmed_at = datetime.now(timezone.utc)
        db.session.commit()

    # Best-effort : si Connect/vendeur pas prêts, l'achat reste confirmé côté
    # acheteur et le reversement pourra être rejoué plus tard.
    released = release_to_seller(purchase)
    if released:
        try:
            from utils.email import notify_payout

            notify_payout(purchase)
        except Exception:
            pass
    return released
