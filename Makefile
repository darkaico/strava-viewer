install:
	poetry install

test:
	poetry run pytest

flask_start:
	poetry run python -m strava_extensions.flask_server.main

clean: ## Remove generated files.
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

update-packages:
	poetry update

lint:
	pre-commit run --all-files

# Docker

up:
	docker-compose up
