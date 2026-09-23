from metropt_pipeline.schema import load_csv, remove_unnamed, check_df, rename_dv_electric, count_righe_valori_null, digitali_binari, count_timestamp_duplicate, datetime
import pandas as pd
import pytest
import warnings

#per creare i test devo utilizzare la logica AAA:
#Arrange - Act - Assert
def test_load_csv():
    reader = load_csv("tests/fixtures/valid_minimal.csv")
    chunk_count = 0

    for chunk in reader:
        chunk_count += 1
        assert isinstance(chunk, pd.DataFrame)
        assert chunk is not None
        assert len(chunk) > 0

    # Verifica che sia stato elaborato ALMENO un chunk
    assert chunk_count > 0

def test_remove_unnamed():
    chunk = pd.DataFrame({
        "Unnamed: 0" : [0, 1],
        "timestamp": ["2020-01-01", "2020-01-02"]
    })
    df_risultato = remove_unnamed(chunk)
    assert "Unnamed: 0" not in df_risultato.columns
    assert "timestamp" in df_risultato.columns

def test_check_df_corretto():
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
    df_valido = pd.DataFrame(columns=features)
    df = check_df(df_valido)
    assert features == list(df.columns)

def test_check_df_errato():
    features_corrette = ['timestamp',
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

    schemi_errati = [
        features_corrette[:-1],
        features_corrette + ["colonna_extra"],
        [features_corrette[1], features_corrette[0], *features_corrette[2:]],
    ]

    for features in schemi_errati:
        with pytest.raises(SystemExit):
            check_df(pd.DataFrame(columns=features))

def test_rename_dv_electric():
    chunk = pd.DataFrame({
            "DV_eletric" : [0, 1],
            "timestamp": ["2020-01-01", "2020-01-02"]
    })
    dv_corretto = rename_dv_electric(chunk)
    assert "dv_electric" in dv_corretto
    assert "DV_eletric" not in dv_corretto
    assert "timestamp" in dv_corretto

def test_count_righe_valori_null():
    chunk = pd.DataFrame({
        "A": [1, None, 3],
        "B": [10, None, None]  # Due righe con nulli, ma tre celle nulle
    })
    risultato = count_righe_valori_null(chunk)
    assert risultato == 2

def test_digitali_binari():
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

    df_binario = digitali_binari(chunk)

    for colonna in chunk.columns:
        assert pd.api.types.is_integer_dtype(df_binario[colonna])

def test_count_timestamp_duplicate():
    chunk = pd.DataFrame({
    "timestamp" : ["2020-02-01 00:00:00", "2020-02-01 00:00:00", "2020-02-01 00:20:00"]
    })

    duplicati = count_timestamp_duplicate(chunk)
    assert duplicati == 1

def test_datetime():
    chunk = pd.DataFrame({
    "timestamp" : ["2020-02-15 20:20:01", "2020-02-15 20:20:11", "2020-02-15 20:20:21"]
    })

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        df = datetime(chunk)

    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
