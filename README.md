[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=darkaico_strava-viewer&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=darkaico_strava-viewer)

# Strava Viewer

App that fetchs information from strava and show in a simple flask application.

## Note

I'm using redis to store Strava access token and set an expiration time. Could it be easily change to just store it plain during app run in case you want to test it without it.

### Strava API

First of all you need Strava API credentials could be found [here](https://developers.strava.com/).

Once you got it you should set the following environment variables

```shell
STRAVA_API_CLIENT_ID=<strava api client id>
STRAVA_API_CLIENT_SECRET=<strava api client secret>
STRAVA_API_REFRESH_TOKEN=<strava api refresh token>
STRAVA_CLUB_ID=<strava club id>
# Optional in case you want to test it locally, otherwise its being updated in docker-compose file
REDIS_URL=redis://localhost:6379
# Optional: port for the Flask server (default: 5000)
FLASK_PORT=5000
```

To make things easier to test in local env im using [python-dotenv](https://github.com/theskumar/python-dotenv) so you could create a new file called `.env` under `strava_viewer` folder (there is an `.env.example` you could us as example).
## Start the App

### Docker

Start the app by just calling

```bash
$ docker-compose up
```

or using make

```bash
$ make up
```

### Local Development
### uv

Im using [uv](https://docs.astral.sh/uv/) as dependency management, make sure you have it installed before following next steps.

- Install dependencies

```shell
uv sync --all-extras
```

- Run Flask Project

```shell
uv run python strava_viewer/flask_server/main.py
```

or using make

```shell
make flask_start
```

- Run tests

```shell
uv run pytest
```

or using make

```shell
make test
```
