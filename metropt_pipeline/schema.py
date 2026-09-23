import pandas as pd
import sys

def load_csv(percorso_csv):
    return pd.read_csv(percorso_csv, chunksize = 100)


def remove_unnamed(chunk):
    return chunk.drop(columns=["Unnamed: 0"])

def check_df(chunk):
    features = ['timestamp',
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

if __name__ == "__main__":

    reader = load_csv("data/MetroPT3(AirCompressor).csv")

    totale_chunk = 0
    totale_righe = 0
    totale_nulli = 0
    totale_duplicati_timestamp = 0

    for i, chunk in enumerate(reader):
        # 1. Pulisce il chunk corrente (avviene 1 sola volta per ciascun chunk)
        cleaned_chunk = remove_unnamed(chunk)

        # 2. Se è il primissimo chunk (indice 0), controlla lo schema
        if i == 0:
            check_df(cleaned_chunk)

        chunk = rename_dv_electric(cleaned_chunk)
        chunk = digitali_binari(chunk)
        chunk = datetime(chunk)

        totale_duplicati_timestamp += count_timestamp_duplicate(chunk)
        totale_nulli += count_righe_valori_null(chunk)
        totale_righe += len(chunk)
        totale_chunk += 1

    if totale_chunk == 0:
        sys.exit("ERRORE CRITICO: Nessun dato elaborato dal file.")

    print("Resoconto Finale Pipeline")
    print(f"Totale chunk elaborati: {totale_chunk} ")
    print(f"Totali righe elaborate: {totale_righe}")
    print(f"Totali righe con almeno un valore nullo: {totale_nulli}")
    print(f"Totali timestamp duplicati: {totale_duplicati_timestamp}")
