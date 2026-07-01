import random
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.datastructures import ImmutableMultiDict

from auth.decorators import login_required
from auth.local_provider import (
    get_current_user,
    sync_session_user,
    validate_email,
    validate_password,
)
from constants import (
    LISTING_FEE_CENTS,
    LISTING_FEE_EUR,
    MAX_MVP_IMAGES,
    MIN_MVP_IMAGES,
    MONETIZATION_TYPES,
    MVP_CARD_COLORS,
    MVP_CATEGORIES,
    PROJECT_STATUS_PENDING_PAYMENT,
    PROJECT_STATUS_PUBLISHED,
)
from extensions import db
from models.mvp import MvpImage, MvpProject
from models.user import User
from utils.listing_fee import is_listing_fee_exempt, listing_fee_label, listing_fee_required
from utils.listing_payment import fulfill_listing_payment
from utils.stripe_checkout import (
    create_listing_checkout_session,
    session_paid_for_listing,
    stripe_enabled,
)
from utils.uploads import delete_project_images, save_project_images

account_bp = Blueprint("account", __name__, url_prefix="/compte")


def _get_db_user():
    user = get_current_user()
    if not user:
        return None
    return User.query.get(user.id)


def _valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _optional_int(form, key: str, errors: list[str], label: str, minimum: int = 0):
    raw = form.get(key, "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
        if value < minimum:
            raise ValueError
        return value
    except ValueError:
        errors.append(f"{label} : indiquez un nombre entier valide.")
        return None


def _optional_float(form, key: str, errors: list[str], label: str, maximum: float = 100.0):
    raw = form.get(key, "").strip().replace(",", ".")
    if not raw:
        return None
    try:
        value = float(raw)
        if value < 0 or value > maximum:
            raise ValueError
        return value
    except ValueError:
        errors.append(f"{label} : indiquez un pourcentage entre 0 et {maximum:g}.")
        return None


def _clear_analytics_fields(data: dict) -> None:
    data["page_views"] = None
    data["sessions_count"] = None
    data["bounce_rate"] = None
    data["avg_duration"] = None
    data["profile_views"] = None
    data["engagement_count"] = None
    data["conversion_count"] = None
    data["conversion_rate"] = None
    data["analytics_period_days"] = None


def _parse_analytics_fields(form, errors: list[str], data: dict) -> None:
    data["page_views"] = _optional_int(form, "page_views", errors, "Pages vues")
    data["sessions_count"] = _optional_int(form, "sessions_count", errors, "Sessions")
    data["profile_views"] = _optional_int(form, "profile_views", errors, "Vues profils")
    data["engagement_count"] = _optional_int(
        form, "engagement_count", errors, "Engagements"
    )
    data["conversion_count"] = _optional_int(
        form, "conversion_count", errors, "Conversions"
    )
    data["bounce_rate"] = _optional_float(form, "bounce_rate", errors, "Taux de rebond")
    data["conversion_rate"] = _optional_float(
        form, "conversion_rate", errors, "Taux de conversion"
    )

    avg_duration = form.get("avg_duration", "").strip()
    data["avg_duration"] = avg_duration[:20] if avg_duration else None

    period_raw = form.get("analytics_period_days", "").strip()
    if not period_raw:
        data["analytics_period_days"] = None
    elif period_raw in {"7", "30", "90"}:
        data["analytics_period_days"] = int(period_raw)
    else:
        errors.append("Période analytics : choisissez 7, 30 ou 90 jours.")


def _form_context(form=None, db_user=None):
    form = form or {}
    monetization_selected = form.getlist("monetization") if hasattr(form, "getlist") else []
    exempt = is_listing_fee_exempt(db_user) if db_user else False
    return {
        "categories": MVP_CATEGORIES,
        "monetization_types": MONETIZATION_TYPES,
        "form": form,
        "monetization_selected": monetization_selected,
        "max_images": MAX_MVP_IMAGES,
        "min_images": MIN_MVP_IMAGES,
        "listing_fee_eur": LISTING_FEE_EUR,
        "listing_fee_exempt": exempt,
        "stripe_enabled": stripe_enabled(),
    }


def _validate_and_parse(form: ImmutableMultiDict, files) -> tuple[dict | None, list[str]]:
    errors = []
    data = {}

    data["title"] = form.get("title", "").strip()
    data["tagline"] = form.get("tagline", "").strip()
    data["description"] = form.get("description", "").strip()
    data["stack"] = form.get("stack", "").strip()
    data["traffic_source"] = form.get("traffic_source", "").strip()
    data["strengths"] = form.get("strengths", "").strip()
    data["weaknesses"] = form.get("weaknesses", "").strip()
    data["resale_reason"] = form.get("resale_reason", "").strip()
    data["github_url"] = None
    data["is_online"] = form.get("is_online") == "1"

    category = form.get("category", "").strip()
    category_other = form.get("category_other", "").strip()
    if category == "Autre":
        if len(category_other) < 2:
            errors.append("Précisez votre catégorie dans le champ « Autre ».")
        data["category"] = category_other
    elif category in MVP_CATEGORIES:
        data["category"] = category
    else:
        errors.append("Sélectionnez une catégorie valide.")

    monetization = form.getlist("monetization")
    valid_mono = [m for m in monetization if m in MONETIZATION_TYPES]
    if not valid_mono:
        errors.append("Sélectionnez au moins un type de monétisation.")
    data["monetization"] = "|".join(valid_mono)

    if len(data["title"]) < 3:
        errors.append("Le titre doit contenir au moins 3 caractères.")
    if len(data["tagline"]) < 10:
        errors.append("La description courte doit contenir au moins 10 caractères.")
    if len(data["description"]) < 30:
        errors.append("La description détaillée doit contenir au moins 30 caractères.")
    if len(data["strengths"]) < 10:
        errors.append("Décrivez au moins un point fort (10 caractères min.).")
    if len(data["weaknesses"]) < 10:
        errors.append("Décrivez au moins un point faible (10 caractères min.).")
    if len(data["resale_reason"]) < 10:
        errors.append("Indiquez la raison de la revente (10 caractères min.).")
    if len(data["traffic_source"]) < 5:
        errors.append("Décrivez la source de trafic.")

    try:
        price = int(form.get("price", "").strip())
        if price < 1:
            raise ValueError
        data["price"] = price
    except ValueError:
        errors.append("Indiquez un prix valide (nombre entier en euros).")

    if not data["stack"]:
        errors.append("Indiquez au moins une technologie dans la stack.")

    if data["is_online"]:
        data["site_url"] = form.get("site_url", "").strip()
        if not _valid_url(data["site_url"]):
            errors.append("L'URL du site est invalide.")
        try:
            data["monthly_visitors"] = int(form.get("monthly_visitors", "").strip())
            if data["monthly_visitors"] < 0:
                raise ValueError
        except ValueError:
            errors.append("Indiquez un nombre de visiteurs mensuels valide.")
        try:
            data["monthly_revenue"] = int(form.get("monthly_revenue", "").strip())
            if data["monthly_revenue"] < 0:
                raise ValueError
        except ValueError:
            errors.append("Indiquez des revenus mensuels valides (en euros).")
        launch_raw = form.get("launch_date", "").strip()
        try:
            data["launch_date"] = datetime.strptime(launch_raw, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Indiquez une date de mise en ligne valide.")
        _parse_analytics_fields(form, errors, data)
    else:
        data["site_url"] = None
        data["monthly_visitors"] = None
        data["monthly_revenue"] = None
        data["launch_date"] = None
        _clear_analytics_fields(data)

    uploaded = [f for f in files.getlist("images") if f and f.filename]
    if len(uploaded) < MIN_MVP_IMAGES:
        errors.append(f"Ajoutez au moins {MIN_MVP_IMAGES} image.")
    if len(uploaded) > MAX_MVP_IMAGES:
        errors.append(f"Maximum {MAX_MVP_IMAGES} images autorisées.")
    data["uploaded_files"] = uploaded

    return (data if not errors else None), errors


def _create_project_from_data(db_user: User, data: dict) -> MvpProject:
    needs_fee = listing_fee_required(db_user)
    fee_exempt = is_listing_fee_exempt(db_user)

    project = MvpProject(
        user_id=db_user.id,
        title=data["title"],
        tagline=data["tagline"],
        description=data["description"],
        category=data["category"],
        stack=data["stack"],
        price=data["price"],
        color=random.choice(MVP_CARD_COLORS),
        status=PROJECT_STATUS_PENDING_PAYMENT if needs_fee else PROJECT_STATUS_PUBLISHED,
        is_online=data["is_online"],
        monthly_visitors=data["monthly_visitors"],
        monthly_revenue=data["monthly_revenue"],
        launch_date=data["launch_date"],
        site_url=data["site_url"],
        github_url=data["github_url"] or None,
        monetization=data["monetization"],
        traffic_source=data["traffic_source"],
        strengths=data["strengths"],
        weaknesses=data["weaknesses"],
        resale_reason=data["resale_reason"],
        page_views=data["page_views"],
        sessions_count=data["sessions_count"],
        bounce_rate=data["bounce_rate"],
        avg_duration=data["avg_duration"],
        profile_views=data["profile_views"],
        engagement_count=data["engagement_count"],
        conversion_count=data["conversion_count"],
        conversion_rate=data["conversion_rate"],
        analytics_period_days=data["analytics_period_days"],
        listing_fee_paid=fee_exempt,
        listing_fee_amount_cents=LISTING_FEE_CENTS if not fee_exempt else None,
    )
    if project.listing_fee_paid:
        project.listing_fee_paid_at = datetime.now(timezone.utc)
    return project


def _save_new_project_images(project: MvpProject, uploaded_files: list) -> bool:
    saved, img_errors = save_project_images(project.id, uploaded_files)
    if img_errors:
        for err in img_errors:
            flash(err, "error")
    if not saved:
        db.session.rollback()
        delete_project_images(project.id)
        flash("Au moins une image valide est requise.", "error")
        return False
    for filename, order in saved:
        db.session.add(
            MvpImage(project_id=project.id, filename=filename, sort_order=order)
        )
    return True


@account_bp.route("/")
@login_required
def dashboard():
    db_user = _get_db_user()
    projects = (
        MvpProject.query.filter_by(user_id=db_user.id)
        .order_by(MvpProject.created_at.desc())
        .all()
    )
    catalogue_count = sum(1 for p in projects if p.is_catalogue_visible())
    pending_count = sum(1 for p in projects if p.status == PROJECT_STATUS_PENDING_PAYMENT)
    return render_template(
        "account/dashboard.html",
        projects=projects,
        db_user=db_user,
        account_section="projects",
        listing_fee_eur=LISTING_FEE_EUR,
        catalogue_count=catalogue_count,
        pending_count=pending_count,
    )


@account_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profile():
    db_user = _get_db_user()

    if request.method == "POST":
        errors = []
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        company = request.form.get("company", "").strip()
        website = request.form.get("website", "").strip()
        location = request.form.get("location", "").strip()
        bio = request.form.get("bio", "").strip()
        current_password = request.form.get("current_password", "")

        if not name or len(name) < 2:
            errors.append("Indiquez votre nom (2 caractères minimum).")
        if not validate_email(email):
            errors.append("Adresse e-mail invalide.")
        if email != db_user.email:
            if db_user.auth_provider != "local":
                errors.append("La modification d'e-mail n'est pas disponible avec ce mode de connexion.")
            elif not db_user.check_password(current_password):
                errors.append("Mot de passe actuel incorrect pour changer l'e-mail.")
            elif User.query.filter(User.email == email, User.id != db_user.id).first():
                errors.append("Un autre compte utilise déjà cet e-mail.")

        if website and not _valid_url(website):
            errors.append("L'URL du site web n'est pas valide.")

        if len(bio) > 500:
            errors.append("La bio ne peut pas dépasser 500 caractères.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "account/profile.html",
                db_user=db_user,
                account_section="profile",
                form=request.form,
            )

        db_user.name = name
        db_user.email = email
        db_user.phone = phone or None
        db_user.company = company or None
        db_user.website = website or None
        db_user.location = location or None
        db_user.bio = bio or None
        db.session.commit()
        sync_session_user(db_user)
        flash("Profil mis à jour.", "success")
        return redirect(url_for("account.profile"))

    return render_template(
        "account/profile.html",
        db_user=db_user,
        account_section="profile",
        form=None,
    )


@account_bp.route("/securite", methods=["GET", "POST"])
@login_required
def security():
    db_user = _get_db_user()

    if request.method == "POST":
        if db_user.auth_provider != "local":
            flash("Le mot de passe se gère via votre fournisseur de connexion.", "error")
            return redirect(url_for("account.security"))

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not db_user.check_password(current_password):
            flash("Mot de passe actuel incorrect.", "error")
            return render_template(
                "account/security.html",
                db_user=db_user,
                account_section="security",
            )

        pwd_error = validate_password(new_password)
        if pwd_error:
            flash(pwd_error, "error")
            return render_template(
                "account/security.html",
                db_user=db_user,
                account_section="security",
            )

        if new_password != confirm_password:
            flash("Les nouveaux mots de passe ne correspondent pas.", "error")
            return render_template(
                "account/security.html",
                db_user=db_user,
                account_section="security",
            )

        db_user.set_password(new_password)
        db.session.commit()
        flash("Mot de passe mis à jour.", "success")
        return redirect(url_for("account.security"))

    return render_template(
        "account/security.html",
        db_user=db_user,
        account_section="security",
    )


@account_bp.route("/achats")
@login_required
def purchases():
    db_user = _get_db_user()
    purchases_list = (
        MvpPurchase.query.filter_by(buyer_id=db_user.id)
        .order_by(MvpPurchase.created_at.desc())
        .all()
    )
    return render_template(
        "account/purchases.html",
        db_user=db_user,
        purchases=purchases_list,
        account_section="purchases",
    )


@account_bp.route("/projet/nouveau", methods=["GET", "POST"])
@login_required
def create_project():
    db_user = _get_db_user()

    if request.method == "POST":
        data, errors = _validate_and_parse(request.form, request.files)
        if errors:
            for err in errors:
                flash(err, "error")
            ctx = _form_context(request.form, db_user)
            return render_template("account/create.html", **ctx)

        project = _create_project_from_data(db_user, data)
        db.session.add(project)
        db.session.flush()

        if not _save_new_project_images(project, data["uploaded_files"]):
            ctx = _form_context(request.form, db_user)
            return render_template("account/create.html", **ctx)

        db.session.commit()

        if project.status == PROJECT_STATUS_PENDING_PAYMENT:
            flash(
                f"« {project.title} » est enregistré. Payez {listing_fee_label()} "
                "pour le publier sur le catalogue.",
                "info",
            )
            return redirect(url_for("account.listing_payment", project_id=project.id))

        flash(f"« {project.title} » est publié sur le catalogue.", "success")
        return redirect(url_for("account.dashboard"))

    return render_template("account/create.html", **_form_context(db_user=db_user))


@account_bp.route("/projet/<project_id>/paiement", methods=["GET", "POST"])
@login_required
def listing_payment(project_id):
    db_user = _get_db_user()
    project = MvpProject.query.filter_by(id=project_id, user_id=db_user.id).first_or_404()

    if project.status != PROJECT_STATUS_PENDING_PAYMENT:
        if project.is_catalogue_visible():
            flash("Ce projet est déjà publié sur le catalogue.", "info")
        return redirect(url_for("account.dashboard"))

    if request.method == "POST":
        action = request.form.get("action", "stripe")

        if action == "simulate" and current_app.debug and not stripe_enabled():
            fulfill_listing_payment(project)
            flash(f"« {project.title} » est publié (paiement simulé — mode dev).", "success")
            return redirect(url_for("account.dashboard"))

        if not stripe_enabled():
            flash(
                "Le paiement en ligne n'est pas encore configuré. "
                "Contactez l'équipe MVPForge.",
                "error",
            )
            return redirect(url_for("account.listing_payment", project_id=project.id))

        try:
            session = create_listing_checkout_session(project, db_user.email)
            project.stripe_checkout_session_id = session["session_id"]
            db.session.commit()
            return redirect(session["url"])
        except Exception:
            flash("Impossible de démarrer le paiement Stripe. Réessayez plus tard.", "error")
            return redirect(url_for("account.listing_payment", project_id=project.id))

    return render_template(
        "account/listing_payment.html",
        project=project,
        listing_fee_eur=LISTING_FEE_EUR,
        stripe_enabled=stripe_enabled(),
        dev_simulate=current_app.debug and not stripe_enabled(),
    )


@account_bp.route("/projet/<project_id>/paiement/succes")
@login_required
def listing_payment_success(project_id):
    db_user = _get_db_user()
    project = MvpProject.query.filter_by(id=project_id, user_id=db_user.id).first_or_404()
    session_id = request.args.get("session_id", "").strip()

    if project.status == PROJECT_STATUS_PUBLISHED:
        flash(f"« {project.title} » est déjà publié.", "info")
        return redirect(url_for("account.dashboard"))

    if not session_id or not session_paid_for_listing(session_id, project.id):
        flash("Paiement non confirmé. Réessayez ou contactez le support.", "error")
        return redirect(url_for("account.listing_payment", project_id=project.id))

    fulfill_listing_payment(project, session_id=session_id)
    flash(f"Paiement reçu — « {project.title} » est en ligne sur le catalogue.", "success")
    return redirect(url_for("account.dashboard"))


@account_bp.route("/projet/<project_id>/supprimer", methods=["POST"])
@login_required
def delete_project(project_id):
    db_user = _get_db_user()
    project = MvpProject.query.filter_by(id=project_id, user_id=db_user.id).first_or_404()
    title = project.title
    delete_project_images(project.id)
    db.session.delete(project)
    db.session.commit()
    flash(f"« {title} » a été supprimé.", "info")
    return redirect(url_for("account.dashboard"))
