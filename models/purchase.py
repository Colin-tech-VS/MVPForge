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
            "paid": "Payé",
            "cancelled": "Annulé",
        }
        return labels.get(self.status, self.status)

    def is_paid(self) -> bool:
        return self.status == "paid"
