from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from auth.decorators import login_required
from auth.local_provider import get_current_user
from constants import PROJECT_STATUS_PUBLISHED, PROJECT_STATUS_SOLD
from extensions import db
from models.mvp import MvpProject
from models.purchase import MvpPurchase
from models.user import User
from utils.purchase_payment import fulfill_project_purchase, get_or_create_pending_purchase
from utils.stripe_checkout import (
    create_purchase_checkout_session,
    session_paid_for_purchase,
    stripe_enabled,
)

purchases_bp = Blueprint("purchases", __name__, url_prefix="/site")


def _get_db_user() -> User | None:
    user = get_current_user()
    if not user:
        return None
    return User.query.get(user.id)


@purchases_bp.route("/projet/<project_id>/acheter", methods=["POST"])
@login_required
def start_purchase(project_id):
    db_user = _get_db_user()
    project = MvpProject.query.filter_by(id=project_id, status=PROJECT_STATUS_PUBLISHED).first()
    if not project:
        flash("Ce projet n'est plus disponible à l'achat.", "error")
        return redirect(url_for("site.catalogue"))

    if project.user_id == db_user.id:
        flash("Vous ne pouvez pas acheter votre propre projet.", "error")
        return redirect(url_for("site.project_detail", project_id=project.id))

    purchase = get_or_create_pending_purchase(project, db_user.id)
    if not purchase:
        flash("Achat impossible pour ce projet.", "error")
        return redirect(url_for("site.project_detail", project_id=project.id))

    return redirect(url_for("purchases.purchase_checkout", purchase_id=purchase.id))


@purchases_bp.route("/achat/<purchase_id>", methods=["GET", "POST"])
@login_required
def purchase_checkout(purchase_id):
    db_user = _get_db_user()
    purchase = MvpPurchase.query.filter_by(id=purchase_id, buyer_id=db_user.id).first_or_404()
    project = purchase.project

    if purchase.is_paid():
        flash("Cet achat est déjà finalisé.", "info")
        return redirect(url_for("account.purchases"))

    if not project.is_purchasable():
        flash("Ce projet a été vendu entre-temps.", "error")
        return redirect(url_for("site.catalogue"))

    if request.method == "POST":
        action = request.form.get("action", "stripe")

        if action == "simulate" and current_app.debug and not stripe_enabled():
            fulfill_project_purchase(purchase)
            flash(
                f"Achat confirmé — « {project.title} » (paiement simulé · mode dev).",
                "success",
            )
            return redirect(url_for("account.purchases"))

        if not stripe_enabled():
            flash("Le paiement en ligne n'est pas encore configuré.", "error")
            return redirect(url_for("purchases.purchase_checkout", purchase_id=purchase.id))

        try:
            session = create_purchase_checkout_session(purchase, db_user.email)
            purchase.stripe_checkout_session_id = session["session_id"]
            db.session.commit()
            return redirect(session["url"])
        except Exception:
            flash("Impossible de démarrer le paiement. Réessayez plus tard.", "error")
            return redirect(url_for("purchases.purchase_checkout", purchase_id=purchase.id))

    return render_template(
        "site/purchase_checkout.html",
        purchase=purchase,
        project=project,
        stripe_enabled=stripe_enabled(),
        dev_simulate=current_app.debug and not stripe_enabled(),
    )


@purchases_bp.route("/achat/<purchase_id>/succes")
@login_required
def purchase_success(purchase_id):
    db_user = _get_db_user()
    purchase = MvpPurchase.query.filter_by(id=purchase_id, buyer_id=db_user.id).first_or_404()
    session_id = request.args.get("session_id", "").strip()

    if purchase.is_paid():
        flash("Votre achat est confirmé.", "success")
        return redirect(url_for("account.purchases"))

    if stripe_enabled():
        if not session_id or not session_paid_for_purchase(session_id, purchase.id):
            flash("Paiement non confirmé. Réessayez ou contactez le support.", "error")
            return redirect(url_for("purchases.purchase_checkout", purchase_id=purchase.id))
        fulfill_project_purchase(purchase, session_id=session_id)
    else:
        abort(404)

    flash(
        f"Paiement reçu — le vendeur vous contactera pour le transfert de « {purchase.project.title} ».",
        "success",
    )
    return redirect(url_for("account.purchases"))
