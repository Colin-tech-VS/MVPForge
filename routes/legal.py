from datetime import date

from flask import Blueprint, render_template

legal_bp = Blueprint("legal", __name__)

# Date de dernière mise à jour affichée en pied des documents légaux.
LAST_UPDATED = date(2026, 7, 1)


def _render(template: str, title: str):
    return render_template(
        template,
        page_title=title,
        last_updated=LAST_UPDATED.strftime("%d/%m/%Y"),
    )


@legal_bp.route("/mentions-legales")
def mentions_legales():
    return _render("legal/mentions_legales.html", "Mentions légales")


@legal_bp.route("/cgv")
def cgv():
    return _render("legal/cgv.html", "Conditions générales de vente")


@legal_bp.route("/cgu")
def cgu():
    return _render("legal/cgu.html", "Conditions générales d'utilisation")


@legal_bp.route("/confidentialite")
def confidentialite():
    return _render("legal/confidentialite.html", "Politique de confidentialité")


@legal_bp.route("/cookies")
def cookies():
    return _render("legal/cookies.html", "Politique de cookies")
