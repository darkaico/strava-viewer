import os

from dotenv import load_dotenv

load_dotenv()

STRAVA_API_CLIENT_ID = os.getenv("STRAVA_API_CLIENT_ID")
STRAVA_API_CLIENT_SECRET = os.getenv("STRAVA_API_CLIENT_SECRET")
STRAVA_API_REFRESH_TOKEN = os.getenv("STRAVA_API_REFRESH_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
