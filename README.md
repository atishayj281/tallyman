# Warehouse Analytics Agent

Ask questions in plain English; get SQL, results and charts from a governed warehouse mart

## Quick start

```bash
make setup      # venv, dev deps, .env from .env.example
make check      # lint + tests (what CI runs)
make up         # docker compose up --build
curl localhost:8000/health
```

## Layout

| Path | What lives there | Task |
|---|---|---|
| `ingestion/` | TPC-H generation, Parquet writers, load metadata | WA-02 to WA-07 |
| `dbt/` | sources, staging, star-schema mart, docs | WA-05, 06, 10 |
| `orchestration/` | Airflow DAGs | WA-08, 09 |
| `agent/` | LangGraph loop, tools, SQL validator | WA-11 to WA-18 |
| `api/` | FastAPI service | WA-21 |
| `streaming/` | Kafka producer and consumer | WA-22 to WA-24 |
| `eval/` | test set, harness, benchmarks | WA-28 to WA-32 |
| `frontend/` | React app | WA-27 |
| `results/` | measured numbers that feed the resume | every milestone |
| `src/wa/` | shared code (config, logging) | WA-01 |
