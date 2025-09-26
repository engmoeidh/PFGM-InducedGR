from pathlib import Path
import pandas as pd

def test_alpha_max_vs_x_has_cols():
    p = Path("data/processed/alpha_max_vs_x_mass_dependent.csv")
    assert p.exists()
    df = pd.read_csv(p)
    cols = set(df.columns.str.lower())
    assert {"x","alpha_max"}.issubset(cols)
    # optional fields
    assert "mass" in cols
    # delta may or may not exist
    # if present, must be numeric
    if "delta" in cols:
        assert pd.api.types.is_numeric_dtype(df["delta"])

def test_alpha_max_vs_mass_has_cols():
    p = Path("data/processed/alpha_max_vs_mass.csv")
    assert p.exists()
    df = pd.read_csv(p)
    assert {"mass","alpha_max"}.issubset(set(df.columns))
