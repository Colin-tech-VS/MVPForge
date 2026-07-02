from flask import Blueprint, Response, current_app, redirect, request, url_for

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def root():
    return redirect(url_for("site.home"))


def _site_url() -> str:
    return (current_app.config.get("SITE_URL") or request.url_root).rstrip("/")


@core_bp.route("/robots.txt")
def robots_txt():
    base = _site_url()
    lines = [
        "User-agent: *",
        "Allow: /",
        # Espaces privés / transactionnels : inutiles pour l'indexation.
        "Disallow: /account/",
        "Disallow: /admin/",
        "Disallow: /auth/",
        "Disallow: /site/api/",
        "",
        f"Sitemap: {base}/sitemap.xml",
        "",
    ]
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
