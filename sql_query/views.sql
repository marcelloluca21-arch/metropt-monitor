-- Views consumed by Power BI and, later, by the API.
-- Replaces the first draft "v_kpi_orari": its column "secondi_compressore_attivo"
-- was SUM(comp), but comp = 1 means the compressor is OFF/offloaded and each
-- reading covers ~10 s, not 1 s, so both the meaning and the unit were wrong.

DROP VIEW IF EXISTS v_kpi_orari;

-- Hourly KPIs.
CREATE OR REPLACE VIEW hourly_kpis AS
SELECT date_trunc('hour', timestamp) AS hour,
       COUNT(*)                      AS n_readings,
       AVG(tp2)                      AS avg_tp2,
       AVG(tp3)                      AS avg_tp3,
       AVG(oil_temperature)          AS avg_oil_temperature,
       MAX(oil_temperature)          AS max_oil_temperature,
       AVG(motor_current)            AS avg_motor_current,
       MAX(motor_current)            AS max_motor_current,
       AVG(dv_electric)              AS load_ratio,          -- share of readings under load
       SUM(lps)                      AS low_pressure_readings -- readings below 7 bar
FROM metropt
GROUP BY 1;

-- Daily KPIs, including data coverage, time under load and load cycles.
-- Each reading "lasts" until the next one; gaps longer than 60 s are outages
-- and are not counted as covered time (same rule as query Q4).
CREATE OR REPLACE VIEW daily_kpis AS
WITH readings AS (
    SELECT timestamp,
           oil_temperature,
           motor_current,
           dv_electric,
           lps,
           LAG(dv_electric) OVER (ORDER BY timestamp) AS prev_dv_electric,
           EXTRACT(EPOCH FROM LEAD(timestamp) OVER (ORDER BY timestamp) - timestamp) AS seconds_to_next
    FROM metropt
)
SELECT timestamp::date                                          AS day,
       COUNT(*)                                                 AS n_readings,
       ROUND(SUM(seconds_to_next) FILTER (WHERE seconds_to_next <= 60) / 3600.0, 2)
                                                                AS hours_covered,
       ROUND(SUM(seconds_to_next) FILTER (WHERE seconds_to_next <= 60
                                            AND dv_electric = 1) / 3600.0, 2)
                                                                AS hours_under_load,
       AVG(oil_temperature)                                     AS avg_oil_temperature,
       MAX(oil_temperature)                                     AS max_oil_temperature,
       MAX(motor_current)                                       AS max_motor_current,
       COUNT(*) FILTER (WHERE prev_dv_electric = 0
                          AND dv_electric = 1)                  AS load_cycles,
       SUM(lps)                                                 AS low_pressure_readings
FROM readings
GROUP BY 1;
