-- Indexes for the metropt table.
--
-- The primary key on "timestamp" already creates a B-tree index (metropt_pkey):
-- every time-range query (WHERE timestamp >= ... AND timestamp < ...) uses it,
-- so no extra index on timestamp is needed.
--
-- Low-pressure alarms (lps = 1) are rare: 5,188 readings out of 1,516,948 (0.34%).
-- A PARTIAL index stores only those rows, so it stays tiny (~136 kB) and turns
-- "find all alarms" from a full table scan into an index-only scan.
-- Measurements are documented in docs/database.md.

CREATE INDEX IF NOT EXISTS metropt_lps_alarm_idx
    ON metropt (timestamp)
    WHERE lps = 1;
