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
PURCHASE_STATUS_PAID = "paid"
PURCHASE_STATUS_CANCELLED = "cancelled"
