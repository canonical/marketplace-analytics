import logging

from flask import Flask, jsonify, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask import request as flask_request
from flask_migrate import Migrate
from sqlalchemy import text
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

db = SQLAlchemy()
migrate = Migrate()
def get_client_ip():
    forwarded = flask_request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return flask_request.remote_addr


limiter = Limiter(key_func=get_client_ip, default_limits=[])


class ReverseProxied:
    """Make Flask aware of the real scheme and path prefix behind HAProxy + traefik."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get("HTTP_X_FORWARDED_PROTO")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        elif environ.get("HTTP_X_FORWARDED_PREFIX"):
            environ["wsgi.url_scheme"] = "https"
        prefix = environ.get("HTTP_X_FORWARDED_PREFIX", "")
        if prefix:
            environ["SCRIPT_NAME"] = prefix
        return self.app(environ, start_response)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.wsgi_app = ReverseProxied(app.wsgi_app)
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    import models  # noqa: F401 - register models with SQLAlchemy

    from analytics.blueprint import analytics_blueprint
    from auth.sso import init_sso
    from auth.decorators import login_required

    app.register_blueprint(analytics_blueprint)
    init_sso(app)

    @app.route("/")
    def index():
        if "user" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/dashboard")
    def dashboard():
        if "user" not in session:
            return redirect(url_for("login", next=url_for("dashboard")))
        return render_template("dashboard.html", user=session["user"])

    # TODO: Remove this endpoint after verifying proxy headers
    @app.route("/debug-headers")
    def debug_headers():
        return jsonify({
            "remote_addr": flask_request.remote_addr,
            "x_forwarded_for": flask_request.headers.get("X-Forwarded-For"),
            "x_forwarded_proto": flask_request.headers.get("X-Forwarded-Proto"),
            "x_forwarded_prefix": flask_request.headers.get("X-Forwarded-Prefix"),
            "x_real_ip": flask_request.headers.get("X-Real-Ip"),
            "scheme": flask_request.scheme,
            "resolved_client_ip": get_client_ip(),
        })

    @app.route("/db-test")
    def dbtest():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "database": str(e)}), 503

    return app


app = create_app()
