from pathlib import Path
import pandas as pd

def test_alpha_max_vs_x_has_cols():
    p = Path("data/processed/alpha_max_vs_x_mass_dependent.csv")
    assert p.exists()
    df = pd.read_csv(p)
    have = {c.lower() for c in df.columns}
    assert "x" in have or "(v/c)^2" in have or "a_max" in have or "alpha_max" in have

def test_alpha_max_vs_mass_has_cols():
    p = Path("data/processed/alpha_max_vs_mass.csv")
    assert p.exists()
    df = pd.read_csv(p)
    assert {"mass","alpha_max"}.issubset(set(df.columns))
