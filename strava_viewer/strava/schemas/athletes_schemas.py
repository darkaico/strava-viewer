from marshmallow import Schema, fields, post_load

from strava_viewer.strava.models.athletes import Athlete


class AthleteSchema(Schema):

    resource_state = fields.Int(required=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)

    @post_load
    def make_model(self, data, **kwargs):
        return Athlete(**data)
