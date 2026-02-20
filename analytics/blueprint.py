import logging

from flask import Blueprint, request, jsonify

from app import db
from models import Event
from analytics.schemas import EventBatchSchema

logger = logging.getLogger(__name__)

analytics_blueprint = Blueprint("analytics", __name__, url_prefix="/analytics")

_batch_schema = EventBatchSchema()


@analytics_blueprint.route("/events", methods=["POST"])
def ingest_events():
    data = request.get_json(silent=True)
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
