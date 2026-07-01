"""Activation catalogue après paiement des frais de mise en ligne."""

from datetime import datetime, timezone

from constants import LISTING_FEE_CENTS, PROJECT_STATUS_PENDING_PAYMENT, PROJECT_STATUS_PUBLISHED
from extensions import db
from models.mvp import MvpProject


def fulfill_listing_payment(
    project: MvpProject,
    *,
    session_id: str | None = None,
    amount_cents: int = LISTING_FEE_CENTS,
) -> bool:
    if project.status != PROJECT_STATUS_PENDING_PAYMENT:
        return False

    project.status = PROJECT_STATUS_PUBLISHED
    project.listing_fee_paid = True
    project.listing_fee_paid_at = datetime.now(timezone.utc)
    project.listing_fee_amount_cents = amount_cents
    if session_id:
        project.stripe_checkout_session_id = session_id
    db.session.commit()
    return True
