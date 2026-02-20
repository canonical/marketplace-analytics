import flask
import logging
from django_openid_auth.teams import TeamsRequest, TeamsResponse
from flask_openid import OpenID

logger = logging.getLogger(__name__)

SSO_LOGIN_URL = "https://login.ubuntu.com"
DEFAULT_SSO_TEAM = "canonical-webmonkeys"


def is_authenticated(session):
    return "user" in session


def empty_session(session):
    session.pop("user", None)


def init_sso(app):
    open_id = OpenID(
        store_factory=lambda: None,
        safe_roots=[],
        extension_responses=[TeamsResponse],
    )

    SSO_TEAM = app.config.get("OPENID_LAUNCHPAD_TEAM", DEFAULT_SSO_TEAM)

    @app.route("/logout")
    def logout():
        empty_session(flask.session)
        return flask.redirect("/")

    @app.route("/login", methods=["GET", "POST"])
    @open_id.loginhandler
    def login():
        if is_authenticated(flask.session):
            return flask.redirect(open_id.get_next_url())

        teams_request = TeamsRequest(query_membership=[SSO_TEAM])

        return open_id.try_login(
            SSO_LOGIN_URL,
            ask_for=["email", "nickname"],
            ask_for_optional=["fullname"],
            extensions=[teams_request],
        )

    @open_id.after_login
    def after_login(resp):
        if SSO_TEAM not in resp.extensions["lp"].is_member:
            flask.abort(403)

        flask.session["user"] = {
            "nickname": resp.nickname,
            "fullname": resp.fullname,
            "email": resp.email,
        }

        return flask.redirect(open_id.get_next_url())
