from functools import wraps

from flask import flash, redirect, request, url_for

from auth.local_provider import get_current_user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            flash("Connectez-vous pour accéder à cette page.", "info")
            return redirect(url_for("auth.login", next=request.url))
        return view(*args, **kwargs)

    return wrapped
