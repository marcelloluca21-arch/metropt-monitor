from metropt_pipeline.persistence import get_connection, insert_chunk
from metropt_pipeline.schema import create_cleaned_chunk, load_csv, check_df

def run_pipeline(csv_path, db, chunksize):
    """Validate, clean and load the CSV into PostgreSQL, committing once per chunk."""
    reader = load_csv(csv_path, chunksize)
    with get_connection(db) as conn:
        with conn.cursor() as cursor:
            total_rows = 0
            for i, chunk in enumerate(reader):
                if i == 0:
                    check_df(chunk)

                chunk = create_cleaned_chunk(chunk)
                insert_chunk(cursor, chunk)
                total_rows += len(chunk)
                print(f"Chunk {i + 1} committed | rows processed so far: {total_rows:,}")
                conn.commit()

            print(f"\nIngestion completed: {total_rows:,} rows processed.")


if __name__ == "__main__":
    run_pipeline("data/MetroPT3(AirCompressor).csv", "POSTGRES_DB", 100000)
