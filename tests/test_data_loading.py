from src.data.load_data import generate_sample_demand, normalize_demand_columns


def test_sample_demand_schema():
    df = generate_sample_demand(periods=48)
    assert list(df.columns) == ["datetime", "demand_mw"]
    assert len(df) == 48


def test_normalize_pjm_style_columns():
    df = generate_sample_demand(periods=4).rename(columns={"datetime": "Datetime", "demand_mw": "PJME_MW"})
    normalized = normalize_demand_columns(df)
    assert list(normalized.columns) == ["datetime", "demand_mw"]
