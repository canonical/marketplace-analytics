import logging

from flask import Flask, jsonify, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    import models  # noqa: F401 - register models with SQLAlchemy

    from analytics.blueprint import analytics_blueprint
    from auth.sso import init_sso
    from auth.decorators import login_required

    app.register_blueprint(analytics_blueprint)
    init_sso(app)

    @app.route("/")
    def index():
        if "user" in session:
            return redirect("/dashboard")
        return redirect("/login")

    @app.route("/dashboard")
    @login_required
    def dashboard():
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
