import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
def get_connection(db):
    """Open a PostgreSQL connection.

    `db` is the name of the environment variable that holds the database name
    (e.g. "POSTGRES_DB" or "POSTGRES_DB_TEST"), not the database name itself.
    """
    return psycopg.connect(
        dbname=os.getenv(db),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
        host=os.getenv("DB_HOST", "localhost"),
    )

def insert_chunk(cursor, chunk):
    """Copy a cleaned chunk into a staging table, then insert it skipping existing timestamps."""
    cursor.execute("CREATE TEMP TABLE IF NOT EXISTS staging (LIKE metropt INCLUDING ALL) ON COMMIT DROP;")
    # Bulk-load the chunk into the staging table with COPY
    with cursor.copy("COPY staging FROM STDIN") as copy:
        for row in chunk.itertuples(index=False, name=None):
            copy.write_row(row)

    cursor.execute("""
        INSERT INTO metropt
        SELECT * FROM staging
        ON CONFLICT (timestamp) DO NOTHING;
    """)

    # Empty the staging table before the next chunk
    cursor.execute("TRUNCATE TABLE staging;")