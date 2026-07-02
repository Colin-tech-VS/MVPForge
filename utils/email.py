"""E-mails transactionnels (SMTP).

Neutralisé (no-op, simple log) tant que SMTP_HOST + EMAIL_FROM ne sont pas
configurés. Aucune dépendance externe : smtplib de la stdlib.
"""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from flask import current_app, url_for


def email_enabled() -> bool:
    cfg = current_app.config
    return bool(cfg.get("SMTP_HOST") and cfg.get("EMAIL_FROM"))


def send_email(to: str, subject: str, body: str) -> bool:
    if not to:
        return False
    if not email_enabled():
        current_app.logger.info("E-mail (désactivé) → %s : %s", to, subject)
        return False

    cfg = current_app.config
    msg = EmailMessage()
    msg["From"] = cfg["EMAIL_FROM"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    host = cfg["SMTP_HOST"]
    port = int(cfg.get("SMTP_PORT", 587))
    user = cfg.get("SMTP_USER")
    password = cfg.get("SMTP_PASSWORD")

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
    except Exception:
        current_app.logger.exception("Échec envoi e-mail vers %s", to)
        return False
    return True


# ── Événements ─────────────────────────────────────────────────────────────

def notify_sale(purchase) -> None:
    """Prévient le vendeur qu'un de ses projets vient d'être vendu."""
    project = purchase.project
    seller = project.seller if project else None
    if not seller:
        return
    body = (
        f"Bonne nouvelle {seller.display_name()},\n\n"
        f"Votre projet « {project.title} » vient d'être vendu "
        f"({purchase.formatted_amount()} €).\n\n"
        f"Montant qui vous revient après commission : "
        f"{purchase.formatted_seller_amount()} €.\n\n"
        "Prochaine étape : l'acheteur accède à votre dossier de passation. "
        "Le paiement vous sera reversé dès qu'il aura confirmé la réception.\n\n"
        "— MVPForge"
    )
    send_email(seller.email, f"Vendu : {project.title}", body)


def notify_buyer_handover(purchase) -> None:
    """Envoie à l'acheteur le lien vers le dossier de passation."""
    buyer = purchase.buyer
    project = purchase.project
    if not buyer:
        return
    link = url_for("purchases.handover", purchase_id=purchase.id, _external=True)
    body = (
        f"Merci {buyer.display_name()},\n\n"
        f"Votre achat de « {project.title} » est confirmé.\n\n"
        f"Accédez au dossier de passation (code, accès, secrets) ici :\n{link}\n\n"
        "Une fois le transfert reçu et vérifié, confirmez la réception depuis "
        "cette page pour finaliser la vente.\n\n"
        "— MVPForge"
    )
    send_email(buyer.email, f"Votre achat : {project.title}", body)


def notify_payout(purchase) -> None:
    """Prévient le vendeur que les fonds ont été reversés."""
    project = purchase.project
    seller = project.seller if project else None
    if not seller:
        return
    body = (
        f"{seller.display_name()},\n\n"
        f"L'acheteur a confirmé la réception de « {project.title} ». "
        f"Le montant de {purchase.formatted_seller_amount()} € a été reversé "
        "sur votre compte Stripe.\n\n"
        "Merci d'utiliser MVPForge !"
    )
    send_email(seller.email, f"Paiement reçu : {project.title}", body)
