import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root before any strava_viewer imports that use settings
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")

from flask import Flask, render_template  # noqa: E402
from flask_wtf import CSRFProtect  # noqa: E402

from strava_viewer.strava.services.activities_services import (  # noqa: E402
    get_activities_for_view,
)
from strava_viewer.strava.services.metrics_services import (  # noqa: E402
    get_dashboard_metrics,
)

logger = logging.getLogger(__name__)
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)


@app.route("/")
@app.route("/index")
def index():
    error = None
    activities = []
    try:
        activities = get_activities_for_view(club_id=None)
        logger.info("Loaded %s activities", len(activities))
    except Exception as e:
        logger.exception("Failed to load activities")
        error = str(e)
    return render_template("index.html", club_activities=activities, error=error)


def _format_moving_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} s"
    minutes, s = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} min"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes} min"


@app.route("/dashboard")
def dashboard():
    error = None
    activities = []
    try:
        activities = get_activities_for_view(club_id=None)
        logger.info("Loaded %s activities for dashboard", len(activities))
    except Exception as e:
        logger.exception("Failed to load activities for dashboard")
        error = str(e)
    metrics = get_dashboard_metrics(activities)
    totals = metrics["totals"]
    totals["total_moving_time_formatted"] = _format_moving_time(
        totals["total_moving_time_seconds"]
    )
    return render_template(
        "dashboard.html",
        metrics=metrics,
        chart_data_by_week=json.dumps(metrics["by_week"]),
        chart_data_by_type=json.dumps(metrics["by_type"]),
        error=error,
    )


@app.route("/lab")
def lab():
    error = None
    activities = []
    try:
        activities = get_activities_for_view(club_id=None)
        logger.info("Loaded %s activities for lab", len(activities))
    except Exception as e:
        logger.exception("Failed to load activities for lab")
        error = str(e)
    metrics = get_dashboard_metrics(activities)
    totals = metrics["totals"]
    totals["total_moving_time_formatted"] = _format_moving_time(
        totals["total_moving_time_seconds"]
    )
    return render_template(
        "data_lab.html",
        metrics=metrics,
        chart_data_by_week=json.dumps(metrics["by_week"]),
        chart_data_by_type=json.dumps(metrics["by_type"]),
        error=error,
    )


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
