# Database layer

PostgreSQL stores the MetroPT-3 telemetry loaded by the ingestion pipeline and exposes
query-ready views for Power BI and, later, for the API.

## Schema

| Object | Type | Purpose | File |
|---|---|---|---|
| `metropt` | table | One row per reading: timestamp + 7 analogue + 8 digital signals | `sql_query/create_table.sql` |
| `known_failures` | table | The 4 failure windows reported by the operator | `sql_query/known_failures.sql` |
| `hourly_kpis` | view | Hourly averages/maxima, load ratio, low-pressure readings | `sql_query/views.sql` |
| `daily_kpis` | view | Daily coverage, hours under load, load cycles, maxima | `sql_query/views.sql` |
| `metropt_lps_alarm_idx` | partial index | Fast lookup of low-pressure alarms | `sql_query/indexes.sql` |

Design choices for `metropt`:

- **`timestamp` is the primary key**: the dataset comes from a single compressor, so a
  timestamp identifies one reading. The key also makes the import idempotent (see below).
- Analogue signals are `double precision`; digital signals are `smallint` with a
  `CHECK (... IN (0, 1))` constraint, because `smallint` alone would accept any integer.
- Every column is `NOT NULL`: the exploratory analysis found no missing values, and any
  future gap must be explicit rather than silently stored.

## Ingestion: idempotent, one transaction per chunk

`metropt_pipeline/loader.py` reads the CSV in chunks, validates the schema on the first
chunk, cleans every chunk and loads it through a temporary staging table:

1. `COPY` the chunk into `staging` (created with `LIKE metropt INCLUDING ALL`, so it
   inherits the same constraints);
2. `INSERT INTO metropt SELECT * FROM staging ON CONFLICT (timestamp) DO NOTHING`;
3. `COMMIT`.

Consequences, verified by the integration tests in `tests/test_loader.py`:

| Scenario | Result |
|---|---|
| Same file imported twice | Row count unchanged (1,516,948 on the full dataset) |
| Invalid value in chunk 4 (`towers = 2`) | Pipeline stops with `CheckViolation`; chunks 1-3 stay committed; chunk 4 is rolled back entirely (300 rows, not 312) |
| Re-run on the corrected file | Missing rows are added, existing ones are skipped: no duplicates |

Full load of the 208 MB CSV (16 chunks of 100,000 rows): about 20-25 seconds on a laptop.

## Signal semantics used in the queries

From the dataset documentation:

| Signal | `1` means |
|---|---|
| `dv_electric` | compressor working **under load** |
| `comp` | **no air intake**: compressor off or offloaded |
| `lps` | pressure below 7 bar |

Readings arrive roughly every 10 seconds (the published dataset is 1 Hz; this CSV is a
sub-sample). Durations are therefore computed from the time to the next reading, ignoring
gaps longer than 60 seconds, which are data outages.

## Analytical queries (`sql_query/queries.sql`)

| # | Question | Technique |
|---|---|---|
| Q1 | Readings inside a time window (failure #4) | half-open range on the primary key |
| Q2 | Hourly statistics for one day | `date_trunc`, `GROUP BY` |
| Q3 | Load cycles per day | window function `LAG` |
| Q4 | Hours under load per day | window function `LEAD`, `FILTER` |
| Q5 | Longest data gaps | `LAG` on timestamps |
| Q6 | Behaviour inside each failure window | `LEFT JOIN` with `known_failures` |

### What the data shows

Inside **all four** documented failure windows the compressor runs under load almost
continuously, while the whole-dataset average is 16%:

| Failure | Window | Readings | Load ratio | Avg oil temp (°C) | Low-pressure readings |
|---|---|---|---|---|---|
| 1 | 2020-04-18 00:00 - 23:59 | 8,657 | 0.989 | 74.13 | 0 |
| 2 | 2020-05-29 23:30 - 05-30 06:00 | 2,360 | 0.992 | 75.87 | 0 |
| 3 | 2020-06-05 10:00 - 06-07 14:30 | 17,315 | 1.000 | 75.52 | 198 |
| 4 | 2020-07-15 14:30 - 19:00 | 1,621 | 0.974 | 83.91 | 530 |

This is the expected signature of an air leak (the compressor keeps working to restore
pressure) and a strong hint for the anomaly-detection phase. On 2020-07-15 the compressor
was under load for 11.5 hours, against 3-4 hours on the neighbouring days.

The longest data gap is two days (2020-04-25 01:10 → 2020-04-27 01:12); on average a day
has about 19.8 hours of covered time. Gaps are reported, never interpolated.

## Indexes and query plans

Measured with `EXPLAIN (ANALYZE, BUFFERS)` on the full table (1,516,948 rows, 158 MB),
PostgreSQL 16, warm cache:

| Query | Plan | Execution time |
|---|---|---|
| Q1 window (1,621 rows) using the primary key | Index Scan on `metropt_pkey` | **0.36 ms** |
| Same query with index scans disabled | Parallel Seq Scan, 1.5 M rows filtered | 61 ms |
| All low-pressure alarms, no extra index | Parallel Seq Scan | 78 ms |
| Same query with the partial index | Index Only Scan on `metropt_lps_alarm_idx` (136 kB) | **≈1 ms** |

Takeaways:

- The primary key already covers every time-range query: no additional timestamp index.
- A **partial index** is the right tool for a rare condition: it indexes 0.34% of the rows
  and costs 136 kB, against 33 MB for the full primary-key index.
- `daily_kpis` scans the whole table with two window functions (~2 s). That is acceptable
  for an export; if it becomes a bottleneck for the API it can be turned into a
  materialized view refreshed after each import.

## How to recreate the database

```bash
docker compose up -d
psql -h localhost -U <user> -d <db> -f sql_query/create_table.sql
psql -h localhost -U <user> -d <db> -f sql_query/known_failures.sql
psql -h localhost -U <user> -d <db> -f sql_query/indexes.sql
python -m metropt_pipeline.loader
psql -h localhost -U <user> -d <db> -f sql_query/views.sql
```

For the integration tests, create a second database (e.g. `metropt_test`), run
`create_table.sql` in it and set `POSTGRES_DB_TEST` in `.env`.
