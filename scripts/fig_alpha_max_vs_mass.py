from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CSV = Path("data/processed/alpha_max_vs_mass.csv")
OUT = Path("figures/alpha_max_vs_mass.png")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}; run: python scripts/generate_data.py")
    df = pd.read_csv(CSV)
    fig, ax = plt.subplots()
    ax.plot(df["mass"], df["alpha_max"], marker="o")
    ax.set_xlabel("Mass [M☉]")
    ax.set_ylabel(r"$\alpha_{\max}$")
    ax.set_title(r"$\alpha_{\max}$ vs mass")
    ax.grid(True, ls=":")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
