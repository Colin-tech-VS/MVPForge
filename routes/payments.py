from flask import Blueprint, current_app, jsonify, request

from extensions import db
from models.mvp import MvpProject
from models.purchase import MvpPurchase
from utils.listing_payment import fulfill_listing_payment
from utils.purchase_payment import fulfill_project_purchase
from utils.stripe_checkout import stripe_enabled

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    if not stripe_enabled():
        return jsonify({"error": "stripe disabled"}), 503

    import stripe

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature", "")
    secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    try:
        if secret:
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
        else:
            event = stripe.Event.construct_from(request.get_json(force=True), stripe.api_key)
    except Exception:
        return jsonify({"error": "invalid payload"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        meta = session.get("metadata") or {}
        kind = meta.get("mvpforge_kind")
        if session.get("payment_status") != "paid":
            return jsonify({"ok": True}), 200

        if kind == "listing_fee":
            project = MvpProject.query.get(meta.get("project_id"))
            if project:
                fulfill_listing_payment(project, session_id=session.get("id"))
        elif kind == "project_purchase":
            purchase = MvpPurchase.query.get(meta.get("purchase_id"))
            if purchase:
                fulfill_project_purchase(
                    purchase,
                    session_id=session.get("id"),
                    payment_intent=session.get("payment_intent"),
                )

    return jsonify({"ok": True}), 200
