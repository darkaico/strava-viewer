"""Marshmallow schemas for Strava API payloads; build DTOs in post_load."""

from dacite import from_dict
from marshmallow import EXCLUDE, Schema, fields, post_load

from strava_viewer.strava.dto import Athlete, SummaryActivity


class AthleteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    resource_state = fields.Int(required=False, load_default=1)
    firstname = fields.Str(required=False, load_default="")
    lastname = fields.Str(required=False, load_default="")

    @post_load
    def make_model(self, data, **kwargs):
        return Athlete(**data)


class SummaryActivitySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    athlete = fields.Nested(AthleteSchema)
    resource_state = fields.Int(required=False, load_default=2)
    name = fields.Str(required=False, load_default="")
    distance = fields.Float(required=False, allow_none=True, load_default=0.0)
    moving_time = fields.Int(required=False, allow_none=True, load_default=0)
    elapsed_time = fields.Int(required=False, allow_none=True, load_default=0)
    total_elevation_gain = fields.Float(required=False, allow_none=True, load_default=0.0)
    activity_type = fields.Str(required=False, data_key="type", load_default="Activity")
    workout_type = fields.Int(required=False, allow_none=True)
    start_date = fields.Str(required=False, allow_none=True)

    @post_load
    def make_model(self, data, **kwargs):
        for key in ("distance", "moving_time", "elapsed_time", "total_elevation_gain"):
            if data.get(key) is None:
                data[key] = 0 if key != "distance" and key != "total_elevation_gain" else 0.0
        return from_dict(data_class=SummaryActivity, data=data)
