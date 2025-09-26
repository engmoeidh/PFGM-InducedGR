from __future__ import annotations
from pathlib import Path
import shutil, csv

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
REF   = INPUT / "reference"
DATA  = ROOT / "data" / "processed"
DATA.mkdir(parents=True, exist_ok=True)

def copy_if_exists(src: Path, dst: Path, label: str) -> bool:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"[ok] {label}: copied {src.name} -> {dst}")
        return True
    return False

# --- alpha_max vs x ---
def build_alpha_max_vs_x():
    # Priority: raw -> reference -> demo
    raw = INPUT / "alpha_max_raw.csv"
    if raw.exists():
        out = DATA / "alpha_max_vs_x_mass_dependent.csv"
        # Normalize columns quickly
        with raw.open(newline="", encoding="utf-8") as f, out.open("w", newline="", encoding="utf-8") as g:
            rd = csv.DictReader(f)
            cols = {k.lower(): k for k in rd.fieldnames or []}
            xk  = cols.get("x") or cols.get("(v/c)^2") or cols.get("v2") or cols.get("x_value") or cols.get("x")
            ak  = cols.get("alpha_max") or cols.get("alpha") or cols.get("a_max") or cols.get("alpha*")
            mk  = cols.get("mass") or cols.get("m") or cols.get("label") or cols.get("group")
            if not xk or not ak:
                raise ValueError(f"{raw} must have columns for x and alpha_max")
            wr = csv.writer(g); wr.writerow(["X","a_max","mass"])
            for row in rd: wr.writerow([row[xk], row[ak], row[mk] if mk else ""])
        print(f"[ok] alpha_max_vs_x: derived from {raw.name}")
        return
    # Prefer your renormalized reference if present
    if copy_if_exists(REF/"alpha_max_vs_x_mass_dependent_renormalized.csv",
                      DATA/"alpha_max_vs_x_mass_dependent.csv",
                      "alpha_max_vs_x"):
        return
    # Fallback demo
    out = DATA/"alpha_max_vs_x_mass_dependent.csv"
    demo = [
        (1.0e-6, 10.0, 1.4),
        (2.0e-6,  9.0, 1.4),
        (5.0e-6,  7.5, 1.4),
        (1.0e-5,  6.8, 1.4),
        (1.0e-6, 12.0, 2.0),
        (2.0e-6, 10.5, 2.0),
        (5.0e-6,  8.5, 2.0),
        (1.0e-5,  7.9, 2.0),
    ]
    with out.open("w", newline="", encoding="utf-8") as g:
        wr = csv.writer(g); wr.writerow(["X","a_max","mass"]); wr.writerows(demo)
    print(f"[ok] alpha_max_vs_x: wrote demo {out.name}")

# --- alpha_max vs mass ---
def build_alpha_max_vs_mass():
    if copy_if_exists(REF/"alpha_max_vs_mass.csv", DATA/"alpha_max_vs_mass.csv", "alpha_max_vs_mass"):
        return
    # tiny demo if missing
    out = DATA/"alpha_max_vs_mass.csv"
    with out.open("w", newline="", encoding="utf-8") as g:
        wr = csv.writer(g); wr.writerow(["mass","alpha_max"])
        wr.writerows([(1.2, 12.0), (1.6, 10.0), (2.0, 8.0)])
    print(f"[ok] alpha_max_vs_mass: wrote demo {out.name}")

# --- pulsar bounds (renormalized) ---
def build_pulsar_bounds():
    if copy_if_exists(REF/"pulsar_alpha_bounds_renormalized.csv",
                      DATA/"pulsar_alpha_bounds_renormalized.csv",
                      "pulsar_bounds"):
        return
    out = DATA/"pulsar_alpha_bounds_renormalized.csv"
    with out.open("w", newline="", encoding="utf-8") as g:
        wr = csv.writer(g); wr.writerow(["pulsar","alpha_max_km2"])
        wr.writerows([("J0737-3039", 1.0e3), ("J1713+0747", 8.0e3)])
    print(f"[ok] pulsar_bounds: wrote demo {out.name}")

def main():
    build_alpha_max_vs_x()
    build_alpha_max_vs_mass()
    build_pulsar_bounds()

if __name__ == "__main__":
    main()
