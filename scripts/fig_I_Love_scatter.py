from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CSV = Path("input/reference/I_Love_scatter.csv")
OUT = Path("figures/I_Love_scatter.png")

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}")
    df = pd.read_csv(CSV)
    print("[info] Loaded", CSV, "shape", df.shape)
    print("[info] columns:", list(df.columns))

    for col in ["alpha", "f_factor", "Ibar", "Lambdabar"]:
        if col not in df.columns:
            raise SystemExit(f"Column '{col}' missing from {CSV}")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["Ibar", "Lambdabar"])
    print("[info] after dropna:", df.shape)

    alphas = sorted(df["alpha"].unique())
    f_factors = sorted(df["f_factor"].unique())
    print("[info] unique alphas:", alphas)
    print("[info] unique f_factors:", f_factors)

    markers = ["o", "s", "^", "D", "v", "P", "X", "*"]
    marker_map = {ff: markers[i % len(markers)] for i, ff in enumerate(f_factors)}

    cmap = plt.get_cmap("viridis")
    if len(alphas) > 1:
        color_map = {a: cmap(i / (len(alphas) - 1)) for i, a in enumerate(alphas)}
    else:
        color_map = {alphas[0]: cmap(0.5)}

    fig, ax = plt.subplots(figsize=(5,4))

    for a in alphas:
        sub_a = df[df["alpha"] == a]
        for ff in f_factors:
            sub = sub_a[sub_a["f_factor"] == ff]
            if sub.empty:
                continue
            label = f"alpha={a}, f={ff}"
            ax.loglog(
                sub["Lambdabar"],
                sub["Ibar"],
                marker=marker_map[ff],
                linestyle="none",
                color=color_map[a],
                label=label,
            )

    ax.set_xlabel("Lambdabar")
    ax.set_ylabel("Ibar")
    ax.set_title("I–Love scatter (selected configurations)")
    ax.grid(True, which="both", linestyle=":", alpha=0.5)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize="x-small", ncol=1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=220)
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
