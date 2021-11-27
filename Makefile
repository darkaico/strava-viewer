install:
	poetry install

test:
	poetry run pytest

flask_start:
	poetry run python -m strava_extensions.flask_server.main

clean:
	find . -iname '*.pyc' -delete
	rm -rf .pytest_cache

update-packages:
	poetry update

lint:
	pre-commit run --all-files

# Docker

up:
	docker-compose up
