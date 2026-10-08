from metropt_pipeline.schema import load_csv, remove_unnamed, check_df, rename_dv_electric, count_rows_with_nulls, convert_digital_binary, count_timestamp_duplicate, convert_timestamp_datetime
import pandas as pd
import pytest
import warnings

def test_load_csv():
    reader = load_csv("tests/fixtures/valid_minimal.csv", 100)
    chunk_count = 0

    for chunk in reader:
        chunk_count += 1
        assert isinstance(chunk, pd.DataFrame)
        assert chunk is not None
        assert len(chunk) > 0

    assert chunk_count > 0

def test_remove_unnamed():
    chunk = pd.DataFrame({
        "Unnamed: 0" : [0, 1],
        "timestamp": ["2020-01-01", "2020-01-02"]
    })
    result = remove_unnamed(chunk)
    assert "Unnamed: 0" not in result.columns
    assert "timestamp" in result.columns

def test_check_df_valid_schema():
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
    valid_df = pd.DataFrame(columns=features)
    df = check_df(valid_df)
    assert features == list(df.columns)

def test_check_df_invalid_schema():
    expected_features = ['Unnamed: 0',
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

    invalid_schemas = [
        expected_features[:-1],                       # missing column
        expected_features + ["extra_column"],        # extra column
        [expected_features[1], expected_features[0], *expected_features[2:]],  # wrong order
    ]

    for features in invalid_schemas:
        with pytest.raises(SystemExit):
            check_df(pd.DataFrame(columns=features))

def test_rename_dv_electric():
    chunk = pd.DataFrame({
            "DV_eletric" : [0, 1],
            "timestamp": ["2020-01-01", "2020-01-02"]
    })
    renamed = rename_dv_electric(chunk)
    assert "dv_electric" in renamed
    assert "DV_eletric" not in renamed
    assert "timestamp" in renamed

def test_count_rows_with_nulls():
    chunk = pd.DataFrame({
        "A": [1, None, 3],
        "B": [10, None, None]  # two rows with nulls, but three null cells
    })
    result = count_rows_with_nulls(chunk)
    assert result == 2

def test_convert_digital_binary():
    chunk = pd.DataFrame({
    "COMP" : [0.0, 1.0],
    "dv_electric" : [1.0, 0.0],
    "Towers": [1.0, 0.0],
    "MPG": [1.0, 0.0],
    "LPS": [1.0, 0.0],
    "Pressure_switch": [1.0, 0.0],
    "Oil_level": [1.0, 0.0],
    "Caudal_impulses": [1.0, 0.0]
    })

    converted = convert_digital_binary(chunk)

    for column in chunk.columns:
        assert pd.api.types.is_integer_dtype(converted[column])

def test_count_timestamp_duplicate():
    chunk = pd.DataFrame({
    "timestamp" : ["2020-02-01 00:00:00", "2020-02-01 00:00:00", "2020-02-01 00:20:00"]
    })

    duplicates = count_timestamp_duplicate(chunk)
    assert duplicates == 1

def test_convert_timestamp_datetime():
    chunk = pd.DataFrame({
    "timestamp" : ["2020-02-15 20:20:01", "2020-02-15 20:20:11", "2020-02-15 20:20:21"]
    })

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        df = convert_timestamp_datetime(chunk)

    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
