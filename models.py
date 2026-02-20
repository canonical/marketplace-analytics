import uuid

from app import db


class Event(db.Model):
    __tablename__ = "events"

    event_id = db.Column(
        db.UUID, primary_key=True, default=uuid.uuid4
    )
    event_type = db.Column(db.String(50), nullable=False)
    event_source = db.Column(
        db.String(50), nullable=False, default="frontend"
    )
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    session_id = db.Column(db.String(255), nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(255), nullable=True)
    url = db.Column(db.Text, nullable=True)
    attributes = db.Column(db.JSON, nullable=True)

    __table_args__ = (
        db.Index("ix_events_timestamp", "timestamp"),
        db.Index("ix_events_event_type", "event_type"),
        db.Index("ix_events_session_id", "session_id"),
        db.Index("ix_events_app_name", "app_name"),
    )
