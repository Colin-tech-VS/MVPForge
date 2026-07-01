"""Frais de publication catalogue — 24 € par annonce (en ligne ou hors ligne)."""

from constants import (
    LISTING_FEE_CENTS,
    LISTING_FEE_EUR,
    LISTING_FEE_EXEMPT_EMAILS,
)
from models.user import User


def is_listing_fee_exempt(user: User | None) -> bool:
    if not user or not user.email:
        return False
    return user.email.strip().lower() in LISTING_FEE_EXEMPT_EMAILS


def listing_fee_required(user: User | None) -> bool:
    """True si le vendeur doit payer avant publication catalogue."""
    return not is_listing_fee_exempt(user)


def listing_fee_label() -> str:
    return f"{LISTING_FEE_EUR} €"
