import json

from marshmallow import Schema, fields, validate, validates, ValidationError


class EventSchema(Schema):
    event_type = fields.String(
        required=True,
        validate=validate.OneOf(["click", "hover", "view"]),
    )
    event_source = fields.String(
        load_default="frontend",
        validate=validate.OneOf(["frontend", "backend"]),
    )
    session_id = fields.String(required=True, validate=validate.Length(max=255))
    target = fields.String(load_default=None, validate=validate.Length(max=255))
    url = fields.String(load_default=None, validate=validate.Length(max=2048))
    attributes = fields.Dict(load_default=None)

    @validates("attributes")
    def validate_attributes(self, value, **kwargs):
        if value and len(json.dumps(value)) > 4096:
            raise ValidationError("Attributes must not exceed 4KB.")


class EventBatchSchema(Schema):
    events = fields.List(
        fields.Nested(EventSchema),
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    app_name = fields.String(
        required=True,
        validate=validate.OneOf(["snapcraft", "charmhub"]),
    )
