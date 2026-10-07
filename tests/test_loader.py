import pandas as pd
import pytest
from psycopg.errors import CheckViolation

from metropt_pipeline.loader import pipeline_exe
from metropt_pipeline.persistence import get_connection

DB_TEST = "POSTGRES_DB_TEST"
CSV_VALIDO = "tests/fixtures/valid_minimal.csv"
CSV_CON_ERRORE = "tests/fixtures/invalid_towers_block4.csv"
CHUNKSIZE = 100


@pytest.fixture
def cur():
    """Cursore sul database di test, con la tabella metropt vuota."""
    with get_connection(DB_TEST) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE metropt")
            conn.commit()
            yield cur


def conta_righe(cur):
    """Restituisce il numero di righe presenti nella tabella metropt."""
    cur.execute("SELECT COUNT(*) FROM metropt")
    return cur.fetchone()[0]


@pytest.mark.integration
def test_pipeline_exe(cur):
    righe_attese = len(pd.read_csv(CSV_VALIDO))

    pipeline_exe(CSV_VALIDO, DB_TEST, CHUNKSIZE)
    risultato1 = conta_righe(cur)
    assert risultato1 == righe_attese

    pipeline_exe(CSV_VALIDO, DB_TEST, CHUNKSIZE)
    risultato2 = conta_righe(cur)
    assert risultato2 == risultato1


@pytest.mark.integration
def test_half_chunk_error(cur):
    df_errato = pd.read_csv(CSV_CON_ERRORE)
    posizione_errore = df_errato.index[df_errato["Towers"] == 2][0]

    blocchi_confermati = posizione_errore // CHUNKSIZE
    righe_attese_dopo_errore = blocchi_confermati * CHUNKSIZE

    with pytest.raises(CheckViolation):
        pipeline_exe(CSV_CON_ERRORE, DB_TEST, CHUNKSIZE)

    assert conta_righe(cur) == righe_attese_dopo_errore

    pipeline_exe(CSV_VALIDO, DB_TEST, CHUNKSIZE)
    assert conta_righe(cur) == len(pd.read_csv(CSV_VALIDO))