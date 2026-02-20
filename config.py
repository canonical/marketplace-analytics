import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRESQL_DB_CONNECT_STRING")
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24).hex())
    OPENID_LAUNCHPAD_TEAM = os.environ.get(
        "OPENID_LAUNCHPAD_TEAM", "canonical-webmonkeys"
    )
