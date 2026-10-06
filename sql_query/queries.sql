-- Analytical queries on the MetroPT-3 compressor telemetry (table: metropt).
-- Signal semantics (Data Description_Metro.pdf):
--   dv_electric = 1  -> compressor working UNDER LOAD
--   comp        = 1  -> no air intake: compressor OFF or OFFLOADED
--   lps         = 1  -> pressure below 7 bar
-- Readings arrive roughly every 10 seconds (the CSV is sub-sampled from 1 Hz).
-- Time filters use half-open intervals [start, end) so that consecutive
-- windows never count the same reading twice.


-- Q1. Readings inside a time window (failure #4: 2020-07-15 14:30 - 19:00).
SELECT timestamp, tp2, tp3, reservoirs, motor_current, oil_temperature, comp, dv_electric, lps
FROM metropt
WHERE timestamp >= '2020-07-15 14:30'
  AND timestamp <  '2020-07-15 19:00'
ORDER BY timestamp;


-- Q2. Hourly statistics for one day.
SELECT date_trunc('hour', timestamp)       AS hour,
       COUNT(*)                            AS n_readings,
       ROUND(AVG(tp3)::numeric, 3)         AS avg_tp3,
       ROUND(MIN(tp3)::numeric, 3)         AS min_tp3,
       ROUND(AVG(oil_temperature)::numeric, 2) AS avg_oil_temperature,
       ROUND(MAX(oil_temperature)::numeric, 2) AS max_oil_temperature,
       ROUND(MAX(motor_current)::numeric, 2)   AS max_motor_current,
       ROUND(AVG(dv_electric)::numeric, 3) AS load_ratio
FROM metropt
WHERE timestamp >= '2020-07-15'
  AND timestamp <  '2020-07-16'
GROUP BY 1
ORDER BY 1;


-- Q3. Load cycles per day: a cycle starts when dv_electric switches 0 -> 1.
-- LAG() reads the value of the previous reading in time order.
WITH transitions AS (
    SELECT timestamp,
           dv_electric,
           LAG(dv_electric) OVER (ORDER BY timestamp) AS prev_dv_electric
    FROM metropt
)
SELECT timestamp::date AS day,
       COUNT(*)        AS load_cycles
FROM transitions
WHERE prev_dv_electric = 0
  AND dv_electric = 1
GROUP BY 1
ORDER BY 1;


-- Q4. Estimated time under load per day.
-- Each reading "lasts" until the next one (LEAD). Gaps longer than 60 s are
-- data outages, not operating time, so they are excluded from the sum.
WITH durations AS (
    SELECT timestamp,
           dv_electric,
           EXTRACT(EPOCH FROM LEAD(timestamp) OVER (ORDER BY timestamp) - timestamp) AS seconds_to_next
    FROM metropt
)
SELECT timestamp::date                                        AS day,
       ROUND(SUM(seconds_to_next) FILTER (WHERE dv_electric = 1) / 3600.0, 2) AS hours_under_load,
       ROUND(SUM(seconds_to_next) / 3600.0, 2)                AS hours_covered
FROM durations
WHERE seconds_to_next <= 60
GROUP BY 1
ORDER BY 1;


-- Q5. Data gaps: consecutive readings more than 60 seconds apart.
WITH gaps AS (
    SELECT LAG(timestamp) OVER (ORDER BY timestamp) AS gap_start,
           timestamp                                AS gap_end
    FROM metropt
)
SELECT gap_start,
       gap_end,
       gap_end - gap_start AS gap_length
FROM gaps
WHERE gap_end - gap_start > INTERVAL '60 seconds'
ORDER BY gap_length DESC
LIMIT 20;


-- Q6. Behaviour inside each documented failure window (JOIN with known_failures).
SELECT f.failure_id,
       f.start_time,
       f.end_time,
       COUNT(m.timestamp)                          AS n_readings,
       ROUND(AVG(m.dv_electric)::numeric, 3)       AS load_ratio,
       ROUND(AVG(m.oil_temperature)::numeric, 2)   AS avg_oil_temperature,
       SUM(m.lps)                                  AS low_pressure_readings
FROM known_failures AS f
LEFT JOIN metropt AS m
       ON m.timestamp >= f.start_time
      AND m.timestamp <  f.end_time
GROUP BY f.failure_id, f.start_time, f.end_time
ORDER BY f.failure_id;
