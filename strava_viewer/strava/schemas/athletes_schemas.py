from marshmallow import EXCLUDE, Schema, fields, post_load

from strava_viewer.strava.models.athletes import Athlete


class AthleteSchema(Schema):

    class Meta:
        unknown = EXCLUDE

    resource_state = fields.Int(required=False, load_default=1)
    firstname = fields.Str(required=False, load_default="")
    lastname = fields.Str(required=False, load_default="")

    @post_load
    def make_model(self, data, **kwargs):
        return Athlete(**data)
