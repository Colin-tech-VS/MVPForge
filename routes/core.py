from flask import Blueprint, Response, current_app, redirect, request, url_for

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def root():
    return redirect(url_for("site.home"))


def _site_url() -> str:
    return (current_app.config.get("SITE_URL") or request.url_root).rstrip("/")


@core_bp.route("/llms.txt")
def llms_txt():
    """Fiche de présentation lisible par les LLM (standard llmstxt.org).

    Décrit MVPForge en Markdown pour que les assistants IA (Claude, ChatGPT,
    Copilot, Gemini, Mistral, Perplexity…) comprennent, résument et classent
    correctement la plateforme, avec des liens vers les pages clés.
    """
    from models.mvp import MvpProject

    base = _site_url()
    name = current_app.config.get("SITE_NAME", "MVPForge")
    tagline = current_app.config.get("SITE_TAGLINE", "")

    lines = [
        f"# {name}",
        "",
        f"> {tagline}",
        "",
        f"{name} est une marketplace francophone où des fondateurs achètent et "
        "vendent des projets MVP (Minimum Viable Product) déjà construits : code "
        "source, design, et parfois trafic et revenus réels. L'acheteur reprend "
        "un produit fonctionnel plutôt que de partir d'une page blanche.",
        "",
        "## Fonctionnement",
        "",
        "- Publication d'une annonce : 24 € (paiement unique via Stripe), projet "
        "en ligne ou hors ligne.",
        "- Commission plateforme : 10 % du prix de vente, prélevée à la vente.",
        "- Paiement sécurisé par séquestre (escrow) : les fonds sont bloqués "
        "jusqu'à ce que l'acheteur confirme la bonne réception de la passation "
        "(code, déploiement, secrets, domaines, comptes tiers, données, cession "
        "de propriété intellectuelle).",
        "",
        "## Pages principales",
        "",
        f"- [Accueil]({base}{url_for('site.home')}): présentation de la plateforme.",
        f"- [Catalogue]({base}{url_for('site.catalogue')}): tous les MVP en vente.",
        f"- [Catégories]({base}{url_for('site.categories')}): projets par secteur.",
        f"- [Comment ça marche]({base}{url_for('site.how_it_works')}): le parcours "
        "d'achat et de vente.",
        f"- [FAQ]({base}{url_for('site.faq')}): questions fréquentes.",
        "",
    ]

    projects = (
        MvpProject.query.filter_by(status="published")
        .order_by(MvpProject.created_at.desc())
        .limit(50)
        .all()
    )
    if projects:
        lines.append("## Projets MVP en vente")
        lines.append("")
        for p in projects:
            url = base + url_for("site.project_detail", project_id=p.id)
            desc = (p.tagline or "").strip()
            price = f"{p.price} €" if p.price else "prix sur demande"
            suffix = f" — {desc}" if desc else ""
            lines.append(f"- [{p.title} · {p.category} · {price}]({url}){suffix}")
        lines.append("")

    lines += [
        "## Ressources",
        "",
        f"- [Plan du site (XML)]({base}/sitemap.xml): index complet des URL.",
        f"- [Mentions légales]({base}{url_for('legal.mentions_legales')}): éditeur "
        "et contact.",
        f"- [CGV]({base}{url_for('legal.cgv')}): conditions de vente.",
        f"- [Confidentialité]({base}{url_for('legal.confidentialite')}): données "
        "personnelles (RGPD).",
        "",
    ]

    return Response("\n".join(lines), mimetype="text/plain; charset=utf-8")


@core_bp.route("/robots.txt")
def robots_txt():
    base = _site_url()
    # Espaces privés / transactionnels : inutiles pour l'indexation.
    disallow = [
        "Disallow: /compte/",
        "Disallow: /admin/",
        "Disallow: /auth/",
        "Disallow: /site/api/",
        "Disallow: /site/achat/",
    ]

    lines = ["User-agent: *", "Allow: /", *disallow, ""]

    # Assistants IA / moteurs génératifs : on autorise explicitement le crawl
    # des pages publiques pour que MVPForge soit connu, cité et bien classé
    # (ChatGPT, Claude, Copilot, Perplexity, Gemini, Mistral…).
    ai_agents = [
        "GPTBot",
        "OAI-SearchBot",
        "ChatGPT-User",
        "ClaudeBot",
        "Claude-Web",
        "anthropic-ai",
        "PerplexityBot",
        "Perplexity-User",
        "Google-Extended",
        "Applebot-Extended",
        "CCBot",
        "Amazonbot",
        "cohere-ai",
        "MistralAI-User",
        "Meta-ExternalAgent",
        "Bytespider",
        "YouBot",
        "DuckAssistBot",
    ]
    for agent in ai_agents:
        lines += [f"User-agent: {agent}", "Allow: /", *disallow, ""]

    lines += [f"Sitemap: {base}/sitemap.xml", f"LLMs: {base}/llms.txt", ""]
    return Response("\n".join(lines), mimetype="text/plain")


@core_bp.route("/sitemap.xml")
def sitemap_xml():
    from models.mvp import MvpProject

    base = _site_url()

    # Pages statiques principales, avec priorité et fréquence de crawl.
    static_pages = [
        ("site.home", 1.0, "daily"),
        ("site.catalogue", 0.9, "daily"),
        ("site.categories", 0.7, "weekly"),
        ("site.how_it_works", 0.6, "monthly"),
        ("site.faq", 0.6, "monthly"),
        ("legal.mentions_legales", 0.2, "yearly"),
        ("legal.cgv", 0.2, "yearly"),
        ("legal.cgu", 0.2, "yearly"),
        ("legal.confidentialite", 0.2, "yearly"),
        ("legal.cookies", 0.2, "yearly"),
    ]

    urls = []
    for endpoint, priority, changefreq in static_pages:
        urls.append(
            {
                "loc": base + url_for(endpoint),
                "priority": priority,
                "changefreq": changefreq,
            }
        )

    # Une entrée par projet visible (publié ou vendu) — cœur du référencement.
    projects = (
        MvpProject.query.filter(MvpProject.status.in_(["published", "sold"]))
        .order_by(MvpProject.updated_at.desc())
        .all()
    )
    for project in projects:
        lastmod = None
        if project.updated_at:
            lastmod = project.updated_at.strftime("%Y-%m-%d")
        urls.append(
            {
                "loc": base + url_for("site.project_detail", project_id=project.id),
                "priority": 0.8,
                "changefreq": "weekly",
                "lastmod": lastmod,
            }
        )

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in urls:
        xml.append("  <url>")
        xml.append(f"    <loc>{u['loc']}</loc>")
        if u.get("lastmod"):
            xml.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        xml.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml.append(f"    <priority>{u['priority']}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")

    return Response("\n".join(xml), mimetype="application/xml")
