from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CSV = Path("data/processed/alpha_max_vs_x_mass_dependent.csv")
PNG = Path("figures/alpha_max_vs_x.png")
PDF = Path("figures/alpha_max_vs_x.pdf")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}; run: python scripts/generate_data.py")
    df = pd.read_csv(CSV)

    # group by mass (legend), separate curves by delta if present
    fig, ax = plt.subplots()
    if "delta" in df.columns:
        for (m,d), sub in df.groupby(["mass","delta"]):
            ax.plot(sub["X"], sub["alpha_max"], marker="o", linestyle="-", label=f"M={m} Msun, δ={d}")
    else:
        for m, sub in df.groupby("mass"):
            ax.plot(sub["X"], sub["alpha_max"], marker="o", linestyle="-", label=f"M={m} Msun")

    ax.set_xlabel("x ≡ (v/c)^2")
    ax.set_ylabel(r"$\alpha_{\max}$")
    ax.set_title(r"$\alpha_{\max}(x)$ (normalized)")
    ax.grid(True, ls=":")
    ax.legend(ncol=1, fontsize="small")

    PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PNG, dpi=220, bbox_inches="tight")
    fig.savefig(PDF, bbox_inches="tight")
    print(f"[ok] Wrote {PNG} and {PDF}")

if __name__ == "__main__":
    main()
