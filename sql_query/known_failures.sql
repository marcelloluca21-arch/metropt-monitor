-- Known failures reported by the operator (source: Data Description_Metro.pdf).
-- The report numbers are kept as published: the second event is labelled "#1"
-- in the source document as well, so report_nr is NOT unique.

CREATE TABLE IF NOT EXISTS known_failures (
    failure_id   smallint PRIMARY KEY,
    report_nr    text        NOT NULL,
    start_time   timestamp   NOT NULL,
    end_time     timestamp   NOT NULL,
    failure_type text        NOT NULL,
    severity     text        NOT NULL,
    report       text,
    CONSTRAINT known_failures_time_order_check CHECK (end_time > start_time)
);

INSERT INTO known_failures (failure_id, report_nr, start_time, end_time, failure_type, severity, report)
VALUES
    (1, '#1', '2020-04-18 00:00', '2020-04-18 23:59', 'Air leak', 'High stress', NULL),
    (2, '#1', '2020-05-29 23:30', '2020-05-30 06:00', 'Air leak', 'High stress', 'Maintenance on 30Apr at 12:00'),
    (3, '#3', '2020-06-05 10:00', '2020-06-07 14:30', 'Air leak', 'High stress', 'Maintenance on 8Jun at 16:00'),
    (4, '#4', '2020-07-15 14:30', '2020-07-15 19:00', 'Air leak', 'High stress', 'Maintenance on 16Jul at 00:00')
ON CONFLICT (failure_id) DO NOTHING;
