import flask
import functools

from auth.sso import is_authenticated, empty_session


def login_required(func):
    @functools.wraps(func)
    def is_user_logged_in(*args, **kwargs):
        if not is_authenticated(flask.session):
            empty_session(flask.session)
            return flask.make_response(
                flask.jsonify({"success": False, "error": "Unauthorized"}), 401
            )
        response = flask.make_response(func(*args, **kwargs))
        response.cache_control.private = True
        return response

    return is_user_logged_in
