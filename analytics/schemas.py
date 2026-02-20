from marshmallow import Schema, fields, validate


class EventSchema(Schema):
    event_type = fields.String(
        required=True,
        validate=validate.OneOf(["click", "hover", "view"]),
    )
    event_source = fields.String(
        load_default="frontend",
        validate=validate.OneOf(["frontend", "backend"]),
    )
    session_id = fields.String(required=True)
    target = fields.String(load_default=None)
    url = fields.String(load_default=None)
    attributes = fields.Dict(load_default=None)


class EventBatchSchema(Schema):
    events = fields.List(
        fields.Nested(EventSchema), required=True
    )
    app_name = fields.String(required=True)
