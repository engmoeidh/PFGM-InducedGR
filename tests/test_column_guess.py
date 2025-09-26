import pandas as pd
from pathlib import Path

def test_alpha_max_vs_x_long_schema():
    p = Path("data/processed/alpha_max_vs_x_mass_dependent.csv")
    assert p.exists(), "normalized alpha_max_vs_x CSV was not generated"
    df = pd.read_csv(p)
    cols = set(df.columns)
    # normalized / long schema
    assert {"X","alpha_max","mass"}.issubset(cols)
    # delta is optional but allowed
    if "delta" in cols:
        assert pd.api.types.is_numeric_dtype(df["delta"])
