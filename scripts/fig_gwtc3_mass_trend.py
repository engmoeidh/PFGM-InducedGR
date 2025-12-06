from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

JOINED = Path("results/gwtc3_mass_trend/gwtc3_mass_trend_joined.csv")
OUT_DELTA = Path("figures/gwtc3_delta_vs_X.png")
OUT_RESID = Path("figures/gwtc3_residuals_vs_M.png")


def choose_column(df, candidates):
    """Return the first column from `candidates` that exists in df, else raise."""
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"None of {candidates} found in columns {list(df.columns)}")


def weighted_fit_alpha(M_Msun, delta, sigma):
    """
    Weighted least-squares fit of delta = S * X with X = 1/(GM/c^2)^4,
    using the X_Mminus4 column already provided in the joined CSV.
    Here we fit S in delta = S X; you can map to alpha with any kappa_2.5 later.
    """
    # In the joined CSV we already have X in m^-4
    # We just treat X as given to keep this plotting script simple.
    # The caller passes the X array explicitly.
    X = M_Msun  # placeholder; we will not use this function directly.
    raise RuntimeError("This function is not intended to be used directly.")


def main():
    if not JOINED.exists():
        raise SystemExit(f"Missing {JOINED}; run gwtc3_fit_common_alpha.py first.")

    df = pd.read_csv(JOINED)
    print("[INFO] loaded", len(df), "rows from", JOINED)
    print("[INFO] columns:", list(df.columns))

    # Required structural columns
    X_col = "X_Mminus4"
    if X_col not in df.columns:
        raise SystemExit(f"{JOINED} missing required column {X_col!r}")

    # Try to locate the PN-test delta and sigma columns
    delta_col = choose_column(
        df,
        [
            "delta_phi_5l_median_eff",  # from our dchi5l summary
            "dchi5l_median",            # alternative naming
            "delta_phi_5l_median",      # from original mass table
        ],
    )

    sigma_col = "sigma_delta_5l_1sigma"
    if sigma_col not in df.columns:
        raise SystemExit(f"{JOINED} missing required column {sigma_col!r}")

    mass_col = "Mtot_det_Msun" if "Mtot_det_Msun" in df.columns else "Mtot_source_Msun"

    # Drop rows with missing values
    sel = df.dropna(subset=[X_col, delta_col, sigma_col, mass_col])
    print("[INFO] usable rows for fit:", len(sel))
    if sel.empty:
        raise SystemExit("No usable rows in joined CSV for GWTC-3 mass trend.")

    X = sel[X_col].to_numpy(dtype=float)
    delta = sel[delta_col].to_numpy(dtype=float)
    sigma = sel[sigma_col].to_numpy(dtype=float)
    M = sel[mass_col].to_numpy(dtype=float)

    # Weighted fit delta = S X
    w = 1.0 / (sigma**2)
    num = np.sum(w * X * delta)
    den = np.sum(w * X * X)
    S = num / den
    var_S = 1.0 / den
    sigma_S = np.sqrt(var_S)

    resid = delta - S * X
    chi2 = np.sum((resid / sigma) ** 2)
    dof = len(delta) - 1

    print(f"[INFO] best-fit S (delta = S X) = {S:.6e} +/- {sigma_S:.6e}")
    print(f"[INFO] chi^2/dof = {chi2:.2f} / {dof}")

    # === Figure 1: delta vs X with fit line ===
    fig1, ax1 = plt.subplots(figsize=(5.0, 4.0))
    ax1.errorbar(
        X,
        delta,
        yerr=sigma,
        fmt="o",
        ms=5,
        capsize=3,
        label="GWTC-3 PN tests",
    )
    xg = np.linspace(0.9 * X.min(), 1.1 * X.max(), 200)
    ax1.plot(xg, S * xg, label=rf"fit, S = {S:.2e}")
    ax1.axhline(0.0, color="k", ls=":", lw=0.8)

    ax1.set_xlabel(r"$X \equiv 1/(GM/c^2)^4\ [{\rm m}^{-4}]$")
    ax1.set_ylabel(r"$\delta\hat{\phi}_{5\ell}$")
    ax1.set_title("GWTC-3 2.5PN tail test: mass trend")
    ax1.grid(True, which="both", ls=":", alpha=0.5)
    ax1.legend(fontsize=8)

    fig1.tight_layout()
    OUT_DELTA.parent.mkdir(parents=True, exist_ok=True)
    fig1.savefig(OUT_DELTA, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT_DELTA}")

    # === Figure 2: residuals vs detector-frame mass ===
    fig2, ax2 = plt.subplots(figsize=(5.0, 4.0))
    ax2.errorbar(
        M,
        resid,
        yerr=sigma,
        fmt="o",
        ms=5,
        capsize=3,
    )
    ax2.axhline(0.0, color="k", ls=":", lw=0.8)
    ax2.set_xlabel(r"$M_{\rm tot}^{\rm(det)}\ [{\rm M}_\odot]$")
    ax2.set_ylabel(r"$\delta\hat{\phi}_{5\ell} - S X$")
    ax2.set_title("Residuals of common-$\\alpha$ fit (GWTC-3)")
    ax2.grid(True, which="both", ls=":", alpha=0.5)

    fig2.tight_layout()
    fig2.savefig(OUT_RESID, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT_RESID}")


if __name__ == "__main__":
    main()
