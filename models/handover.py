"""Dossier de passation d'un projet — préparé par le vendeur, débloqué à
l'acheteur après paiement. Les champs sensibles sont chiffrés au repos."""

import uuid
from datetime import datetime, timezone

from extensions import db
from utils.crypto import decrypt, encrypt


class ProjectHandover(db.Model):
    __tablename__ = "mvp_handovers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(
        db.String(36),
        db.ForeignKey("mvp_projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Contenu du dossier (texte libre, non sensible).
    repo_url = db.Column(db.String(500), nullable=True)
    deploy_notes = db.Column(db.Text, nullable=True)
    domains = db.Column(db.Text, nullable=True)
    accounts = db.Column(db.Text, nullable=True)
    data_notes = db.Column(db.Text, nullable=True)
    analytics_access = db.Column(db.Text, nullable=True)
    legal_notes = db.Column(db.Text, nullable=True)

    # Sensible — chiffré (voir utils/crypto).
    secrets_enc = db.Column(db.Text, nullable=True)
    github_token_enc = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = db.relationship(
        "MvpProject", backref=db.backref("handover", uselist=False, cascade="all, delete-orphan")
    )

    # --- secrets (chiffrés) ---
    @property
    def secrets(self) -> str:
        return decrypt(self.secrets_enc)

    @secrets.setter
    def secrets(self, value: str | None) -> None:
        self.secrets_enc = encrypt(value)

    @property
    def github_token(self) -> str:
        return decrypt(self.github_token_enc)

    @github_token.setter
    def github_token(self, value: str | None) -> None:
        self.github_token_enc = encrypt(value)

    def is_ready(self) -> bool:
        """Vrai si le vendeur a renseigné au moins l'essentiel de la passation."""
        return bool(self.repo_url or self.deploy_notes or self.secrets_enc)
