from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# constants (SI)
G    = 6.67430e-11
c    = 2.99792458e8
Msun = 1.98847e30

def length_scale_m(mass_msun: float) -> float:
    """(GM/c^2) in meters for a given mass in Msun."""
    return G * (mass_msun * Msun) / c**2

CSV = Path("data/processed/pulsar_alpha_bounds_renormalized.csv")
OUT = Path("figures/pulsar_alpha_bounds.png")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}; run: python scripts/generate_data.py")
    df = pd.read_csv(CSV)

    print("[info] Loaded", CSV, "shape", df.shape)
    print("[info] columns:", list(df.columns))
    print("[info] head:")
    print(df.head())

    # We expect columns: 'System', 'P (s)', 'M (M☉)', 'x', 'δ', 'α_max (m^4)'
    try:
        mass_col = "M (M☉)"
        alpha_col = "α_max (m^4)"
        mass_vals = df[mass_col].astype(float).to_numpy()
        alpha_vals = df[alpha_col].astype(float).to_numpy()
    except KeyError as e:
        raise SystemExit(f"Expected columns 'M (M☉)' and 'α_max (m^4)' in {CSV}, got {list(df.columns)}") from e

    # Compute dimensionless hat_alpha = alpha_max / (GM/c^2)^4
    L = length_scale_m(mass_vals)  # meters
    hat_alpha = alpha_vals / (L**4)
    df = df.assign(hat_alpha=hat_alpha)

    print("[info] hat_alpha (dimensionless) values:")
    print(df[["System", "δ", "hat_alpha"]])

    # Build a label that distinguishes δ as well
    if "δ" in df.columns:
        labels = df["System"] + " (δ=" + df["δ"].astype(str) + ")"
    else:
        labels = df["System"]

    fig, ax = plt.subplots()
    ax.barh(labels, df["hat_alpha"])
    ax.set_xlabel(r"$\hat{\alpha}_{\max}$ (dimensionless)")
    ax.set_title(r"Pulsar timing bounds on $\hat{\alpha}$ (renormalized)")
    ax.grid(True, axis="x", ls=":", alpha=0.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
