import pandas as pd
import sys
def load_csv(percorso_csv, chunksize):
    return pd.read_csv(percorso_csv, chunksize = chunksize)

def remove_unnamed(chunk):
    return chunk.drop(columns=["Unnamed: 0"])

def check_df(chunk):
    features = ['Unnamed: 0',
                'timestamp',
                'TP2',
                'TP3',
                'H1',
                'DV_pressure',
                'Reservoirs',
                'Oil_temperature',
                'Motor_current',
                'COMP',
                'DV_eletric',
                'Towers',
                'MPG',
                'LPS',
                'Pressure_switch',
                'Oil_level',
                'Caudal_impulses']

    if features == list(chunk.columns):
        print("Schema verificato con successo!")
        return(chunk)
    else:
        sys.exit("ERRORE CRITICO: Le colonne del dataset non corrispondono allo schema richiesto. Pipeline bloccata.")

def rename_dv_electric(chunk):
    return chunk.rename(columns={"DV_eletric": "dv_electric"})

def count_righe_valori_null(chunk):
    return chunk.isna().any(axis=1).sum()

def digitali_binari(chunk):
    digitali = [
    "COMP",
    "dv_electric",
    "Towers",
    "MPG",
    "LPS",
    "Pressure_switch",
    "Oil_level",
    "Caudal_impulses"
    ]

    chunk[digitali] = chunk[digitali].astype(int)

    return chunk

def count_timestamp_duplicate(chunk):
    return chunk["timestamp"].duplicated().sum()

def datetime(chunk):
    chunk["timestamp"] = pd.to_datetime(
        chunk["timestamp"],
        format="%Y-%m-%d %H:%M:%S"
    )
    return chunk

def to_lowercase_columns(chunk):
    chunk.columns = chunk.columns.str.lower()
    return chunk

def create_cleaned_chunk(chunk):
    chunk = remove_unnamed(chunk)
    chunk = rename_dv_electric(chunk)
    chunk = digitali_binari(chunk)
    chunk = datetime(chunk)
    chunk = to_lowercase_columns(chunk)
    return chunk

if __name__ == "__main__":

    percorso_csv = "tests/fixtures/valid_minimal.csv"
    chunksize = 100.000
    reader = load_csv(percorso_csv, chunksize)

    totale_chunk = 0
    totale_righe = 0
    totale_nulli = 0
    totale_duplicati_timestamp = 0

    for i, chunk in enumerate(reader):
        # 2. Se è il primissimo chunk (indice 0), controlla lo schema
        if i == 0:
            check_df(chunk)        # 1. Pulisce il chunk corrente (avviene 1 sola volta per ciascun chunk)

        chunk = remove_unnamed(chunk)



        chunk = rename_dv_electric(chunk)
        chunk = digitali_binari(chunk)
        chunk = datetime(chunk)
        chunk = to_lowercase_columns(chunk)

        totale_duplicati_timestamp += count_timestamp_duplicate(chunk)
        totale_nulli += count_righe_valori_null(chunk)
        totale_righe += len(chunk)
        totale_chunk += 1
    print(chunk)

    if totale_chunk == 0:
        sys.exit("ERRORE CRITICO: Nessun dato elaborato dal file.")

    print("Resoconto Finale Pipeline")
    print(f"Totale chunk elaborati: {totale_chunk} ")
    print(f"Totali righe elaborate: {totale_righe}")
    print(f"Totali righe con almeno un valore nullo: {totale_nulli}")
    print(f"Totali timestamp duplicati: {totale_duplicati_timestamp}")
