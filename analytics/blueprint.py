import logging
import re

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from app import db, limiter
from models import Event
from analytics.schemas import EventBatchSchema
from auth.decorators import login_required

logger = logging.getLogger(__name__)

analytics_blueprint = Blueprint("analytics", __name__, url_prefix="/analytics")

_batch_schema = EventBatchSchema()


@analytics_blueprint.route("/events", methods=["POST"])
@cross_origin(origins=[
    "https://snapcraft.io",
    "https://charmhub.io",
    re.compile(r"https?://localhost:\d+"),
    re.compile(r"https://.*\.demos\.haus"),
])
@limiter.limit("1000/minute")
def ingest_events():
    data = request.get_json(silent=True, force=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    errors = _batch_schema.validate(data)
    if errors:
        return jsonify({"error": errors}), 400

    parsed = _batch_schema.load(data)
    app_name = parsed["app_name"]

    try:
        for event_data in parsed["events"]:
            event = Event(
                event_type=event_data["event_type"],
                event_source=event_data["event_source"],
                session_id=event_data["session_id"],
                app_name=app_name,
                target=event_data.get("target"),
                url=event_data.get("url"),
                attributes=event_data.get("attributes"),
            )
            db.session.add(event)

        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Failed to ingest analytics events")
        return "", 204

    return "", 204


@analytics_blueprint.route("/events", methods=["GET"])
@login_required
def get_events():
    app_name = request.args.get("app_name")
    event_type = request.args.get("event_type")
    session_id = request.args.get("session_id")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    per_page = min(per_page, 200)

    query = Event.query.order_by(Event.timestamp.desc())

    if app_name:
        query = query.filter(Event.app_name == app_name)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if session_id:
        query = query.filter(Event.session_id == session_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "events": [
            {
                "event_id": str(e.event_id),
                "event_type": e.event_type,
                "event_source": e.event_source,
                "timestamp": e.timestamp.isoformat(),
                "session_id": e.session_id,
                "app_name": e.app_name,
                "target": e.target,
                "url": e.url,
                "attributes": e.attributes,
            }
            for e in pagination.items
        ],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    })
