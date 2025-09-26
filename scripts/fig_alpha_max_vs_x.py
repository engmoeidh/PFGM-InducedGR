from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CSV = Path("data/processed/alpha_max_vs_x_mass_dependent.csv")
PNG = Path("figures/alpha_max_vs_x.png")
PDF = Path("figures/alpha_max_vs_x.pdf")

# constants (SI)
G   = 6.67430e-11
c   = 2.99792458e8
Msun= 1.98847e30

def length_scale_m(mass_msun: float) -> float:
    """(GM/c^2) in meters for a given mass in Msun."""
    return G*(mass_msun*Msun)/c**2

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}; run: python scripts/generate_data.py")
    df = pd.read_csv(CSV)

    # Expect normalized long schema: X, alpha_max, mass, (optional) delta
    need = {"X","alpha_max","mass"}
    if not need.issubset(df.columns):
        raise SystemExit(f"{CSV} missing required columns {need}, has {list(df.columns)}")

    # Compute dimensionless hat_alpha = alpha_max / (GM/c^2)^4 for each row
    L = length_scale_m(df["mass"].astype(float).values)  # meters
    hat_alpha = df["alpha_max"].astype(float).values / (L**4)
    df = df.assign(hat_alpha=hat_alpha)

    # Plot: group by mass, separate by delta if present; use log-y for dynamic range
    fig, ax = plt.subplots()
    if "delta" in df.columns:
        for (m,d), sub in df.groupby(["mass","delta"]):
            sub = sub.sort_values("X")
            ax.semilogy(sub["X"], sub["hat_alpha"], marker="o", linestyle="-", label=f"M={m} Msun, δ={d}")
    else:
        for m, sub in df.groupby("mass"):
            sub = sub.sort_values("X")
            ax.semilogy(sub["X"], sub["hat_alpha"], marker="o", linestyle="-", label=f"M={m} Msun")

    ax.set_xlabel("x ≡ (v/c)^2")
    ax.set_ylabel(r"$\hat{\alpha}_{\max}$")
    ax.set_title(r"$\hat{\alpha}_{\max}(x)$ (dimensionless)")
    ax.grid(True, which="both", ls=":")
    ax.legend(ncol=1, fontsize="small")

    PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PNG, dpi=220, bbox_inches="tight")
    fig.savefig(PDF, bbox_inches="tight")
    print(f"[ok] Wrote {PNG} and {PDF}")

if __name__ == "__main__":
    main()
