from dataclasses import dataclass
from typing import Optional

from strava_viewer.strava.utils import materialize_mapping_utils

from .athletes import Athlete


@dataclass
class SummaryActivity:

    athlete: Athlete
    resource_state: int
    name: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    activity_type: str
    workout_type: Optional[int] = None

    @property
    def materialize_icon(self):
        return materialize_mapping_utils.get_icon_by_activity(self.activity_type)
