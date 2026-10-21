import numpy as np
from metropt_pipeline.schema import create_cleaned_chunk, load_csv, check_df

def timestamp_threshold(chunk, threshold, last_timestamp=None):
    timestamp_diff_sec = chunk["timestamp"].diff().dt.total_seconds()

    chunk["registration_off"] = timestamp_diff_sec >= threshold
    chunk["turn_off_duration"] = np.where(chunk["registration_off"], timestamp_diff_sec, 0)

    if last_timestamp is not None:
        first_timestamp = chunk["timestamp"].iloc[0].timestamp()
        diff_first_last_timestamp = first_timestamp - last_timestamp
        if diff_first_last_timestamp >= threshold:
            chunk.loc[chunk.index[0], "registration_off"] = True
            chunk.loc[chunk.index[0], "turn_off_duration"] = diff_first_last_timestamp

    return chunk

if __name__ == "__main__":

    csv_path = "tests/fixtures/valid_minimal.csv"
    chunksize = 100
    threshold = 120

    reader = load_csv(csv_path, chunksize)
    last_timestamp = None

    for i, chunk in enumerate(reader):
        check_df(chunk)
        chunk = create_cleaned_chunk(chunk)

        chunk = timestamp_threshold(chunk, threshold, last_timestamp)
        last_timestamp = chunk["timestamp"].iloc[-1].timestamp()
        print(chunk[["timestamp", "registration_off", "turn_off_duration"]])