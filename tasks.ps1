param([Parameter(Position=0)][string]$Task = "help")

switch ($Task) {
  "setup"     { python -m venv venv; .\venv\Scripts\python -m pip install -e ".[dev]"
                if (-not (Test-Path .env)) { Copy-Item .env.example .env } }
  "lint"      { ruff check .; ruff format --check . }
  "fmt"       { ruff check --fix .; ruff format . }
  "test"      { pytest -q }
  "check"     { ruff check .; ruff format --check .; pytest -q }
  "s3-config" { python scripts\render_s3_config.py }
  "up"        { python scripts\render_s3_config.py; docker compose up -d --build }
  "down"      { docker compose down }
  "test-int"  { pytest -q -m integration }
  default     { "tasks: setup lint fmt test check s3-config up down test-int" }
}