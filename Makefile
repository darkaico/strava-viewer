install:
	uv sync --all-extras

test:
	uv run pytest

flask_start:
	uv run python -m strava_viewer.flask_server.main

clean: ## Remove generated files.
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

update-packages:
	uv lock --upgrade
	uv sync

lint:
	pre-commit run --all-files

# Docker

up:
	docker-compose up
