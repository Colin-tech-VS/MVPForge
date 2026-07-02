import uuid
from datetime import datetime, timezone

from extensions import db


class MvpPurchase(db.Model):
    __tablename__ = "mvp_purchases"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(
        db.String(36), db.ForeignKey("mvp_projects.id"), nullable=False, index=True
    )
    buyer_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False, index=True
    )
    amount_cents = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    stripe_checkout_session_id = db.Column(db.String(255), nullable=True)

    # Séquestre / reversement vendeur (Stripe Connect).
    platform_fee_cents = db.Column(db.Integer, nullable=True)
    seller_amount_cents = db.Column(db.Integer, nullable=True)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True)
    stripe_transfer_id = db.Column(db.String(255), nullable=True)
    buyer_confirmed_at = db.Column(db.DateTime, nullable=True)
    released_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    paid_at = db.Column(db.DateTime, nullable=True)

    project = db.relationship("MvpProject", backref=db.backref("purchases", lazy="dynamic"))
    buyer = db.relationship("User", backref=db.backref("purchases", lazy="dynamic"))

    def formatted_amount(self) -> str:
        return f"{self.amount_cents // 100:,}".replace(",", " ")

    def status_label(self) -> str:
        labels = {
            "pending": "En attente",
            "paid": "Payé — passation en cours",
            "released": "Finalisé",
            "refunded": "Remboursé",
            "cancelled": "Annulé",
        }
        return labels.get(self.status, self.status)

    def is_paid(self) -> bool:
        # "paid" (fonds en séquestre) ou "released" (reversé) = achat honoré.
        return self.status in ("paid", "released")

    def is_released(self) -> bool:
        return self.status == "released"

    def formatted_seller_amount(self) -> str:
        cents = self.seller_amount_cents or 0
        return f"{cents // 100:,}".replace(",", " ")
