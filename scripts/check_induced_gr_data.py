from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF  = ROOT / "input" / "reference"
DATA = ROOT / "data" / "processed"

def check_alpha_max_vs_mass():
    print("\n[alpha_max_vs_mass]")
    ref = REF / "alpha_max_vs_mass.csv"
    dst = DATA / "alpha_max_vs_mass.csv"
    print("  ref =", ref)
    print("  dst =", dst)

    if not ref.exists():
        print("  !! MISSING ref file")
        return
    if not dst.exists():
        print("  !! MISSING dst file")
        return

    r = pd.read_csv(ref)
    d = pd.read_csv(dst)

    print("  ref shape:", r.shape, "cols:", list(r.columns))
    print("  dst shape:", d.shape, "cols:", list(d.columns))
    print("  ref head:")
    print(r.head())
    print("  dst head:")
    print(d.head())

    if "mass_Msun" not in r.columns:
        print("  !! ref missing 'mass_Msun'")
        return
    mass_col = "mass"
    if mass_col not in d.columns:
        print(f"  !! dst missing '{mass_col}'")
        return

    # expected dimensionless alpha from ref
    if "hat_alpha_max (dimensionless)" not in r.columns:
        print("  !! ref missing 'hat_alpha_max (dimensionless)'")
        return

    expected = pd.DataFrame({
        "mass": r["mass_Msun"].astype(float),
        "alpha_max": r["hat_alpha_max (dimensionless)"].astype(float),
    })

    merged = d.merge(expected, on="mass", suffixes=("_dst", "_ref"))
    print(f"  merged rows: {len(merged)} (dst={len(d)}, ref={len(expected)})")

    diff = np.abs(merged["alpha_max_dst"].to_numpy() - merged["alpha_max_ref"].to_numpy())
    if diff.size == 0:
        print("  !! no overlapping rows to compare")
        return

    print(f"  max |Δ alpha_max| = {diff.max():.3e}")
    print(f"  min |Δ alpha_max| = {diff.min():.3e}")

    if np.allclose(merged["alpha_max_dst"], merged["alpha_max_ref"], rtol=0.0, atol=0.0):
        print("  OK: processed alpha_max_vs_mass matches reference-derived expectation exactly")
    else:
        print("  !! WARNING: processed alpha_max_vs_mass differs from reference-derived expectation")

def build_expected_alpha_max_vs_x():
    """Rebuild the expected long-form table from the renormalized reference."""
    src = REF / "alpha_max_vs_x_mass_dependent_renormalized.csv"
    if not src.exists():
        raise SystemExit(f"Missing {src}")

    df = pd.read_csv(src)

    # identify x column
    xcol = None
    for c in df.columns:
        lc = c.strip().lower()
        if lc in {"x", "(v/c)^2"}:
            xcol = c
            break
    if xcol is None:
        raise SystemExit(f"{src} must contain an 'x' or '(v/c)^2' column")

    value_cols = [c for c in df.columns if c != xcol]

    long = df.melt(
        id_vars=[xcol],
        value_vars=value_cols,
        var_name="series",
        value_name="alpha_max",
    )

    import re
    def parse_series(s: str):
        m = re.search(r"M[_ ]*([0-9.]+)\s*Msun", s, re.I)
        mass = float(m.group(1)) if m else None
        d = re.search(r"delta[_= ]*([0-9.]+)", s, re.I)
        delta = float(d.group(1)) if d else None
        return mass, delta

    parsed = long["series"].apply(parse_series)
    long["mass"]  = [t[0] for t in parsed]
    long["delta"] = [t[1] for t in parsed]

    long = long.rename(columns={xcol: "X"})
    out = long[["X", "alpha_max", "mass", "delta"]].dropna().reset_index(drop=True)
    return out

def check_alpha_max_vs_x():
    print("\n[alpha_max_vs_x_mass_dependent]")
    ref = REF / "alpha_max_vs_x_mass_dependent_renormalized.csv"
    dst = DATA / "alpha_max_vs_x_mass_dependent.csv"
    print("  ref =", ref)
    print("  dst =", dst)

    if not ref.exists():
        print("  !! MISSING ref file")
        return
    if not dst.exists():
        print("  !! MISSING dst file")
        return

    expected = build_expected_alpha_max_vs_x()
    d = pd.read_csv(dst)

    print("  expected shape:", expected.shape, "cols:", list(expected.columns))
    print("  dst      shape:", d.shape, "cols:", list(d.columns))
    print("  expected head:")
    print(expected.head())
    print("  dst head:")
    print(d.head())

    # basic schema check
    need = {"X", "alpha_max", "mass", "delta"}
    if not need.issubset(d.columns):
        print(f"  !! dst missing required columns {need}")
        return

    # sort by keys for a stable comparison
    keys = ["X", "mass", "delta"]
    exp_sorted = expected.sort_values(keys).reset_index(drop=True)
    dst_sorted = d.sort_values(keys).reset_index(drop=True)

    if exp_sorted.shape != dst_sorted.shape:
        print("  !! shape mismatch after sorting:")
        print("     exp:", exp_sorted.shape, "dst:", dst_sorted.shape)
        # still compute diffs for overlapping part if possible
        n = min(len(exp_sorted), len(dst_sorted))
        exp_sorted = exp_sorted.iloc[:n]
        dst_sorted = dst_sorted.iloc[:n]

    if len(exp_sorted) == 0:
        print("  !! no rows to compare after sorting")
        return

    diff = np.abs(exp_sorted["alpha_max"].to_numpy() - dst_sorted["alpha_max"].to_numpy())
    max_abs = diff.max()
    min_abs = diff.min()
    print(f"  max |Δ alpha_max| = {max_abs:.3e}")
    print(f"  min |Δ alpha_max| = {min_abs:.3e}")

    # relative error (use 1.0 floor to avoid division by tiny numbers)
    denom = np.maximum(np.abs(exp_sorted["alpha_max"].to_numpy()), 1.0)
    rel = diff / denom
    print(f"  max relative |Δ alpha_max| = {rel.max():.3e}")

def check_pulsar():
    print("\n[pulsar_alpha_bounds_renormalized]")
    ref = REF / "pulsar_alpha_bounds_renormalized.csv"
    dst = DATA / "pulsar_alpha_bounds_renormalized.csv"
    print("  ref =", ref)
    print("  dst =", dst)

    if not ref.exists():
        print("  !! MISSING ref file")
        return
    if not dst.exists():
        print("  !! MISSING dst file")
        return

    r = pd.read_csv(ref)
    d = pd.read_csv(dst)
    print("  ref shape:", r.shape, "cols:", list(r.columns))
    print("  dst shape:", d.shape, "cols:", list(d.columns))

    if r.equals(d):
        print("  OK: processed pulsar file is identical to reference")
    else:
        print("  !! WARNING: processed pulsar file differs from reference")

if __name__ == "__main__":
    check_alpha_max_vs_mass()
    check_alpha_max_vs_x()
    check_pulsar()
