FROM python:3.11

LABEL maintainer="darkaico@gmail.com"

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    UV_SYSTEM_PYTHON=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY uv.lock pyproject.toml /app/

RUN uv sync --frozen --no-dev --no-install-project

EXPOSE 5000

COPY ./ ./

CMD ["python3", "-m", "strava_viewer.flask_server.main"]
