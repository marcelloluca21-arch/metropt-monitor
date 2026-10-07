import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
def get_connection(db):
    """Restituisce un oggetto connessione verso PostgreSQL."""
    return psycopg.connect(
        dbname=os.getenv(db),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
        host=os.getenv("DB_HOST", "localhost"),
    )

def insert_chunk(cursor, chunk):
    cursor.execute("CREATE TEMP TABLE IF NOT EXISTS staging (LIKE metropt INCLUDING ALL) ON COMMIT DROP;")
    # Apre un contesto 'with' dedicato alla scrittura di riga
    with cursor.copy("COPY staging FROM STDIN") as copy:
        for riga in chunk.itertuples(index=False, name=None):
            copy.write_row(riga)

    cursor.execute("""
        INSERT INTO metropt
        SELECT * FROM staging
        ON CONFLICT (timestamp) DO NOTHING;
    """)

    # 4. Svuota la tabella di appoggio per il blocco successivo
    cursor.execute("TRUNCATE TABLE staging;")