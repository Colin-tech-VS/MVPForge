MVP_CATEGORIES = [
    "SaaS B2B",
    "SaaS B2C",
    "E-commerce",
    "Marketplace",
    "Productivité",
    "Finance & Fintech",
    "Santé & Wellness",
    "Éducation & E-learning",
    "Social & Communauté",
    "IA & Automatisation",
    "DevTools",
    "Application mobile",
    "Extension navigateur",
    "No-code / Low-code",
    "Gaming",
    "Média & Contenu",
    "Immobilier",
    "RH & Recrutement",
    "LegalTech",
    "FoodTech",
    "Voyage & Tourisme",
    "IoT & Hardware",
    "Crypto & Web3",
    "Autre",
]

MONETIZATION_TYPES = [
    "Abonnement",
    "Affiliation",
    "Produits digitaux",
    "Produits physiques",
    "Publicité",
    "Services",
    "Vente de leads",
    "Vente de liens",
]

MVP_CARD_COLORS = [
    "#1A6B52",
    "#3B6B9A",
    "#6B4B8A",
    "#9A6B3B",
    "#3B8A6B",
    "#8A4B6B",
]

MAX_MVP_IMAGES = 20
MIN_MVP_IMAGES = 1
MAX_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Frais de publication catalogue (toute annonce, en ligne ou hors ligne)
LISTING_FEE_EUR = 24
LISTING_FEE_CENTS = 2400
LISTING_FEE_EXEMPT_EMAILS = frozenset({"coco.cayre@gmail.com"})

PROJECT_STATUS_PUBLISHED = "published"
PROJECT_STATUS_PENDING_PAYMENT = "pending_payment"
PROJECT_STATUS_SOLD = "sold"

PURCHASE_STATUS_PENDING = "pending"
PURCHASE_STATUS_PAID = "paid"          # payé — fonds détenus en séquestre par la plateforme
PURCHASE_STATUS_RELEASED = "released"  # passation confirmée — fonds reversés au vendeur
PURCHASE_STATUS_REFUNDED = "refunded"
PURCHASE_STATUS_CANCELLED = "cancelled"

# Commission plateforme prélevée sur chaque vente (le vendeur touche le reste).
PLATFORM_COMMISSION_PCT = 10

# Étapes de passation présentées à l'acheteur et au vendeur. La confirmation de
# réception par l'acheteur déclenche la libération du séquestre vers le vendeur.
HANDOVER_STEPS = [
    ("code", "Code source", "Accès au dépôt (transfert de propriété ou export)."),
    ("deploy", "Déploiement", "Runbook, dépendances, variables d'environnement."),
    ("secrets", "Secrets & accès", "Clés API, identifiants, comptes de service."),
    ("domains", "Domaines & DNS", "Noms de domaine et procédure de transfert."),
    ("accounts", "Comptes tiers", "Hébergeur, analytics, e-mailing, paiements."),
    ("data", "Données", "Export base de données (RGPD si base clients)."),
    ("legal", "Juridique", "Cession de propriété intellectuelle, absence de passif."),
]
