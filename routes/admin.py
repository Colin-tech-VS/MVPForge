from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def dashboard():
    return render_template("admin/index.html")
