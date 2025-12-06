from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CSV = Path("input/reference/Qbar_option1_provisional.csv")
OUT = Path("figures/Qbar_option1_provisional.png")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}")
    df = pd.read_csv(CSV)
    print("[info] Loaded", CSV, "shape", df.shape)
    print("[info] columns:", list(df.columns))

    for col in ["alpha", "f_factor", "Qbar_provisional"]:
        if col not in df.columns:
            raise SystemExit(f"Column '{col}' missing from {CSV}")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["Qbar_provisional"])
    print("[info] after dropna:", df.shape)

    alphas = sorted(df["alpha"].unique())
    f_factors = sorted(df["f_factor"].unique())
    print("[info] unique alphas:", alphas)
    print("[info] unique f_factors:", f_factors)

    cmap = plt.get_cmap("plasma")
    if len(alphas) > 1:
        color_map = {a: cmap(i / (len(alphas) - 1)) for i, a in enumerate(alphas)}
    else:
        color_map = {alphas[0]: cmap(0.5)}

    fig, ax = plt.subplots(figsize=(5,4))

    for a in alphas:
        sub = df[df["alpha"] == a].sort_values("f_factor")
        if sub.empty:
            continue
        ax.plot(
            sub["f_factor"],
            sub["Qbar_provisional"],
            marker="o",
            linestyle="-",
            color=color_map[a],
            label=f"alpha={a}",
        )

    ax.set_xlabel("f_factor")
    ax.set_ylabel("Qbar_provisional")
    ax.set_title("Q̄ vs f_factor (option 1 provisional)")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(fontsize="small")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=220)
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
