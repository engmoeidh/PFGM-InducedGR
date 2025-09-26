from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CSV = Path("data/processed/pulsar_alpha_bounds_renormalized.csv")
OUT = Path("figures/pulsar_alpha_bounds.png")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}; run: python scripts/generate_data.py")
    df = pd.read_csv(CSV)
    # Accept either (pulsar, alpha_max_km2) or (name, value) style
    name_col = "pulsar" if "pulsar" in df.columns else df.columns[0]
    val_col  = "alpha_max_km2" if "alpha_max_km2" in df.columns else df.columns[1]
    fig, ax = plt.subplots()
    ax.barh(df[name_col], df[val_col])
    ax.set_xlabel(r"$\alpha_{\max}$  [km$^2$]")
    ax.set_title("Pulsar timing bounds (renormalized)")
    ax.grid(True, axis="x", ls=":")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
