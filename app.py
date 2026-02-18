import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "POSTGRESQL_DB_CONNECT_STRING", ""
)
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "Marketplace Analytics"


@app.route("/db-test")
def dbtest():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": str(e)}), 503
