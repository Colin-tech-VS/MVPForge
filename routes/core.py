from flask import Blueprint, redirect, url_for

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def root():
    return redirect(url_for("site.home"))
