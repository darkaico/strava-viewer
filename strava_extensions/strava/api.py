from functools import cached_property
from http import HTTPStatus

import requests

from strava_extensions.strava import settings
from strava_extensions.strava.services.builder_service import BuilderService
from strava_extensions.strava.utils.redis_client import get_redis_client
from strava_extensions.utils.mixins import LoggerMixin


class StravaAPI(LoggerMixin):

    API_URL = "https://www.strava.com/api/v3"
    REFRESH_TOKEN_URL = "https://www.strava.com/oauth/token"
    access_token = None

    def __init__(self):
        self.redis_client = get_redis_client()
        self.api_client_id = settings.STRAVA_API_CLIENT_ID
        self.api_client_secret = settings.STRAVA_API_CLIENT_SECRET
        self.api_refresh_token = settings.STRAVA_API_REFRESH_TOKEN

    @cached_property
    def access_token_redis_key(self):
        return f"access-token-{self.api_client_id}"

    def get_access_token(self):
        if not self.redis_client.exists(self.access_token_redis_key):
            self._refresh_token()

        return self.redis_client.get(self.access_token_redis_key)

    def _refresh_token(self):
        data = {
            "client_id": self.api_client_id,
            "client_secret": self.api_client_secret,
            "refresh_token": self.api_refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(self.REFRESH_TOKEN_URL, data=data)

        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        json_response = response.json()
        expires_at = int(json_response["expires_at"])
        self.redis_client.set(
            self.access_token_redis_key, json_response["access_token"], ex=expires_at
        )

    def get(self, resource_url: str):
        url = f"{self.API_URL}/{resource_url}"

        response = requests.get(url, params={"access_token": self.get_access_token()})

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            self._refresh_token()
            response = requests.get(url, params={"access_token": self.get_access_token()})

        if response.status_code != 200:
            self.logger.error(response)
            response.raise_for_status()

        return response.json()

    def get_club_activities(self, club_id: int):
        resource_url = f"clubs/{club_id}/activities"

        json_activities = self.get(resource_url)

        return BuilderService.build_summary_activities(json_activities)
