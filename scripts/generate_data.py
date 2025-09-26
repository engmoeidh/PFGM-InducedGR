from __future__ import annotations
from pathlib import Path
import shutil, csv, re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
REF   = INPUT / "reference"
DATA  = ROOT / "data" / "processed"
DATA.mkdir(parents=True, exist_ok=True)

def copy(src: Path, dst: Path, what: str) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"[ok] {what}: copied {src.name} -> {dst}")
        return True
    return False

# --- alpha_max vs x (mass-dependent, renormalized) ---
def build_alpha_max_vs_x():
    # Prefer your renormalized reference
    src = REF / "alpha_max_vs_x_mass_dependent_renormalized.csv"
    if not src.exists():
        # fallback tiny demo
        out = DATA / "alpha_max_vs_x_mass_dependent.csv"
        demo = pd.DataFrame({"X":[1e-6,2e-6,5e-6,1e-5],
                             "alpha_max":[10.0,9.0,7.5,6.8],
                             "mass":[1.4,1.4,1.4,1.4],
                             "delta":[0.001,0.001,0.001,0.001]})
        demo.to_csv(out, index=False)
        print(f"[ok] alpha_max_vs_x: wrote demo {out.name}")
        return

    df = pd.read_csv(src)
    # Expect: first column is x (could be "x" or "(v/c)^2")
    xcol = None
    for c in df.columns:
        lc = c.strip().lower()
        if lc in {"x","(v/c)^2"}:
            xcol = c; break
    if xcol is None:
        raise ValueError(f"{src} must contain an 'x' or '(v/c)^2' column")

    # Melt all alpha columns: alpha_max_M_2.6Msun_delta_0.001  → mass=2.6, delta=0.001
    value_cols = [c for c in df.columns if c != xcol]
    long = df.melt(id_vars=[xcol], value_vars=value_cols, var_name="series", value_name="alpha_max")

    def parse_series(s: str):
        # patterns like: alpha_max_M_2.6Msun_delta_0.001
        m = re.search(r"M[_ ]*([0-9.]+)\s*Msun", s, re.I)
        mass = float(m.group(1)) if m else None
        d = re.search(r"delta[_= ]*([0-9.]+)", s, re.I)
        delta = float(d.group(1)) if d else None
        return mass, delta

    parsed = long["series"].apply(parse_series)
    long["mass"]  = [t[0] for t in parsed]
    long["delta"] = [t[1] for t in parsed]
    long = long.rename(columns={xcol:"X"})
    # Keep only necessary columns, drop NA rows
    out_df = long[["X","alpha_max","mass","delta"]].dropna().reset_index(drop=True)

    out = DATA / "alpha_max_vs_x_mass_dependent.csv"
    out_df.to_csv(out, index=False)
    print(f"[ok] alpha_max_vs_x: normalized wide→long → {out}")

# --- alpha_max vs mass (prefer dimensionless hat_alpha) ---
def build_alpha_max_vs_mass():
    src = REF / "alpha_max_vs_mass.csv"
    if not src.exists():
        # demo
        out = DATA / "alpha_max_vs_mass.csv"
        pd.DataFrame({"mass":[1.2,1.6,2.0],"alpha_max":[12.0,10.0,8.0]}).to_csv(out, index=False)
        print(f"[ok] alpha_max_vs_mass: wrote demo {out.name}")
        return

    df = pd.read_csv(src)
    # pick mass column
    mass_col = None
    for c in df.columns:
        if c.lower() in {"mass","mass_msun"}:
            mass_col = c; break
    if mass_col is None:
        raise ValueError(f"{src} must contain 'mass' or 'mass_Msun'")

    # pick alpha column: prefer hat_alpha_max (dimensionless); otherwise a column starting with 'alpha_max'
    prefer = [c for c in df.columns if "hat_alpha_max" in c]
    if prefer:
        alpha_col = prefer[0]
    else:
        cand = [c for c in df.columns if c.strip().lower().startswith("alpha_max")]
        if not cand:
            raise ValueError(f"{src} must contain a column starting with 'alpha_max' or 'hat_alpha_max'")
        alpha_col = cand[0]

    out_df = pd.DataFrame({
        "mass": df[mass_col],
        "alpha_max": df[alpha_col]
    })
    out = DATA / "alpha_max_vs_mass.csv"
    out_df.to_csv(out, index=False)
    print(f"[ok] alpha_max_vs_mass: normalized → {out} (alpha from '{alpha_col}')")

# --- pulsar bounds (copy through) ---
def build_pulsar_bounds():
    copy(REF/"pulsar_alpha_bounds_renormalized.csv",
         DATA/"pulsar_alpha_bounds_renormalized.csv",
         "pulsar_bounds")

def main():
    build_alpha_max_vs_x()
    build_alpha_max_vs_mass()
    build_pulsar_bounds()

if __name__ == "__main__":
    main()
