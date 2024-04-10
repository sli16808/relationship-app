import os

from flask import Flask, render_template, request, session, url_for
from markupsafe import escape


def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "relat3.sqlite")
    )

    if test_config is None:
        # load instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load test config if passed in
        app.config.from_mapping(test_config)

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # sample route to use for testing later
    @app.route("/hello")
    def hello():
        return "Hello, world!"

    # set up db
    from . import db
    db.init_app(app)

    # register auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # register checkin blueprint and add route for /
    from . import checkin
    app.register_blueprint(checkin.bp)
    app.add_url_rule("/", endpoint="index")

    from . import relationship
    app.register_blueprint(relationship.bp, url_prefix="/relationship")

    return app


"""
@app.route("/user/<username>")
def show_user_profile(username):
    # show the user profile for that user
    return f"User {escape(username)}"


@app.route("/post/<int:post_id>")
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f"Post {post_id}"


@app.route("/path/<path:subpath>")
def show_subpath(subpath):
    # show the subpath after /path/
    return f"Subpath {escape(subpath)}"

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
"""
