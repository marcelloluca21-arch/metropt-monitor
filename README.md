# MetroPT Monitor

End-to-end predictive-maintenance project on real telemetry from the air compressor of a
Porto metro train (MetroPT-3 dataset, February–September 2020): data ingestion into
PostgreSQL, anomaly detection compared against the documented failures, an API, a web
dashboard and Power BI reports.

> Work in progress. Done so far: exploratory analysis, chunked ingestion pipeline,
> PostgreSQL layer with idempotent loading, analytical SQL and tests.

## Current status

| Phase | Content | Status |
|---|---|---|
| 1 | Environment, Git workflow, exploratory data analysis (`analisi.ipynb`) | ✅ |
| 2 | Chunked ingestion pipeline with schema validation and unit tests | ✅ |
| 3 | PostgreSQL: schema, idempotent loading, analytical queries, views, indexes | ✅ |
| 4 | Feature engineering (1-minute windows, Parquet, time-based split) | next |
| 5-6 | Anomaly detection: statistical baseline, Isolation Forest, PCA, One-Class SVM | planned |
| 7-8 | FastAPI backend, React + TypeScript dashboard | planned |
| 9-10 | Power BI, Docker Compose for the full stack, CI, online demo | planned |

## Highlights so far

- **Idempotent ingestion**: 1.5 M readings loaded in ~20 s, one transaction per chunk,
  `ON CONFLICT DO NOTHING` on the timestamp key. Re-running the import adds nothing; a
  failing chunk is rolled back without losing the chunks already committed.
- **Integration tests on a real database** (separate `metropt_test` database, pytest
  fixture, `integration` marker).
- **Data insight**: during all four reported air-leak failures the compressor runs under
  load 97–100% of the time, against 16% on average. Details in
  [`docs/database.md`](docs/database.md).

## Tech stack

Python 3.12 · pandas · psycopg 3 · PostgreSQL 18 (Docker) · pytest — later scikit-learn,
FastAPI, React, TypeScript, Power BI.

## Project structure

```
metropt_pipeline/   ingestion pipeline (schema checks, cleaning, persistence, loader)
sql_query/          table definitions, analytical queries, views, indexes
tests/              unit tests and PostgreSQL integration tests (+ small CSV fixtures)
docs/               technical documentation
analisi.ipynb       exploratory data analysis
compose.yaml        PostgreSQL service
```

## Run it locally

Requirements: Python 3.12, Docker Desktop.

```bash
# 1. Python environment
python -m venv .venv
.venv\Scripts\Activate.ps1            # Windows PowerShell
python -m pip install -r requirements.txt

# 2. Configuration
copy .env.example .env                # then edit the values

# 3. Database
docker compose up -d
#    create the tables (see docs/database.md for the full sequence)

# 4. Data: place the dataset at data/MetroPT3(AirCompressor).csv (not versioned)
python -m metropt_pipeline.loader

# 5. Tests
python -m pytest -v                       # all tests (PostgreSQL must be running)
python -m pytest -m "not integration" -v  # unit tests only
```

## Data

MetroPT-3 dataset by Davari, Veloso, Ribeiro, Pereira and Gama (INESC TEC / University of
Porto). The original CSV is kept local and excluded from Git because of its size.
