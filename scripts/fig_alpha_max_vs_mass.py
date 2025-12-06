from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CSV = Path("data/processed/alpha_max_vs_mass.csv")
OUT = Path("figures/alpha_max_vs_mass.png")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}; run: python scripts/generate_data.py")
    df = pd.read_csv(CSV)

    print("[info] Loaded", CSV, "shape", df.shape)
    print("[info] head:")
    print(df.head())

    fig, ax = plt.subplots()
    ax.plot(df["mass"], df["alpha_max"], marker="o")

    ax.set_xlabel(r"Mass $M\,[M_\odot]$")
    # generate_data.py chooses 'hat_alpha_max (dimensionless)' from the reference table,
    # so the processed 'alpha_max' is the dimensionless bound \hat{alpha}_max(M).
    ax.set_ylabel(r"$\hat{\alpha}_{\max}$")
    ax.set_title(r"Maximal allowed $\hat{\alpha}$ vs mass (dimensionless)")

    ax.grid(True, linestyle=":", alpha=0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
