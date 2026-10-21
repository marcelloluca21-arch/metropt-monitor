import pandas as pd
from metropt_pipeline.timestamp import timestamp_threshold


def test_timestamp_threshold():
    test_df = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2020-02-01 08:00:00",   # 0: first row, nothing before
            "2020-02-01 08:00:10",   # 1: +10 s, normal
            "2020-02-01 08:00:30",   # 2: +20 s, one missed reading, NOT an interruption
            "2020-02-01 08:00:40",   # 3: +10 s, normal
            "2020-02-01 08:05:40",   # 4: +300 s, INTERRUPTION
            "2020-02-01 08:05:50",   # 5: +10 s, normal
        ]),
    })
    threshold = 120
    timestamp_threshold(test_df, threshold)

    assert test_df["registration_off"].tolist() == [False, False, False, False, True, False]
    assert test_df["turn_off_duration"].tolist() == [0, 0, 0, 0, 300, 0]


def test_timestamp_threshold_across_chunks():
    """An interruption that falls exactly between two chunks must be detected."""
    chunk_1 = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2020-02-01 08:00:00",
            "2020-02-01 08:00:10",
            "2020-02-01 08:00:20",
        ]),
    })
    chunk_2 = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([
                "2020-02-01 08:05:20",   # +300 s from the end of chunk_1: INTERRUPTION
                "2020-02-01 08:05:30",   # +10 s, normal
            ]),
        },
        index=[3, 4],  # like a real reader: the second chunk does not start from 0
    )
    threshold = 120

    chunk_1 = timestamp_threshold(chunk_1, threshold)
    last_timestamp = chunk_1["timestamp"].iloc[-1].timestamp()
    chunk_2 = timestamp_threshold(chunk_2, threshold, last_timestamp)

    assert chunk_1["registration_off"].tolist() == [False, False, False]
    assert chunk_2["registration_off"].tolist() == [True, False]
    assert chunk_2["turn_off_duration"].tolist() == [300, 0]
