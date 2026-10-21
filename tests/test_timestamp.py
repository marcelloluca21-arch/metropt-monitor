import pandas as pd
from metropt_pipeline.timestamp import timestamp_threshold

def test_timestamp_threshold():
    test_df = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2020-02-01 08:00:00",   # 0: prima riga, nessuna riga prima
            "2020-02-01 08:00:10",   # 1: +10 s, normale
            "2020-02-01 08:00:30",   # 2: +20 s, misura persa, NON interruzione
            "2020-02-01 08:00:40",   # 3: +10 s, normale
            "2020-02-01 08:05:40",   # 4: +300 s, INTERRUZIONE
            "2020-02-01 08:05:50",   # 5: +10 s, normale
        ]),
    })
    threshold = 120
    timestamp_threshold(threshold, test_df)

    assert test_df["registration_off"].tolist() == [False, False, False, False, True, False,]
    assert test_df["turn_off_duration"].tolist() == [0, 0, 0, 0, 300, 0,]