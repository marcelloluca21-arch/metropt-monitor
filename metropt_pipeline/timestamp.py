import pandas as pd
import numpy as np
from metropt_pipeline.schema import create_cleaned_chunk, load_csv, check_df

def timestamp_threshold(threshold, chunk):
        timestamp_diff_sec = chunk["timestamp"].diff().dt.total_seconds()

        chunk["registration_off"] = timestamp_diff_sec >= threshold
        chunk["turn_off_duration"] = np.where(chunk["registration_off"], timestamp_diff_sec, 0)

        return(chunk)

if __name__ == "__main__":

    csv_path = "tests/fixtures/valid_minimal.csv"
    chunksize = 100
    threshold = 120

    reader = load_csv(csv_path, chunksize)

    for i, chunk in enumerate(reader):
        check_df(chunk)
        chunk = create_cleaned_chunk(chunk)

        timestamp_threshold(threshold, chunk)
        print(chunk[["timestamp", "registration_off","turn_off_duration"]])