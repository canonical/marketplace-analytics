import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRESQL_DB_CONNECT_STRING")
