from metropt_pipeline.persistence import get_connection, insert_chunk
from metropt_pipeline.schema import create_cleaned_chunk, load_csv, check_df

def pipeline_exe(percorso_csv, db, chunksize):
    reader = load_csv(percorso_csv, chunksize)
    with get_connection(db) as conn:
         with conn.cursor() as cursor:
            righe_totali = 0
            for i, chunk in enumerate(reader):
                if i == 0:
                    check_df(chunk)

                chunk = create_cleaned_chunk(chunk)
                insert_chunk(cursor, chunk)
                righe_totali += len(chunk)
                print(f" Blocco {i + 1} completato | Righe elaborate finora: {righe_totali:,}")
                conn.commit()
            
            print(f"\n INGESTION COMPLETATA: {righe_totali:,} righe inserite con successo!")
if __name__ == "__main__":
    pipeline_exe("data/MetroPT3(AirCompressor).csv", "POSTGRES_DB", 100000)
