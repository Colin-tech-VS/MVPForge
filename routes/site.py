from flask import Blueprint, abort, jsonify, render_template, send_from_directory
from sqlalchemy import func

from constants import PROJECT_STATUS_PUBLISHED, PROJECT_STATUS_SOLD
from extensions import db
from models.mvp import MvpImage, MvpProject

site_bp = Blueprint("site", __name__, url_prefix="/site")


def _published_mvps():
    return (
        MvpProject.query.filter_by(status="published")
        .order_by(MvpProject.created_at.desc())
        .all()
    )


def _category_counts():
    rows = (
        db.session.query(MvpProject.category, func.count(MvpProject.id))
        .filter_by(status="published")
        .group_by(MvpProject.category)
        .order_by(func.count(MvpProject.id).desc())
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


@site_bp.route("/")
def home():
    all_mvps = _published_mvps()
    return render_template(
        "site/home.html",
        showcase=all_mvps[:3],
        featured=all_mvps,
        categories=_category_counts()[:6],
        stats={
            "total": len(all_mvps),
            "online": sum(1 for m in all_mvps if m.is_online),
            "min_price": min((m.price for m in all_mvps), default=0),
        },
    )


@site_bp.route("/catalogue")
def catalogue():
    mvps = _published_mvps()
    categories = _category_counts()
    return render_template("site/catalogue.html", mvps=mvps, categories=categories)


@site_bp.route("/projet/<project_id>")
def project_detail(project_id):
    project = MvpProject.query.filter(
        MvpProject.id == project_id,
        MvpProject.status.in_([PROJECT_STATUS_PUBLISHED, PROJECT_STATUS_SOLD]),
    ).first()
    if not project:
        abort(404)

    from auth.local_provider import get_current_user
    from models.user import User

    current = get_current_user()
    db_user = User.query.get(current.id) if current else None
    is_owner = bool(db_user and db_user.id == project.user_id)
    user_purchased = bool(db_user and project.buyer_id == db_user.id)
    can_purchase = project.is_purchasable() and not is_owner

    gallery = project.images.order_by(MvpImage.sort_order).all()
    return render_template(
        "site/detail.html",
        project=project,
        gallery=gallery,
        analytics_metrics=project.analytics_metrics(),
        analytics_period=project.analytics_period_days or 30,
        is_owner=is_owner,
        user_purchased=user_purchased,
        can_purchase=can_purchase,
    )


@site_bp.route("/categories")
def categories():
    counts = _category_counts()
    mvps = _published_mvps()
    return render_template("site/categories.html", categories=counts, mvps=mvps)


@site_bp.route("/comment-ca-marche")
def how_it_works():
    return render_template("site/how_it_works.html")


@site_bp.route("/uploads/<project_id>/<filename>")
def serve_upload(project_id, filename):
    from pathlib import Path
    from flask import current_app, redirect

    from utils.supabase_storage import public_url, storage_enabled

    # Images présentes localement (seed, ou dev) : servies directement.
    folder = Path(current_app.instance_path) / "uploads" / project_id
    if folder.exists() and (folder / filename).exists():
        return send_from_directory(folder, filename)

    # Sinon (uploads utilisateurs en prod) : redirection vers Supabase Storage.
    if storage_enabled():
        return redirect(public_url(f"{project_id}/{filename}"), code=302)

    abort(404)


@site_bp.route("/api/mvps")
def api_mvps():
    mvps = _published_mvps()
    return jsonify(
        [
            {
                "id": m.id,
                "title": m.title,
                "tagline": m.tagline,
                "price": m.price,
                "category": m.category,
                "stack": m.stack_list,
                "color": m.color,
                "cover": (
                    f"/site/uploads/{m.id}/{m.cover_image.filename}"
                    if m.cover_image
                    else None
                ),
                "url": f"/site/projet/{m.id}",
            }
            for m in mvps
        ]
    )
