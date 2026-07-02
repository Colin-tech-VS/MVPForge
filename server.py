import os
from pathlib import Path

from flask import Flask, render_template

from config import Config
from extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    import models  # noqa: F401

    from routes.account import account_bp
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.core import core_bp
    from routes.legal import legal_bp
    from routes.payments import payments_bp
    from routes.purchases import purchases_bp
    from routes.site import site_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(site_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payments_bp)

    with app.app_context():
        from utils.database import upgrade_database

        upgrade_database()
        if app.config.get("SEED_CATALOG", True):
            from utils.seed import seed_catalog_projects

            seed_catalog_projects()

    @app.context_processor
    def inject_user():
        from auth.local_provider import get_current_user

        return {"current_user": get_current_user()}

    @app.context_processor
    def inject_seo():
        from flask import request

        base = (app.config.get("SITE_URL") or request.url_root).rstrip("/")
        return {
            "site_url": base,
            "canonical_url": base + request.path,
            "site_name": app.config.get("SITE_NAME", "MVPForge"),
            "site_tagline": app.config.get("SITE_TAGLINE", ""),
            "legal_entity": app.config.get("LEGAL_ENTITY", "MVPForge"),
            "legal_email": app.config.get("LEGAL_EMAIL", ""),
        }

    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Pages d'erreur propres + garde-fou contre les 500 en cascade.

    Une transaction laissée en échec (ex. coupure DB, timeout Stripe/Supabase)
    met la session SQLAlchemy dans un état "PendingRollback" : sans rollback,
    toutes les requêtes suivantes servies par le même worker gunicorn
    renverraient un 500 — d'où des 500 "intermittents". On annule donc la
    transaction avant de rendre la page d'erreur.
    """

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        from werkzeug.exceptions import HTTPException

        # Les erreurs HTTP explicites (404, 403…) gardent leur comportement.
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("Unhandled exception: %s", error)
        db.session.rollback()
        return render_template("errors/500.html"), 500


app = create_app()

if __name__ == "__main__":
    app.run(
        debug=True,
        port=int(os.environ.get("PORT", 5000)),
        exclude_patterns=["*_artworks_ref*", "*/_artworks_ref/*", "*/tools/*"],
    )
