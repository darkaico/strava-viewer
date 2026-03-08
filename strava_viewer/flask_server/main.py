import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root before any strava_viewer imports that use settings
_project_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_project_root / ".env")

from flask import (  # noqa: E402
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_limiter import Limiter  # noqa: E402
from flask_limiter.util import get_remote_address  # noqa: E402
from flask_wtf import CSRFProtect  # noqa: E402

from strava_viewer.strava.credentials import (  # noqa: E402
    clear_strava_credentials,
    get_strava_credentials,
    set_strava_credentials_redis,
    set_strava_credentials_session,
)
from strava_viewer.strava.services.activities_services import (  # noqa: E402
    clear_activities_cache,
    get_activities_for_view,
)
from strava_viewer.strava.services.metrics_services import (  # noqa: E402
    get_dashboard_metrics,
)

logger = logging.getLogger(__name__)

_DEBUG = os.getenv("FLASK_DEBUG", "false").strip().lower() in ("true", "1", "yes")
_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")
if not _DEBUG and _SECRET_KEY == "dev-secret-change-in-production":
    raise RuntimeError(
        "FLASK_SECRET_KEY must be set in production. "
        "Set FLASK_DEBUG=true only for local development."
    )

app = Flask(__name__)
app.config["SECRET_KEY"] = _SECRET_KEY
app.config["DEBUG"] = _DEBUG
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if os.getenv("PREFER_HTTPS", "false").strip().lower() in ("true", "1", "yes"):
    app.config["SESSION_COOKIE_SECURE"] = True

csrf = CSRFProtect()
csrf.init_app(app)

_storage_uri = os.getenv("RATE_LIMIT_STORAGE_URI")
if _storage_uri:
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[os.getenv("RATE_LIMIT_DEFAULT", "200 per hour")],
        storage_uri=_storage_uri,
    )
else:
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[os.getenv("RATE_LIMIT_DEFAULT", "200 per hour")],
        storage_uri="memory://",
    )


@app.context_processor
def inject_strava_connected():
    connected = get_strava_credentials(session=session) is not None
    return {"strava_connected": connected}


def _require_strava_credentials():
    creds = get_strava_credentials(session=session)
    if not creds:
        return None
    return creds


def _config_edit_allowed():
    """Return True if config save/clear is allowed (no password or correct password)."""
    required = os.getenv("CONFIG_EDIT_PASSWORD", "").strip()
    if not required:
        return True
    return request.form.get("config_edit_password", "").strip() == required


@app.route("/")
def index():
    return render_template(
        "index.html",
        active_nav="home",
        header_title="Strava Viewer",
    )


@app.route("/config", methods=["GET", "POST"])
@limiter.limit(os.getenv("RATE_LIMIT_CONFIG", "10 per minute"))
def config():
    config_edit_required = bool(os.getenv("CONFIG_EDIT_PASSWORD", "").strip())
    if request.method == "POST":
        if not _config_edit_allowed():
            return (
                render_template(
                    "config.html",
                    active_nav="config",
                    header_title="Strava connection",
                    strava_connected=get_strava_credentials(session=session) is not None,
                    config_edit_required=config_edit_required,
                    config_edit_error="Invalid or missing config password.",
                ),
                403,
            )
        action = request.form.get("action")
        if action == "clear":
            clear_strava_credentials(session=session)
            return redirect(url_for("config"))
        if action == "clear_cache":
            clear_activities_cache()
            return redirect(url_for("config", cache_cleared="1"))
        if action == "save":
            client_id = request.form.get("client_id", "").strip()
            client_secret = request.form.get("client_secret", "").strip()
            refresh_token = request.form.get("refresh_token", "").strip()
            try:
                cid = int(client_id)
            except (ValueError, TypeError):
                cid = None
            if cid is not None and client_secret and refresh_token:
                data = {
                    "client_id": str(cid),
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                }
                set_strava_credentials_redis(data)
                set_strava_credentials_session(session, data)
                return redirect(url_for("config"))
    connected = get_strava_credentials(session=session) is not None
    return render_template(
        "config.html",
        active_nav="config",
        header_title="Strava connection",
        strava_connected=connected,
        config_edit_required=config_edit_required,
        config_edit_error=request.args.get("config_edit_error"),
        cache_cleared=request.args.get("cache_cleared") == "1",
    )


@app.route("/activity-list")
@limiter.limit(os.getenv("RATE_LIMIT_API", "30 per minute"))
def activity_list():
    creds = _require_strava_credentials()
    if not creds:
        return redirect(url_for("config"))
    error = None
    activities = []
    try:
        activities = get_activities_for_view(club_id=None, credentials=creds)
        logger.info("Loaded %s activities", len(activities))
    except Exception as e:
        logger.exception("Failed to load activities")
        error = str(e)
    return render_template(
        "activity_list.html",
        club_activities=activities,
        error=error,
        active_nav="activity_list",
        header_title="Strava Viewer",
    )


def _format_moving_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} s"
    minutes, s = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} min"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes} min"


@app.route("/dashboard")
@limiter.limit(os.getenv("RATE_LIMIT_API", "30 per minute"))
def dashboard():
    creds = _require_strava_credentials()
    if not creds:
        return redirect(url_for("config"))
    error = None
    activities = []
    try:
        activities = get_activities_for_view(club_id=None, credentials=creds)
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
        active_nav="dashboard",
        header_title="Dashboard",
    )


@app.route("/lab")
@limiter.limit(os.getenv("RATE_LIMIT_API", "30 per minute"))
def lab():
    creds = _require_strava_credentials()
    if not creds:
        return redirect(url_for("config"))
    error = None
    activities = []
    try:
        activities = get_activities_for_view(club_id=None, credentials=creds)
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
        active_nav="lab",
        header_title="Data Lab: Origins",
    )


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=_DEBUG)
