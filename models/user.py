import uuid
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    company = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    external_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    auth_provider = db.Column(db.String(20), nullable=False, default="local")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def display_name(self) -> str:
        return self.name or self.email.split("@")[0]

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_auth_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name or self.email.split("@")[0],
        }
