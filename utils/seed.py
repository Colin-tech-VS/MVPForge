"""Projets catalogue Colin — upsert sans supprimer les annonces des autres vendeurs."""

import shutil
from datetime import date
from pathlib import Path

from flask import current_app

from constants import MVP_CARD_COLORS
from extensions import db
from models.mvp import MvpImage, MvpProject
from models.user import User
from utils.uploads import delete_project_images

COLIN_EMAIL = "coco.cayre@gmail.com"

SEED_PROJECTS = [
    {
        "title": "Artworks Digital",
        "images_dir": "artworks",
        "launch_date": date(2026, 1, 1),
        "data": {
            "title": "Artworks Digital",
            "tagline": "Plateforme française qui relie artistes, galeries et collectionneurs autour de l'œuvre originale",
            "description": (
                "Écosystème numérique complet pour l'art contemporain : portfolios artistes gratuits à vie, "
                "pages galeries, marketplace avec paiement Stripe Connect, matching curatoriale artistes ↔ galeries, "
                "wishlist collectionneurs, blog SEO, multilingue (FR/EN/JA/KO) et assistante IA Aria.\n\n"
                "Modèle économique : création gratuite, commissions à la vente uniquement (18 % artistes, 5 % galeries). "
                "Stack Flask/Python, PostgreSQL/Supabase en production, analytics intégré (real-time, géo, UTM, conversions). "
                "Design musée (noir & or), SEO schema.org, sitemaps, llms.txt.\n\n"
                "Traction mesurée sur 30 jours (analytics admin) : 101 079 pages vues, 20 724 visiteurs uniques, "
                "42 768 sessions, 111 112 vues profils cumulées, 2 113 soutiens. "
                "13 inscriptions portfolio et 14 comptes via formulaires sur la période."
            ),
            "price": 49_000,
            "category": "Marketplace",
            "stack": "Python, Flask, Jinja2, PostgreSQL, Supabase, Stripe Connect, Mistral IA, CSS",
            "is_online": True,
            "monthly_visitors": 20_724,
            "monthly_revenue": 0,
            "page_views": 101_079,
            "sessions_count": 42_768,
            "bounce_rate": 82.3,
            "avg_duration": "4m 33s",
            "profile_views": 111_112,
            "engagement_count": 2_113,
            "conversion_count": 13,
            "conversion_rate": 0.07,
            "analytics_period_days": 30,
            "site_url": "https://www.artworksdigital.fr",
            "github_url": None,
            "monetization": "Commission à la vente|Marketplace|Services",
            "traffic_source": (
                "Direct 19 484 · Referral 5 701 · Campagnes UTM 648 · Search 33 · Social 5 "
                "(30 j · visiteurs uniques). Top pages : accueil, portfolios artistes, /artistes, /galeries, marketplace."
            ),
            "strengths": (
                "Produit live depuis janvier 2026 avec trafic réel : 20k+ visiteurs/mois, 100k+ pages vues/mois. "
                "Écosystème 3 audiences (artistes, galeries, collectionneurs). Analytics admin complet (real-time, conversions, UTM). "
                "SEO muséal solide (sitemaps, schema.org). Multilingue natif. Gratuit à l'inscription."
            ),
            "weaknesses": (
                "Revenus encore faibles — modèle commission, masse critique marketplace à accélérer. "
                "Taux de rebond élevé (82 %) typique d'une plateforme découverte. "
                "Dépendance APIs IA et Stripe."
            ),
            "resale_reason": (
                "Recentrage stratégique du fondateur sur d'autres projets. "
                "Plateforme fonctionnelle, documentée, avec métriques réelles et prête à être opérée par un repreneur art/tech."
            ),
        },
    },
    {
        "title": "Veliora",
        "images_dir": "veliora",
        "launch_date": None,
        "color": MVP_CARD_COLORS[1],
        "data": {
            "title": "Veliora",
            "tagline": "CRM immobilier — score mandat, crawler multi-portails et radar d'appels prioritaires",
            "description": (
                "SaaS B2B pour agences immobilières : Veliora détecte les opportunités sur les portails, "
                "calcule un score mandat expliqué (0–100), compare au marché DVF et livre chaque matin "
                "une liste d'appels prioritaires.\n\n"
                "Inclus : crawler Playwright multi-portails, CRM mandats vente/location, comparatif DVF, "
                "vitrine marketing, abonnement Stripe (500 € HT/mois/agence prévu), PWA installable avec crawls "
                "en arrière-plan et notifications.\n\n"
                "État actuel : produit développé et déployable, pas encore lancé commercialement "
                "(pas de site public actif). Captures issues d'un environnement de démo. "
                "Déploiement Scalingo documenté (Procfile, SQLite/Supabase, Stripe)."
            ),
            "price": 18_000,
            "category": "Immobilier",
            "stack": "Python, Flask, Playwright, SQLite, Supabase, Stripe, PWA, Gunicorn",
            "is_online": False,
            "monthly_visitors": None,
            "monthly_revenue": None,
            "site_url": None,
            "github_url": None,
            "monetization": "Abonnement|Services",
            "traffic_source": "Pas encore en ligne — go-to-market à définir (SEO, démos agences, réseau immobilier).",
            "strengths": (
                "Produit B2B ciblé avec pricing défini (500 €/mois/agence). Score mandat transparent (règles métier). "
                "Crawler multi-portails différenciant. PWA + crawls serveur. Produit et déploiement prêts — "
                "idéal pour un repreneur qui lance la commercialisation."
            ),
            "weaknesses": (
                "Pas encore lancé : zéro traction utilisateurs à ce jour. "
                "CRM incomplet (sync Hektor, signature électronique, matching acheteurs). "
                "Dépendance Playwright pour la veille portails."
            ),
            "resale_reason": (
                "Vente du produit et de la marque par le fondateur — recentrage sur d'autres projets. "
                "MVP technique abouti, à mettre en ligne et commercialiser par le repreneur."
            ),
        },
    },
    {
        "title": "Inside Vietnam Travel",
        "images_dir": "ivt",
        "launch_date": date(2025, 6, 8),
        "color": MVP_CARD_COLORS[2],
        "data": {
            "title": "Inside Vietnam Travel",
            "tagline": "Guide voyage Vietnam SEO — contenu éditorial, affiliés et rédaction IA (Groq / Mistral)",
            "description": (
                "Site de guide voyage Vietnam indépendant (pas une agence) : guides, itinéraires, blog "
                "et recommandations affiliées. Stack Flask, contenu SEO, admin complet.\n\n"
                "Fonctionnalités : assistant voyage Mai (IA), rédaction assistée Groq ou Mistral (switch admin), "
                "analytics temps réel (barres minute par minute, géo, UTM, SEO, trafic IA/LLM), clics affiliés, "
                "profils visiteurs cookie, newsletter, migration Supabase (PostgreSQL), déploiement Scalingo/Gunicorn.\n\n"
                "Traction mesurée sur 30 jours (analytics admin, juil. 2026) : 7 257 visiteurs uniques, "
                "181 visiteurs UTM réseaux sociaux, 726 utilisateurs Mai uniques (≈ 10 % du trafic), "
                "249 messages chat, 747 profils personnalisation. Trafic international fort (PK, SY, IN, IQ, FR…)."
            ),
            "price": 9_500,
            "category": "Voyage & Tourisme",
            "stack": "Python, Flask, Groq, Mistral IA, PostgreSQL, Supabase, Gunicorn",
            "is_online": True,
            "monthly_visitors": 7_257,
            "monthly_revenue": None,
            "profile_views": 747,
            "engagement_count": 249,
            "conversion_count": 139,
            "conversion_rate": 1.9,
            "analytics_period_days": 30,
            "analytics_extra": None,
            "site_url": "https://insidevietnamtravel.com",
            "github_url": None,
            "monetization": "Affiliation|Produits digitaux",
            "traffic_source": (
                "Direct 6 528 (90 %) · UTM réseaux sociaux 181 · SEO min. 10 · trafic IA 11 · 30 j. "
                "Top pays : Pakistan 1 507, Syrie 920, Inde 594, France 205. "
                "Mai AI : 726 utilisateurs uniques, 139 ont envoyé un message."
            ),
            "strengths": (
                "Site live avec 7 257 visiteurs uniques / 30 j. Assistant Mai IA intégré avec forte adoption "
                "(10 % des visiteurs). Niche travel claire, stack documentée Scalingo + Supabase. "
                "Contenu duplicable sur d'autres destinations."
            ),
            "weaknesses": (
                "Revenus affiliation à consolider. Un seul marché géographique pour l'instant. "
                "Dépendance APIs IA pour la production de contenu."
            ),
            "resale_reason": (
                "Cession du site par le fondateur — focus sur d'autres projets. "
                "Projet autonome, peu de maintenance si le contenu est externalisé."
            ),
        },
    },
]


def _get_colin_user() -> User:
    user = User.query.filter_by(email=COLIN_EMAIL).first()
    if user:
        if not user.name:
            user.name = "Colin"
        return user

    user = User(email=COLIN_EMAIL, name="Colin", auth_provider="local")
    user.set_password("changeme-colin-seed")
    db.session.add(user)
    db.session.flush()
    return user


def _seed_images(project_id: str, images_dir: str | None) -> None:
    if not images_dir:
        return

    seed_dir = Path(current_app.root_path) / "static" / "seed" / images_dir
    if not seed_dir.exists():
        return

    upload_root = Path(current_app.instance_path) / "uploads" / project_id
    upload_root.mkdir(parents=True, exist_ok=True)

    for image in MvpImage.query.filter_by(project_id=project_id).all():
        db.session.delete(image)

    for existing in upload_root.iterdir():
        if existing.is_file():
            existing.unlink(missing_ok=True)

    for order, src in enumerate(sorted(seed_dir.glob("*"))):
        if not src.is_file() or src.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            continue
        filename = src.name
        shutil.copy2(src, upload_root / filename)
        db.session.add(
            MvpImage(project_id=project_id, filename=filename, sort_order=order)
        )


def _upsert_project(seller: User, spec: dict, color_index: int) -> None:
    data = spec["data"]
    project = MvpProject.query.filter_by(title=spec["title"]).first()

    if project:
        for key, value in data.items():
            setattr(project, key, value)
        project.user_id = seller.id
        project.status = "published"
        project.launch_date = spec["launch_date"]
        if spec.get("color"):
            project.color = spec["color"]
    else:
        project = MvpProject(
            user_id=seller.id,
            color=spec.get("color") or MVP_CARD_COLORS[color_index % len(MVP_CARD_COLORS)],
            status="published",
            launch_date=spec["launch_date"],
            **data,
        )
        db.session.add(project)

    db.session.flush()
    if seller.email.strip().lower() == COLIN_EMAIL.lower():
        project.listing_fee_paid = True
        project.status = "published"
    if spec.get("images_dir"):
        _seed_images(project.id, spec["images_dir"])


def seed_catalog_projects() -> None:
    """Met à jour les projets Colin du catalogue sans toucher aux autres vendeurs."""
    seller = _get_colin_user()

    for index, spec in enumerate(SEED_PROJECTS):
        _upsert_project(seller, spec, index)

    legacy = User.query.filter_by(email="artworks@mvpforge.local").first()
    if legacy and legacy.id != seller.id:
        for project in MvpProject.query.filter_by(user_id=legacy.id).all():
            project.user_id = seller.id
        db.session.delete(legacy)

    db.session.commit()


# Alias rétrocompatibilité
def seed_artworks_digital() -> None:
    seed_catalog_projects()
