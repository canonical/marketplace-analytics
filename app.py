import logging

from flask import Flask, jsonify, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
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

    @app.route("/db-test")
    def dbtest():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "database": str(e)}), 503

    return app


app = create_app()
