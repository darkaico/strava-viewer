import time
from functools import cached_property
from http import HTTPStatus

import requests
from marshmallow import ValidationError

from strava_viewer.strava import settings
from strava_viewer.strava.schemas import SummaryActivitySchema
from strava_viewer.strava.utils.redis_client import get_redis_client
from strava_viewer.utils.mixins import LoggerMixin


class StravaAPI(LoggerMixin):

    API_URL = "https://www.strava.com/api/v3"
    REFRESH_TOKEN_URL = "https://www.strava.com/oauth/token"
    access_token = None

    def __init__(self, credentials=None):
        self.redis_client = get_redis_client()
        if credentials and isinstance(credentials, dict):
            self.api_client_id = credentials.get("client_id")
            self.api_client_secret = credentials.get("client_secret")
            self.api_refresh_token = credentials.get("refresh_token")
        else:
            self.api_client_id = settings.STRAVA_API_CLIENT_ID
            self.api_client_secret = settings.STRAVA_API_CLIENT_SECRET
            self.api_refresh_token = settings.STRAVA_API_REFRESH_TOKEN

    @cached_property
    def access_token_redis_key(self):
        return f"access-token-{self.api_client_id}"

    def get_access_token(self):
        if not self.redis_client.exists(self.access_token_redis_key):
            self._refresh_token()

        token = self.redis_client.get(self.access_token_redis_key)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token or ""

    def _refresh_token(self):
        data = {
            "client_id": self.api_client_id,
            "client_secret": self.api_client_secret,
            "refresh_token": self.api_refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(self.REFRESH_TOKEN_URL, data=data)

        if response.status_code != HTTPStatus.OK:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise requests.exceptions.HTTPError(
                    "Strava refresh token expired or invalid. Re-authorize the app at "
                    "https://www.strava.com/settings/api (or your app's OAuth URL), "
                    "then set STRAVA_API_REFRESH_TOKEN in .env with the new refresh token. "
                    "Ensure the app has activity:read scope.",
                    response=response,
                )
            response.raise_for_status()

        json_response = response.json()
        expires_at = int(json_response["expires_at"])
        # Redis ex= expects seconds until expiry; Strava gives absolute Unix timestamp
        ttl_seconds = max(1, expires_at - int(time.time()))
        self.redis_client.set(
            self.access_token_redis_key,
            json_response["access_token"],
            ex=ttl_seconds,
        )

    def get(self, resource_url: str, params=None):
        url = f"{self.API_URL}/{resource_url}"
        request_params = dict(params) if params else {}
        request_params["access_token"] = self.get_access_token()

        response = requests.get(url, params=request_params)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            self.redis_client.delete(self.access_token_redis_key)
            self._refresh_token()
            request_params["access_token"] = self.get_access_token()
            response = requests.get(url, params=request_params)

        if response.status_code != 200:
            self.logger.error(response)
            response.raise_for_status()

        return response.json()

    def _parse_activities(self, json_activities):
        if not json_activities:
            return []
        try:
            return SummaryActivitySchema(many=True).load(json_activities)
        except (ValidationError, TypeError):
            self.logger.exception("Activity list validation failed")
            raise

    def get_athlete_activities(self, after=None, before=None, per_page=200):
        """List the authenticated athlete's activities. Requires activity:read scope."""
        resource_url = "athlete/activities"
        params = {"per_page": min(per_page, 200)}
        if after is not None:
            params["after"] = int(after)
        if before is not None:
            params["before"] = int(before)
        json_activities = self.get(resource_url, params=params)
        return self._parse_activities(json_activities)

    def get_club_activities(self, club_id: int):
        resource_url = f"clubs/{club_id}/activities"
        json_activities = self.get(resource_url)
        return self._parse_activities(json_activities)
