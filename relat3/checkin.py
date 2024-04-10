from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint("checkin", __name__)

@bp.route("/")
@login_required
def index():
    db = get_db()
    checkins = db.execute(
        """
        SELECT c.id, title, body, created, author_id, username
        FROM checkins c JOIN users u ON c.author_id = u.id
        ORDER BY created DESC
        """
    ).fetchall()
    return render_template("checkin/index.html", checkins=checkins)


@bp.route("/create", methods=("GET", "POST",))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """
                INSERT INTO checkins (title, body, author_id)
                VALUES (?, ?, ?)
                """,
                (title, body, g.user["id"])
            )
            db.commit()
            return redirect(url_for("checkin.index"))
    
    return render_template("checkin/create.html")


def get_checkin(id, check_author=True):
    checkin = get_db().execute(
        """
        SELECT c.id, title, body, created, author_id, username
        FROM checkins c JOIN users u ON c.author_id = u.id
        WHERE c.id = ?
        """,
        (id,)
    ).fetchone()

    if checkin is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and checkin["author_id"] != g.user["id"]:
        abort(403)

    return checkin


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    checkin = get_checkin(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                """
                UPDATE checkins
                SET title = ?, body = ?
                WHERE id = ?
                """,
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("checkin.index"))
        
    return render_template("checkin/update.html", checkin=checkin)
    

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_checkin(id)
    db = get_db()
    db.execute(
        """
        DELETE FROM checkins
        WHERE id = ?
        """,
        (id,)
    )
    db.commit()
    return redirect(url_for("checkin.index"))