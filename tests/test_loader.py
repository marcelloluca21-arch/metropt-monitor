import pandas as pd
import pytest
from psycopg.errors import CheckViolation

from metropt_pipeline.loader import run_pipeline
from metropt_pipeline.persistence import get_connection

DB_TEST = "POSTGRES_DB_TEST"
VALID_CSV = "tests/fixtures/valid_minimal.csv"
INVALID_CSV = "tests/fixtures/invalid_towers_block4.csv"
CHUNKSIZE = 100


@pytest.fixture
def cur():
    """Cursor on the test database, with an empty metropt table."""
    with get_connection(DB_TEST) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE metropt")
            conn.commit()
            yield cur


def count_rows(cur):
    """Return the number of rows in the metropt table."""
    cur.execute("SELECT COUNT(*) FROM metropt")
    return cur.fetchone()[0]


@pytest.mark.integration
def test_second_import_adds_no_rows(cur):
    expected_rows = len(pd.read_csv(VALID_CSV))

    run_pipeline(VALID_CSV, DB_TEST, CHUNKSIZE)
    total1 = count_rows(cur)
    assert total1 == expected_rows

    run_pipeline(VALID_CSV, DB_TEST, CHUNKSIZE)
    total2 = count_rows(cur)
    assert total2 == total1


@pytest.mark.integration
def test_half_chunk_error(cur):
    df_incorrect = pd.read_csv(INVALID_CSV)
    error_position = df_incorrect.index[df_incorrect["Towers"] == 2][0]

    confirmed_chunks = error_position // CHUNKSIZE
    expected_rows_after_error = confirmed_chunks * CHUNKSIZE

    with pytest.raises(CheckViolation):
        run_pipeline(INVALID_CSV, DB_TEST, CHUNKSIZE)

    assert count_rows(cur) == expected_rows_after_error

    run_pipeline(VALID_CSV, DB_TEST, CHUNKSIZE)
    assert count_rows(cur) == len(pd.read_csv(VALID_CSV))
