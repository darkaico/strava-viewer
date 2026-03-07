"""Strava credential resolution: .env first, then Redis, then Flask session."""

import json

from strava_viewer.strava import settings
from strava_viewer.strava.utils.redis_client import get_redis_client

REDIS_CREDENTIALS_KEY = "strava:credentials"
SESSION_CREDENTIALS_KEY = "strava_credentials"


def _from_env():
    client_id = settings.STRAVA_API_CLIENT_ID
    client_secret = settings.STRAVA_API_CLIENT_SECRET
    refresh_token = settings.STRAVA_API_REFRESH_TOKEN
    if client_id and client_secret and refresh_token:
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
    return None


def _required_keys_present(data):
    if not data or not isinstance(data, dict):
        return False
    return all(data.get(k) for k in ("client_id", "client_secret", "refresh_token"))


def get_strava_credentials(session=None):
    """
    Return Strava credentials from env, then Redis, then session.
    Returns dict with client_id, client_secret, refresh_token or None.
    """
    env_creds = _from_env()
    if _required_keys_present(env_creds):
        return env_creds

    try:
        redis_client = get_redis_client()
        raw = redis_client.get(REDIS_CREDENTIALS_KEY)
        if raw:
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            data = json.loads(raw)
            if _required_keys_present(data):
                return data
    except Exception:
        pass

    if session:
        data = session.get(SESSION_CREDENTIALS_KEY)
        if _required_keys_present(data):
            return data

    return None


def set_strava_credentials_redis(data):
    """Store credentials in Redis. No-op if Redis not configured or data invalid."""
    if not _required_keys_present(data):
        return
    try:
        redis_client = get_redis_client()
        if hasattr(redis_client, "set"):
            redis_client.set(
                REDIS_CREDENTIALS_KEY,
                json.dumps(
                    {
                        "client_id": str(data["client_id"]).strip(),
                        "client_secret": str(data["client_secret"]).strip(),
                        "refresh_token": str(data["refresh_token"]).strip(),
                    }
                ),
            )
    except Exception:
        pass


def set_strava_credentials_session(session, data):
    """Store credentials in Flask session."""
    if not session or not _required_keys_present(data):
        return
    session[SESSION_CREDENTIALS_KEY] = {
        "client_id": str(data["client_id"]).strip(),
        "client_secret": str(data["client_secret"]).strip(),
        "refresh_token": str(data["refresh_token"]).strip(),
    }


def clear_strava_credentials(session=None):
    """Remove credentials from Redis and session. Does not modify .env."""
    try:
        redis_client = get_redis_client()
        if hasattr(redis_client, "delete"):
            redis_client.delete(REDIS_CREDENTIALS_KEY)
    except Exception:
        pass
    if session and SESSION_CREDENTIALS_KEY in session:
        session.pop(SESSION_CREDENTIALS_KEY, None)
