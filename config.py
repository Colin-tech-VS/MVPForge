import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _normalize_database_url(url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # URL publique du site (sans slash final), ex: https://mvpforge.com
    # Utilisée pour les URLs canoniques, Open Graph et le sitemap.xml.
    # Si vide, on retombe sur l'origine de la requête (request.url_root).
    SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")
    # Identité de la plateforme (SEO + pages légales).
    SITE_NAME = os.environ.get("SITE_NAME", "MVPForge")
    SITE_TAGLINE = os.environ.get(
        "SITE_TAGLINE",
        "La marketplace pour acheter et vendre des projets MVP prêts à lancer.",
    )
    # Coordonnées légales (mentions légales, CGV, RGPD…).
    LEGAL_ENTITY = os.environ.get("LEGAL_ENTITY", "MVPForge")
    LEGAL_EMAIL = os.environ.get("LEGAL_EMAIL", "contact@mvpforge.com")

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL")
    ) or f"sqlite:///{BASE_DIR / 'instance' / 'mvpforge.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 105 * 1024 * 1024  # ~20 images × 5 Mo

    # Catalogue Colin (seed) au démarrage — désactiver en prod si besoin : SEED_CATALOG=0
    SEED_CATALOG = os.environ.get("SEED_CATALOG", "1") == "1"

    # "local" = SQLite | "supabase" = Supabase Auth
    AUTH_BACKEND = os.environ.get("AUTH_BACKEND", "local")

    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

    # Supabase Storage (persistance des images uploadées).
    # Actif dès que SUPABASE_URL + SUPABASE_SERVICE_KEY sont définis.
    # Sinon, fallback disque local (instance/uploads/, éphémère sur Scalingo).
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
    SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "mvp-images")

    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    # E-mails transactionnels (SMTP). Inactif tant que non configuré.
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    EMAIL_FROM = os.environ.get("EMAIL_FROM", "")

    # Clé de chiffrement des données de passation (défaut : dérivée de SECRET_KEY).
    HANDOVER_KEY = os.environ.get("HANDOVER_KEY", "")
