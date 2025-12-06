from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

CSV = Path("input/reference/I_Love_Q_panel_finalized.csv")
OUT = Path("figures/I_Love_Q_panel_finalized.png")


def main() -> None:
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV}")

    df = pd.read_csv(CSV)
    print("[info] Loaded", CSV, "shape", df.shape)
    print("[info] columns:", list(df.columns))

    df = df.replace([np.inf, -np.inf], np.nan)

    # Keep only converged matches
    if "match_status" in df.columns:
        df = df[df["match_status"].astype(str).str.strip() == "ok"]
    print("[info] after match_status filter:", df.shape)

    # Require basic columns
    for col in ["Ibar", "Qbar", "Lambdabar", "alpha", "f_factor"]:
        if col not in df.columns:
            raise SystemExit(f"{CSV} missing required column {col!r}")

    # Drop rows with NaN in core columns
    df = df.dropna(subset=["Ibar", "Qbar", "Lambdabar", "alpha", "f_factor"])
    print("[info] after dropna on core cols:", df.shape)

    # Remove zeros and non-finite entries
    mask = (
        np.isfinite(df["Ibar"]) & np.isfinite(df["Qbar"]) & np.isfinite(df["Lambdabar"])
        & (df["Ibar"] != 0.0) & (df["Qbar"] != 0.0) & (df["Lambdabar"] != 0.0)
    )
    df = df[mask]
    print("[info] after >0 & finite cuts:", df.shape)

    if df.empty:
        print("[ERROR] No usable rows after cleaning; inspect the CSV.")
        return

    alphas = np.sort(df["alpha"].unique())
    fvals = np.sort(df["f_factor"].unique())
    print("[info] unique alphas:", alphas)
    print("[info] unique f_factor:", fvals)

    fig, (ax_IL, ax_QL, ax_IQ) = plt.subplots(1, 3, figsize=(12, 4))

    color_list = ["tab:blue", "tab:orange", "tab:green", "tab:red",
                  "tab:purple", "tab:brown", "tab:pink", "tab:gray"]
    color_map = {a: color_list[i % len(color_list)] for i, a in enumerate(alphas)}

    marker_list = ["o", "s", "^", "D", "P", "X", "v", "*"]
    marker_map = {f: marker_list[i % len(marker_list)] for i, f in enumerate(fvals)}

    # Scatter each point
    for _, row in df.iterrows():
        a = float(row["alpha"])
        f = float(row["f_factor"])
        I = float(row["Ibar"])
        Q = float(row["Qbar"])
        L = float(row["Lambdabar"])

        color = color_map[a]
        marker = marker_map[f]

        # I–Love
        ax_IL.scatter(
            np.log10(abs(L)),
            np.log10(abs(I)),
            c=[color],
            marker=marker,
            s=38,
        )

        # Q–Love: sign(Q) encoded by fill / hollow
        face = color if Q > 0 else "none"
        edge = color
        ax_QL.scatter(
            np.log10(abs(L)),
            np.log10(abs(Q)),
            facecolors=face,
            edgecolors=edge,
            marker=marker,
            s=38,
        )

        # I–Q
        face = color if Q > 0 else "none"
        edge = color
        ax_IQ.scatter(
            np.log10(abs(I)),
            np.log10(abs(Q)),
            facecolors=face,
            edgecolors=edge,
            marker=marker,
            s=38,
        )

    # Labels / titles
    ax_IL.set_xlabel(r"$\log_{10}\bar{\Lambda}$")
    ax_IL.set_ylabel(r"$\log_{10}\bar I$")
    ax_IL.set_title("I--Love (PFGM)")

    ax_QL.set_xlabel(r"$\log_{10}\bar{\Lambda}$")
    ax_QL.set_ylabel(r"$\log_{10}|\bar Q|$")
    ax_QL.set_title(r"$\bar Q$--Love (PFGM)")

    ax_IQ.set_xlabel(r"$\log_{10}\bar I$")
    ax_IQ.set_ylabel(r"$\log_{10}|\bar Q|$")
    ax_IQ.set_title(r"$\bar I$--$\bar Q$")

    for ax in (ax_IL, ax_QL, ax_IQ):
        ax.grid(True, linestyle=":", alpha=0.5)

    # Legends
    alpha_handles = [
        Line2D(
            [0], [0],
            marker="o", linestyle="",
            markerfacecolor=color_map[a],
            markeredgecolor=color_map[a],
            label=rf"$\alpha={a:g}$",
        )
        for a in alphas
    ]
    f_handles = [
        Line2D(
            [0], [0],
            marker=marker_map[f],
            linestyle="",
            color="k",
            label=rf"$f_\mathrm{{match}}={f:g}$",
        )
        for f in fvals
    ]
    sign_handles = [
        Line2D([0], [0], marker="o", linestyle="",
               markerfacecolor="k", markeredgecolor="k", label="Q > 0"),
        Line2D([0], [0], marker="o", linestyle="",
               markerfacecolor="none", markeredgecolor="k", label="Q < 0"),
    ]

    ax_IL.legend(handles=alpha_handles, title=r"$\alpha$", fontsize=8)
    ax_QL.legend(handles=f_handles, title=r"$f_\mathrm{match}$",
                 fontsize=8, loc="lower right")
    ax_IQ.legend(handles=sign_handles, title="sign(Q)", fontsize=8)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT}")


if __name__ == "__main__":
    main()
