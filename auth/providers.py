from dataclasses import dataclass
from typing import Protocol

from flask import current_app


@dataclass
class AuthUser:
    id: str
    email: str
    name: str
    provider: str = "local"


@dataclass
class AuthResult:
    success: bool
    user: AuthUser | None = None
    error: str | None = None
    tokens: dict | None = None


class AuthProvider(Protocol):
    def register(self, email: str, password: str, name: str | None = None) -> AuthResult: ...
    def login(self, email: str, password: str) -> AuthResult: ...


def get_auth_provider() -> AuthProvider:
    backend = current_app.config.get("AUTH_BACKEND", "local")
    if backend == "supabase":
        from auth.supabase_provider import SupabaseAuthProvider

        return SupabaseAuthProvider()
    from auth.local_provider import LocalAuthProvider

    return LocalAuthProvider()
