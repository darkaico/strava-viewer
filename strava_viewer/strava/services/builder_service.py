from marshmallow import ValidationError

from strava_viewer.strava.schemas.activities_schemas import SummaryActivitySchema
from strava_viewer.utils import logger_utils


class BuilderService:

    logger = logger_utils.build_logger("builder_service")

    @classmethod
    def build_summary_activities(cls, json_summary_activities: dict):
        result = []
        if not json_summary_activities:
            return result

        try:
            result = SummaryActivitySchema(many=True).load(json_summary_activities)
        except (ValidationError, TypeError) as err:
            cls.logger.error(err)

        return result
