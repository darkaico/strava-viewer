# Strava Viewer

App that fetches information from Strava and shows it in a simple Flask application.

## Note

Redis is used to store the Strava access token with an expiration time. You can change this to store it in memory during app run if you want to test without Redis.

## Setup

### Strava API

You need Strava API credentials from [developers.strava.com](https://developers.strava.com/).

Set the following environment variables:

```shell
STRAVA_API_CLIENT_ID=<your client id>
STRAVA_API_CLIENT_SECRET=<your client secret>
STRAVA_API_REFRESH_TOKEN=<your refresh token>
STRAVA_CLUB_ID=<your club id>

# Optional: for local dev (docker-compose sets this for Docker)
REDIS_URL=redis://localhost:6379

# Optional: Flask server port (default: 5000)
FLASK_PORT=5000
```

For local development, use [python-dotenv](https://github.com/theskumar/python-dotenv): create a `.env` file under the `strava_viewer` folder (see `.env.example`).

## Running the app

### Docker

```bash
docker-compose up
```

or:

```bash
make up
```

### Local development

Install [uv](https://docs.astral.sh/uv/), then:

**Install dependencies**

```shell
uv sync --all-extras
```

**Run the app**

```shell
uv run python strava_viewer/flask_server/main.py
```

or:

```shell
make flask_start
```

**Run tests**

```shell
uv run pytest
```

or:

```shell
make test
```
