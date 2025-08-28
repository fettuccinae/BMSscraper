from functools import wraps
from flask import redirect, url_for, g


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


def login_forbidden(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None:
            return redirect(url_for("tix.index"))
        return view(**kwargs)

    return wrapped_view
