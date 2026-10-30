.PHONY: setup lint fmt test up down check

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'
	test -f .env || cp .env.example .env

lint:
	ruff check . && ruff format --check .

fmt:
	ruff check --fix . && ruff format .

test:
	pytest -q

up: s3-config
	docker compose up -d --build

down:
	docker compose down

check: lint test   # same two things CI runs

s3-config:
	python scripts/render_s3_config.py

test-int:
	pytest -q -m integration
