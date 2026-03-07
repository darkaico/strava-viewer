"""Aggregate SummaryActivity lists into metrics for dashboard charts and cards."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List

from strava_viewer.strava.dto import SummaryActivity


@dataclass
class Totals:
    total_distance_km: float
    total_moving_time_seconds: int
    total_elevation_gain_m: float
    activity_count: int


@dataclass
class ByTypeItem:
    activity_type: str
    distance_km: float
    count: int
    moving_time_seconds: int
    elevation_gain_m: float


@dataclass
class ByWeekItem:
    week_label: str  # e.g. "2024-W12"
    distance_km: float
    moving_time_seconds: int
    elevation_gain_m: float
    count: int


def compute_totals(activities: List[SummaryActivity]) -> Totals:
    """Sum distance, moving time, elevation and count across all activities."""
    if not activities:
        return Totals(0.0, 0, 0.0, 0)
    total_distance = sum(a.distance for a in activities) / 1000.0  # m -> km
    total_time = sum(a.moving_time for a in activities)
    total_elevation = sum(a.total_elevation_gain for a in activities)
    return Totals(
        total_distance_km=round(total_distance, 2),
        total_moving_time_seconds=total_time,
        total_elevation_gain_m=round(total_elevation, 1),
        activity_count=len(activities),
    )


def compute_by_activity_type(activities: List[SummaryActivity]) -> List[ByTypeItem]:
    """Group by activity_type; return list of type, distance, count, time, elevation."""
    by_type: dict = defaultdict(
        lambda: {"distance": 0.0, "count": 0, "moving_time": 0, "elevation": 0.0}
    )
    for a in activities:
        t = a.activity_type or "Other"
        by_type[t]["distance"] += a.distance / 1000.0
        by_type[t]["count"] += 1
        by_type[t]["moving_time"] += a.moving_time
        by_type[t]["elevation"] += a.total_elevation_gain
    return [
        ByTypeItem(
            activity_type=key,
            distance_km=round(by_type[key]["distance"], 2),
            count=by_type[key]["count"],
            moving_time_seconds=by_type[key]["moving_time"],
            elevation_gain_m=round(by_type[key]["elevation"], 1),
        )
        for key in sorted(by_type.keys())
    ]


def _parse_week_key(iso_date_str: str) -> str | None:
    """Return ISO week label 'YYYY-Www' or None if unparseable."""
    if not iso_date_str:
        return None
    try:
        # Handle both "2024-03-07T12:00:00Z" and "2024-03-07"
        dt = datetime.fromisoformat(iso_date_str.replace("Z", "+00:00")[:10])
        return dt.strftime("%Y-W%W")
    except (ValueError, TypeError):
        return None


def compute_by_week(activities: List[SummaryActivity]) -> List[ByWeekItem]:
    """Group activities by week (start_date); activities without start_date are skipped."""
    by_week: dict = defaultdict(
        lambda: {"distance": 0.0, "moving_time": 0, "elevation": 0.0, "count": 0}
    )
    for a in activities:
        key = _parse_week_key(a.start_date) if getattr(a, "start_date", None) else None
        if not key:
            continue
        by_week[key]["distance"] += a.distance / 1000.0
        by_week[key]["moving_time"] += a.moving_time
        by_week[key]["elevation"] += a.total_elevation_gain
        by_week[key]["count"] += 1
    return [
        ByWeekItem(
            week_label=key,
            distance_km=round(by_week[key]["distance"], 2),
            moving_time_seconds=by_week[key]["moving_time"],
            elevation_gain_m=round(by_week[key]["elevation"], 1),
            count=by_week[key]["count"],
        )
        for key in sorted(by_week.keys())
    ]


def get_dashboard_metrics(activities: List[SummaryActivity]) -> dict:
    """
    Return a dict suitable for the dashboard view: totals, by_type, by_week.
    by_type and by_week are lists of dicts for JSON/chart use.
    """
    totals = compute_totals(activities)
    by_type = compute_by_activity_type(activities)
    by_week = compute_by_week(activities)
    return {
        "totals": {
            "total_distance_km": totals.total_distance_km,
            "total_moving_time_seconds": totals.total_moving_time_seconds,
            "total_elevation_gain_m": totals.total_elevation_gain_m,
            "activity_count": totals.activity_count,
        },
        "by_type": [
            {
                "activity_type": t.activity_type,
                "distance_km": t.distance_km,
                "count": t.count,
                "moving_time_seconds": t.moving_time_seconds,
                "elevation_gain_m": t.elevation_gain_m,
            }
            for t in by_type
        ],
        "by_week": [
            {
                "week_label": w.week_label,
                "distance_km": w.distance_km,
                "moving_time_seconds": w.moving_time_seconds,
                "elevation_gain_m": w.elevation_gain_m,
                "count": w.count,
            }
            for w in by_week
        ],
    }
