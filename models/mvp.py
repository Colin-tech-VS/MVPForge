import json
import uuid
from datetime import datetime, timezone

from extensions import db


class MvpProject(db.Model):
    __tablename__ = "mvp_projects"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    stack = db.Column(db.String(500), nullable=False, default="")
    color = db.Column(db.String(7), nullable=False, default="#1A6B52")
    status = db.Column(db.String(20), nullable=False, default="published", index=True)

    buyer_id = db.Column(
        db.String(36), db.ForeignKey("users.id"), nullable=True, index=True
    )
    sold_at = db.Column(db.DateTime, nullable=True)

    is_online = db.Column(db.Boolean, nullable=False, default=False)
    monthly_visitors = db.Column(db.Integer, nullable=True)
    monthly_revenue = db.Column(db.Integer, nullable=True)
    launch_date = db.Column(db.Date, nullable=True)
    site_url = db.Column(db.String(500), nullable=True)
    github_url = db.Column(db.String(500), nullable=True)
    monetization = db.Column(db.String(500), nullable=True, default="")
    traffic_source = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    resale_reason = db.Column(db.Text, nullable=True)

    page_views = db.Column(db.Integer, nullable=True)
    sessions_count = db.Column(db.Integer, nullable=True)
    bounce_rate = db.Column(db.Float, nullable=True)
    avg_duration = db.Column(db.String(20), nullable=True)
    profile_views = db.Column(db.Integer, nullable=True)
    engagement_count = db.Column(db.Integer, nullable=True)
    conversion_count = db.Column(db.Integer, nullable=True)
    conversion_rate = db.Column(db.Float, nullable=True)
    analytics_period_days = db.Column(db.Integer, nullable=True)
    analytics_extra = db.Column(db.Text, nullable=True)

    listing_fee_paid = db.Column(db.Boolean, nullable=False, default=False)
    listing_fee_paid_at = db.Column(db.DateTime, nullable=True)
    listing_fee_amount_cents = db.Column(db.Integer, nullable=True)
    stripe_checkout_session_id = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    seller = db.relationship("User", backref=db.backref("mvp_projects", lazy="dynamic"), foreign_keys=[user_id])
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    images = db.relationship(
        "MvpImage",
        backref="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="MvpImage.sort_order",
    )

    @property
    def stack_list(self) -> list[str]:
        if not self.stack:
            return []
        return [s.strip() for s in self.stack.split(",") if s.strip()]

    @property
    def monetization_list(self) -> list[str]:
        if not self.monetization:
            return []
        return [m.strip() for m in self.monetization.split("|") if m.strip()]

    @property
    def cover_image(self):
        return self.images.order_by(MvpImage.sort_order).first()

    def formatted_price(self) -> str:
        return f"{self.price:,}".replace(",", " ")

    def formatted_launch_date(self) -> str | None:
        if not self.launch_date:
            return None
        months = (
            "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre",
        )
        day = "1er" if self.launch_date.day == 1 else str(self.launch_date.day)
        return f"{day} {months[self.launch_date.month - 1]} {self.launch_date.year}"

    def is_catalogue_visible(self) -> bool:
        return self.status == "published"

    def is_sold(self) -> bool:
        return self.status == "sold"

    def is_purchasable(self) -> bool:
        return self.status == "published" and not self.is_sold()

    def status_label(self) -> str:
        labels = {
            "published": "Publié",
            "pending_payment": "Paiement requis",
            "sold": "Vendu",
            "draft": "Brouillon",
        }
        return labels.get(self.status, self.status)

    def _fmt_num(self, value: int) -> str:
        return f"{value:,}".replace(",", " ")

    def _has_analytics_band(self) -> bool:
        return any(
            value is not None
            for value in (
                self.page_views,
                self.sessions_count,
                self.profile_views,
                self.engagement_count,
                self.conversion_count,
            )
        )

    def _analytics_label_overrides(self) -> dict[str, str]:
        if not self.analytics_extra:
            return {}
        try:
            data = json.loads(self.analytics_extra)
        except (json.JSONDecodeError, TypeError):
            return {}
        return data.get("metric_labels", {})

    def analytics_metrics(self) -> list[dict]:
        if not self._has_analytics_band():
            return []

        overrides = self._analytics_label_overrides()
        metrics: list[dict] = []
        if self.monthly_visitors is not None:
            metrics.append(
                {
                    "label": "Visiteurs uniques",
                    "value": self._fmt_num(self.monthly_visitors),
                    "accent": True,
                }
            )
        if self.page_views is not None:
            metrics.append(
                {"label": "Pages vues", "value": self._fmt_num(self.page_views)}
            )
        if self.sessions_count is not None:
            metrics.append(
                {"label": "Sessions", "value": self._fmt_num(self.sessions_count)}
            )
        if self.avg_duration:
            metrics.append(
                {"label": "Durée moyenne", "value": self.avg_duration}
            )
        if self.profile_views is not None:
            metrics.append(
                {
                    "label": overrides.get("profile_views", "Vues profils / pages clés"),
                    "value": self._fmt_num(self.profile_views),
                }
            )
        if self.engagement_count is not None:
            metrics.append(
                {
                    "label": overrides.get("engagement_count", "Engagements (likes, soutiens…)"),
                    "value": self._fmt_num(self.engagement_count),
                }
            )
        if self.conversion_count is not None:
            metrics.append(
                {
                    "label": overrides.get(
                        "conversion_count", "Conversions (inscriptions, essais…)"
                    ),
                    "value": self._fmt_num(self.conversion_count),
                }
            )
        return metrics

class MvpImage(db.Model):
    __tablename__ = "mvp_images"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(
        db.String(36), db.ForeignKey("mvp_projects.id"), nullable=False, index=True
    )
    filename = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
