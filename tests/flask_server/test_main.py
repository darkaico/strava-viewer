import pytest

from strava_viewer.flask_server.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_200(client, mocker):
    mocker.patch(
        "strava_viewer.flask_server.main.get_activities_for_view",
        return_value=[],
    )
    r = client.get("/")
    assert r.status_code == 200


def test_dashboard_returns_200(client, mocker):
    mocker.patch(
        "strava_viewer.flask_server.main.get_strava_credentials",
        return_value={
            "client_id": "123",
            "client_secret": "secret",
            "refresh_token": "token",
        },
    )
    mocker.patch(
        "strava_viewer.flask_server.main.get_activities_for_view",
        return_value=[],
    )
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert b"Total Distance" in r.data
    assert b"Moving Time" in r.data
    assert b"Elevation Gain" in r.data
    assert b"CHARTS" in r.data


def test_dashboard_redirects_to_config_when_not_connected(client, mocker):
    mocker.patch(
        "strava_viewer.flask_server.main.get_strava_credentials",
        return_value=None,
    )
    r = client.get("/dashboard")
    assert r.status_code == 302
    assert r.location and "config" in r.location


def test_config_returns_200(client):
    r = client.get("/config")
    assert r.status_code == 200
    assert b"SYSTEM AUTHENTICATION" in r.data or b"Strava" in r.data
