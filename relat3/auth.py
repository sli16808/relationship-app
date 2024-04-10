import functools
import re

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


# register route allows new users to create an account
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first-name"]
        family_name = request.form["family-name"]
        db = get_db()
        error = None

        if not email:
            error = "Email is required"
        elif not email_validator(email):
            error = "Invalid email address"
        elif not password:
            error = "Password is required"
        elif not first_name:
            error = "First name is required"
        elif not family_name:
            error = "Family name is required"

        if error is None:
            try:
                db.execute(
                    """
                    INSERT INTO users (email, password, first_name, family_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        email,
                        generate_password_hash(password),
                        first_name,
                        family_name,
                    ),
                )
                db.commit()
            except db.IntegrityError:
                error = f"{email} is already associated with an account."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


# login route lets existing users log into account using
# the user table and password hash
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM users where email = ?", (email,)
        ).fetchone()

        if user is None:
            error = "Email address not found."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


# logout route allows logged-in user to end session
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# function to set g.user to session user if it exists
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM users where id = ?", (user_id,)).fetchone()
        )


# validate email syntax
def email_validator(email):
    if re.match(r'^[\w\.-]+@[\w\.-]+$', email):
        return True
    else:
        return False


# login_required is a helper function to decorate functions
# and make sure that a user is logged in (based on g.user)
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
