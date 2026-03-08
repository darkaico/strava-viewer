import os

from dotenv import load_dotenv

load_dotenv()

STRAVA_API_CLIENT_ID = os.getenv("STRAVA_API_CLIENT_ID")
STRAVA_API_CLIENT_SECRET = os.getenv("STRAVA_API_CLIENT_SECRET")
STRAVA_API_REFRESH_TOKEN = os.getenv("STRAVA_API_REFRESH_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")

# Optional TTL in seconds for credentials stored in Redis. None = no expiry.
_raw_ttl = os.getenv("REDIS_CREDENTIALS_TTL")
REDIS_CREDENTIALS_TTL = int(_raw_ttl) if _raw_ttl and _raw_ttl.isdigit() else None

# Activities cache: TTL in seconds (default 24 hours). 0 or unset = use default.
_raw_activities_ttl = os.getenv("STRAVA_ACTIVITIES_CACHE_TTL_SECONDS")
STRAVA_ACTIVITIES_CACHE_TTL_SECONDS = (
    int(_raw_activities_ttl) if _raw_activities_ttl and _raw_activities_ttl.isdigit() else 86400
)
# Set to false to disable activities cache (e.g. "false", "0", "no").
_enabled = os.getenv("STRAVA_ACTIVITIES_CACHE_ENABLED", "true").strip().lower()
STRAVA_ACTIVITIES_CACHE_ENABLED = _enabled not in ("false", "0", "no")
