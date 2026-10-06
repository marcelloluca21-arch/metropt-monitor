CREATE VIEW v_kpi_orari AS
SELECT 
    date_trunc('hour', timestamp) AS ora,
    AVG(tp2) AS media_tp2,
    AVG(oil_temperature) AS media_temp_olio,
    MAX(motor_current) AS picco_corrente,
    SUM(comp) AS secondi_compressore_attivo
FROM metropt
GROUP BY 1;