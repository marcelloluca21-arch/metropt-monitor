import pandas as pd
import sys
def load_csv(csv_path, chunksize):
    return pd.read_csv(csv_path, chunksize = chunksize)

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
        print("Schema verified successfully.")
        return(chunk)
    else:
        sys.exit("CRITICAL ERROR: Dataset feautures doesn't match.")

def rename_dv_electric(chunk):
    return chunk.rename(columns={"DV_eletric": "dv_electric"})

def count_rows_with_nulls(chunk):
    return chunk.isna().any(axis=1).sum()

def convert_digital_binary(chunk):
    digital = [
    "COMP",
    "dv_electric",
    "Towers",
    "MPG",
    "LPS",
    "Pressure_switch",
    "Oil_level",
    "Caudal_impulses"
    ]

    chunk[digital] = chunk[digital].astype(int)

    return chunk

def count_timestamp_duplicate(chunk):
    return chunk["timestamp"].duplicated().sum()

def convert_timestamp_datetime(chunk):
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
    chunk = convert_digital_binary(chunk)
    chunk = convert_timestamp_datetime(chunk)
    chunk = to_lowercase_columns(chunk)
    return chunk

if __name__ == "__main__":

    csv_path = "tests/fixtures/valid_minimal.csv"
    chunksize = 100000
    reader = load_csv(csv_path, chunksize)

    total_chunk = 0
    total_rows = 0
    total_null = 0
    total_duplicated_timestamp = 0

    for i, chunk in enumerate(reader):
        if i == 0:
            check_df(chunk)

        chunk = remove_unnamed(chunk)
        chunk = rename_dv_electric(chunk)
        chunk = convert_digital_binary(chunk)
        chunk = convert_timestamp_datetime(chunk)
        chunk = to_lowercase_columns(chunk)

        total_duplicated_timestamp += count_timestamp_duplicate(chunk)
        total_null += count_rows_with_nulls(chunk)
        total_rows += len(chunk)
        total_chunk += 1
    print(chunk)

    if total_chunk == 0:
        sys.exit("CRITICAL ERROR: No data processed from file.")

    print("Pipeline summary")
    print(f"Total chunks processed: {total_chunk}")
    print(f"Total rows processed: {total_rows}")
    print(f"Total rows with at least one null: {total_null}")
    print(f"Total duplicated timestamps: {total_duplicated_timestamp}")
