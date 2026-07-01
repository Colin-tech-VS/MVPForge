"""Finalisation achat MVP après paiement Stripe."""

from datetime import datetime, timezone

from constants import PROJECT_STATUS_SOLD, PURCHASE_STATUS_PAID
from extensions import db
from models.purchase import MvpPurchase


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
) -> bool:
    if purchase.status == PURCHASE_STATUS_PAID:
        return True

    project = purchase.project
    if not project or not project.is_purchasable():
        return False

    now = datetime.now(timezone.utc)
    purchase.status = PURCHASE_STATUS_PAID
    purchase.paid_at = now
    if session_id:
        purchase.stripe_checkout_session_id = session_id

    project.status = PROJECT_STATUS_SOLD
    project.buyer_id = purchase.buyer_id
    project.sold_at = now

    db.session.commit()
    return True
