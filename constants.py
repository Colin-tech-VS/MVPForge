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

# Questions fréquentes — affichées sur /site/faq et exposées en données
# structurées (schema.org FAQPage) pour le référencement (rich snippets Google).
FAQ_ITEMS = [
    (
        "Qu'est-ce qu'un MVP sur MVPForge ?",
        "Un MVP (Minimum Viable Product) est un produit numérique déjà "
        "construit : code source, design et parfois trafic et revenus réels. "
        "Sur MVPForge, vous reprenez un projet fonctionnel plutôt que de partir "
        "d'une page blanche.",
    ),
    (
        "Comment se passe l'achat d'un projet ?",
        "Vous payez en ligne via Stripe. Les fonds sont conservés en séquestre "
        "par la plateforme le temps de la passation (code, déploiement, secrets, "
        "domaines…). Dès que vous confirmez la bonne réception, les fonds sont "
        "reversés au vendeur.",
    ),
    (
        "Qu'est-ce que le séquestre (escrow) ?",
        "Le séquestre protège l'acheteur et le vendeur : votre paiement est "
        "bloqué par MVPForge et n'est libéré au vendeur qu'après confirmation "
        "que tous les éléments du projet vous ont bien été transférés.",
    ),
    (
        "Combien coûte la publication d'une annonce ?",
        "La mise en vente d'un MVP coûte 24 € (paiement unique via Stripe), "
        "que le projet soit en production ou hors ligne. Une commission de 10 % "
        "est ensuite prélevée sur le prix de vente lorsque le projet est vendu.",
    ),
    (
        "Que reçoit l'acheteur exactement ?",
        "Tout ce qui est nécessaire pour reprendre le projet : accès au code "
        "source, documentation de déploiement, clés et secrets, noms de domaine, "
        "comptes tiers, export des données et cession de propriété "
        "intellectuelle.",
    ),
    (
        "Puis-je vendre un projet qui n'est pas encore en ligne ?",
        "Oui. Vous pouvez vendre un MVP en production avec du trafic mesuré, "
        "comme un projet abouti mais pas encore lancé. La fiche indique "
        "clairement le statut du produit.",
    ),
    (
        "Les revenus et statistiques affichés sont-ils vérifiés ?",
        "Les métriques (visiteurs, revenus, conversions) sont déclarées par le "
        "vendeur sur la fiche du projet. Nous vous encourageons à demander des "
        "preuves (analytics, exports) avant de finaliser un achat.",
    ),
    (
        "Comment contacter MVPForge ?",
        "Vous pouvez nous écrire à tout moment via l'adresse indiquée sur la "
        "page des mentions légales pour toute question sur un projet, un "
        "paiement ou une passation.",
    ),
]
