from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth.local_provider import get_current_user, login_user, logout_user
from auth.providers import get_auth_provider

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _store_tokens(tokens: dict | None) -> None:
    if not tokens:
        return
    session["supabase_access_token"] = tokens.get("access_token")
    session["supabase_refresh_token"] = tokens.get("refresh_token")


@auth_bp.route("/connexion", methods=["GET", "POST"])
def login():
    if get_current_user():
        return redirect(url_for("account.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        result = get_auth_provider().login(email, password)
        if result.success and result.user:
            login_user(result.user)
            session.permanent = remember
            _store_tokens(result.tokens)
            flash(f"Bienvenue, {result.user.name} !", "success")
            next_url = request.args.get("next") or url_for("account.dashboard")
            return redirect(next_url)

        flash(result.error or "Connexion impossible.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/inscription", methods=["GET", "POST"])
def register():
    if get_current_user():
        return redirect(url_for("account.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Les mots de passe ne correspondent pas.", "error")
            return render_template("auth/register.html")

        result = get_auth_provider().register(email, password, name)
        if result.success and result.user:
            login_user(result.user)
            _store_tokens(result.tokens)
            flash("Compte créé avec succès. Bienvenue sur MVPForge !", "success")
            return redirect(url_for("account.dashboard"))

        flash(result.error or "Inscription impossible.", "error")

    return render_template("auth/register.html")


@auth_bp.route("/deconnexion")
def logout():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("site.home"))
