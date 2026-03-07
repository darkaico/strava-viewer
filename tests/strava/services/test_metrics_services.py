import pytest

from strava_viewer.strava.dto import Athlete, SummaryActivity
from strava_viewer.strava.services.metrics_services import (
    compute_by_activity_type,
    compute_by_week,
    compute_totals,
    get_dashboard_metrics,
)


def _athlete(firstname="Test", lastname="User"):
    return Athlete(resource_state=2, firstname=firstname, lastname=lastname)


def _activity(
    distance=1000.0,
    moving_time=3600,
    total_elevation_gain=50.0,
    activity_type="Run",
    start_date="2024-03-01T10:00:00Z",
):
    return SummaryActivity(
        athlete=_athlete(),
        resource_state=2,
        name="Test Activity",
        distance=distance,
        moving_time=moving_time,
        elapsed_time=moving_time,
        total_elevation_gain=total_elevation_gain,
        activity_type=activity_type,
        start_date=start_date,
    )


def test_compute_totals_empty():
    result = compute_totals([])
    assert result.total_distance_km == 0.0
    assert result.total_moving_time_seconds == 0
    assert result.total_elevation_gain_m == 0.0
    assert result.activity_count == 0


def test_compute_totals_single():
    activities = [_activity(distance=5000.0, moving_time=1800, total_elevation_gain=100.0)]
    result = compute_totals(activities)
    assert result.total_distance_km == 5.0
    assert result.total_moving_time_seconds == 1800
    assert result.total_elevation_gain_m == 100.0
    assert result.activity_count == 1


def test_compute_totals_multiple():
    activities = [
        _activity(distance=2000.0, moving_time=600),
        _activity(distance=3000.0, moving_time=900),
    ]
    result = compute_totals(activities)
    assert result.total_distance_km == 5.0
    assert result.total_moving_time_seconds == 1500
    assert result.activity_count == 2


def test_compute_by_activity_type():
    activities = [
        _activity(activity_type="Run", distance=1000.0),
        _activity(activity_type="Run", distance=2000.0),
        _activity(activity_type="Ride", distance=5000.0),
    ]
    result = compute_by_activity_type(activities)
    assert len(result) == 2
    run = next(r for r in result if r.activity_type == "Run")
    ride = next(r for r in result if r.activity_type == "Ride")
    assert run.distance_km == 3.0
    assert run.count == 2
    assert ride.distance_km == 5.0
    assert ride.count == 1


def test_compute_by_week():
    activities = [
        _activity(start_date="2024-03-04T10:00:00Z", distance=1000.0),
        _activity(start_date="2024-03-06T10:00:00Z", distance=2000.0),
        _activity(start_date="2024-03-18T10:00:00Z", distance=3000.0),
    ]
    result = compute_by_week(activities)
    assert len(result) == 2  # two different weeks
    total_km = sum(w.distance_km for w in result)
    assert total_km == 6.0


def test_compute_by_week_skips_missing_start_date():
    a = _activity(start_date="2024-03-04T10:00:00Z", distance=1000.0)
    a.start_date = None
    result = compute_by_week([a])
    assert len(result) == 0


def test_get_dashboard_metrics():
    activities = [
        _activity(distance=5000.0, moving_time=1800, activity_type="Run"),
        _activity(distance=10000.0, moving_time=3600, activity_type="Ride"),
    ]
    metrics = get_dashboard_metrics(activities)
    assert metrics["totals"]["total_distance_km"] == 15.0
    assert metrics["totals"]["activity_count"] == 2
    assert len(metrics["by_type"]) == 2
    assert len(metrics["by_week"]) >= 1
