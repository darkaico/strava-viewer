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
