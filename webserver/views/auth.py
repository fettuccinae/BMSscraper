from flask import Blueprint, request, url_for, flash, render_template, redirect, session, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from webserver.db.user import check_if_user_name_is_unique, register_user, get_user
from webserver.decorators import login_forbidden, login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.before_app_request
def load_user_from_session():
    user_name = session.get("user_name")
    if user_name is None:
        g.user = None
    else:
        g.user = get_user(user_name)


@login_forbidden
@auth_bp.route("/register", methods=["GET", "POST"])
def registeration():
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")
        if not user_name or not password:
            flash("BOTH user_name AND PASSWORD REQUIRED")

        elif not check_if_user_name_is_unique(user_name):
            flash("user_name ALREADY EXISTS")

        else:
            try:
                register_user(user_name, generate_password_hash(password))
                flash("SUCCESSFULLY REGISTERED")
                return redirect(url_for("auth.login"))

            except Exception as err:
                current_app.logger.error(f"db error{err}")
                flash("SOME DB ERROR BNRUH, TRY LATER")

    return render_template("auth/register.html")


@login_forbidden
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")

        user = get_user(user_name)

        error = None
        if user is None:
            error = "user_name DOESNT EXSIST"
        elif not check_password_hash(user["password_hash"], password):
            error = "WRONG PASSWORD MY"
        else:
            session.clear()
            session["user_name"] = user["user_name"]
            return redirect(url_for("tix.index"))
        
        flash(error)
    
    return render_template("auth/login.html")


@login_required
@auth_bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
