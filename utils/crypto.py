"""Chiffrement symétrique pour les données sensibles de passation.

La clé Fernet est dérivée de SECRET_KEY (ou HANDOVER_KEY si défini) : aucun
secret supplémentaire à gérer, mais les données de passation (secrets, tokens)
sont chiffrées au repos en base.
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


def _fernet() -> Fernet:
    seed = current_app.config.get("HANDOVER_KEY") or current_app.config["SECRET_KEY"]
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt(plaintext: str | None) -> str | None:
    if not plaintext:
        return None
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(token: str | None) -> str:
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        # Clé changée ou donnée corrompue : on ne fait pas planter la page.
        return ""
