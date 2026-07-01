from auth.local_provider import validate_email, validate_password
from auth.providers import AuthResult, AuthUser
from extensions import db
from models.user import User


class SupabaseAuthProvider:
    def __init__(self):
        from flask import current_app

        url = current_app.config.get("SUPABASE_URL")
        key = current_app.config.get("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL et SUPABASE_KEY sont requis quand AUTH_BACKEND=supabase."
            )
        from supabase import create_client

        self.client = create_client(url, key)

    def register(self, email: str, password: str, name: str | None = None) -> AuthResult:
        email = email.strip().lower()
        if not validate_email(email):
            return AuthResult(success=False, error="Adresse e-mail invalide.")
        pwd_error = validate_password(password)
        if pwd_error:
            return AuthResult(success=False, error=pwd_error)

        try:
            metadata = {}
            if name and name.strip():
                metadata["full_name"] = name.strip()

            response = self.client.auth.sign_up(
                {"email": email, "password": password, "options": {"data": metadata}}
            )
        except Exception as exc:
            return AuthResult(success=False, error=self._format_error(exc))

        if not response.user:
            return AuthResult(success=False, error="Inscription impossible. Réessayez.")

        user = self._sync_user(response.user, name)
        return AuthResult(
            success=True,
            user=AuthUser(
                id=user.id,
                email=user.email,
                name=user.name or user.email.split("@")[0],
                provider="supabase",
            ),
            tokens=self._extract_tokens(response),
        )

    def login(self, email: str, password: str) -> AuthResult:
        email = email.strip().lower()
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
        except Exception as exc:
            return AuthResult(success=False, error=self._format_error(exc))

        if not response.user:
            return AuthResult(success=False, error="E-mail ou mot de passe incorrect.")

        user = self._sync_user(response.user)
        return AuthResult(
            success=True,
            user=AuthUser(
                id=user.id,
                email=user.email,
                name=user.name or user.email.split("@")[0],
                provider="supabase",
            ),
            tokens=self._extract_tokens(response),
        )

    def _sync_user(self, supabase_user, name: str | None = None) -> User:
        external_id = supabase_user.id
        email = (supabase_user.email or "").lower()
        meta_name = None
        if supabase_user.user_metadata:
            meta_name = supabase_user.user_metadata.get("full_name")

        user = User.query.filter_by(external_id=external_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                email=email,
                external_id=external_id,
                auth_provider="supabase",
            )
            db.session.add(user)

        user.external_id = external_id
        user.email = email
        user.auth_provider = "supabase"
        if name and name.strip():
            user.name = name.strip()
        elif meta_name:
            user.name = meta_name

        db.session.commit()
        return user

    def _extract_tokens(self, response) -> dict | None:
        if not response.session:
            return None
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

    def _format_error(self, exc: Exception) -> str:
        msg = str(exc)
        if "already registered" in msg.lower() or "already exists" in msg.lower():
            return "Un compte existe déjà avec cet e-mail."
        if "invalid login" in msg.lower() or "invalid credentials" in msg.lower():
            return "E-mail ou mot de passe incorrect."
        return "Une erreur est survenue. Réessayez."
