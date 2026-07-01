import re

from flask import session

from auth.providers import AuthUser
from extensions import db
from models.user import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))


def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caractères."
    return None


class LocalAuthProvider:
    def register(self, email: str, password: str, name: str | None = None) -> "AuthResult":
        from auth.providers import AuthResult

        email = email.strip().lower()
        if not validate_email(email):
            return AuthResult(success=False, error="Adresse e-mail invalide.")
        pwd_error = validate_password(password)
        if pwd_error:
            return AuthResult(success=False, error=pwd_error)
        if User.query.filter_by(email=email).first():
            return AuthResult(success=False, error="Un compte existe déjà avec cet e-mail.")

        user = User(email=email, name=(name or "").strip() or None, auth_provider="local")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return AuthResult(
            success=True,
            user=AuthUser(
                id=user.id,
                email=user.email,
                name=user.name or user.email.split("@")[0],
                provider="local",
            ),
        )

    def login(self, email: str, password: str) -> "AuthResult":
        from auth.providers import AuthResult

        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return AuthResult(success=False, error="E-mail ou mot de passe incorrect.")

        return AuthResult(
            success=True,
            user=AuthUser(
                id=user.id,
                email=user.email,
                name=user.name or user.email.split("@")[0],
                provider="local",
            ),
        )


def login_user(user: AuthUser) -> None:
    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_name"] = user.name
    session["auth_provider"] = user.provider
    session.permanent = True


def logout_user() -> None:
    session.pop("user_id", None)
    session.pop("user_email", None)
    session.pop("user_name", None)
    session.pop("auth_provider", None)
    session.pop("supabase_access_token", None)
    session.pop("supabase_refresh_token", None)


def get_current_user() -> AuthUser | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return AuthUser(
        id=user_id,
        email=session.get("user_email", ""),
        name=session.get("user_name", ""),
        provider=session.get("auth_provider", "local"),
    )


def sync_session_user(user: User) -> None:
    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_name"] = user.display_name()
    session["auth_provider"] = user.auth_provider
