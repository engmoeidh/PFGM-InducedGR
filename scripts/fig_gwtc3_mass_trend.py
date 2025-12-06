"""
High-level GWTC-3 mass-trend figures for the induced-GR paper.

Inputs (from gwtc3_fit_common_alpha.py):
    results/gwtc3_mass_trend/gwtc3_mass_trend_joined.csv

Outputs (in figures/):
    gwtc3_alpha_max_v_mass_plot.png
    gwtc3_delta_vs_X.png
    gwtc3_residuals_vs_M.png
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RES  = ROOT / "results" / "gwtc3_mass_trend"
FIG  = ROOT / "figures"

JOINED = RES / "gwtc3_mass_trend_joined.csv"

# Physical constants (SI)
G     = 6.67430e-11
C     = 2.99792458e8
M_SUN = 1.98847e30


def gm_over_c2_m(m_msun: np.ndarray) -> np.ndarray:
    """GM/c^2 in metres for detector-frame mass in Msun."""
    m_msun = np.asarray(m_msun, dtype=float)
    return G * (m_msun * M_SUN) / (C ** 2)


def X_from_mass(m_msun: np.ndarray) -> np.ndarray:
    """X = 1 / (GM/c^2)^4 in SI (m^-4)."""
    L = gm_over_c2_m(m_msun)
    return 1.0 / (L ** 4)


def weighted_fit_alpha(M_Msun, delta, sigma, kappa_25: float = 1.0):
    """
    Fit delta = S * X with X = 1/(GM/c^2)^4, through origin, weighted by 1/sigma^2.

    Returns:
        alpha_hat, sigma_alpha, (ci68_lo, ci68_hi), (ci90_lo, ci90_hi), diagnostics
    where diagnostics = (X, resid, chi2, dof).
    """
    X = X_from_mass(M_Msun)
    delta = np.asarray(delta, dtype=float)
    sigma = np.asarray(sigma, dtype=float)

    w = 1.0 / (sigma ** 2)
    num = np.sum(w * X * delta)
    den = np.sum(w * X * X)
    S = num / den
    var_S = 1.0 / den
    sigma_S = np.sqrt(var_S)

    alpha_hat = S / kappa_25
    sigma_alpha = sigma_S / kappa_25
    ci68 = (alpha_hat - sigma_alpha, alpha_hat + sigma_alpha)
    ci90 = (alpha_hat - 1.64 * sigma_alpha, alpha_hat + 1.64 * sigma_alpha)

    resid = delta - S * X
    chi2 = np.sum((resid / sigma) ** 2)
    dof = max(len(delta) - 1, 1)

    return alpha_hat, sigma_alpha, ci68, ci90, (X, resid, chi2, dof)


def main():
    if not JOINED.exists():
        raise SystemExit(f"Missing {JOINED}; run gwtc3_fit_common_alpha.py first.")

    df = pd.read_csv(JOINED)
    print(f"[INFO] loaded {len(df)} rows from {JOINED}")

    # Keep only rows that have the PN-test info and mass
    need_cols = ["Mtot_det_Msun", "dchi5l_median", "sigma_delta_5l_1sigma"]
    missing = [c for c in need_cols if c not in df.columns]
    if missing:
        raise SystemExit(f"Joined CSV missing columns {missing}")

    sel = df.dropna(subset=need_cols)
    print(f"[INFO] using {len(sel)} events for plotting")

    M   = sel["Mtot_det_Msun"].to_numpy()
    d5l = sel["dchi5l_median"].to_numpy()
    sig = sel["sigma_delta_5l_1sigma"].to_numpy()
    X   = X_from_mass(M)

    # Refit alpha_hat to be sure we are consistent with the data at hand
    alpha_hat, sigma_alpha, ci68, ci90, (X_fit, resid, chi2, dof) = weighted_fit_alpha(M, d5l, sig)
    print(f"[INFO] alpha_hat [m^4] = {alpha_hat:.6e} ± {sigma_alpha:.6e} (68%)")
    print(f"[INFO] chi^2/dof = {chi2:.2f}/{dof}")

    # Per-event alpha_i = delta_i / X_i, with propagated errors
    alpha_i = d5l / X
    sigma_alpha_i = sig / X

    FIG.mkdir(parents=True, exist_ok=True)

    # 1) alpha_max vs mass
    plt.figure(figsize=(6, 4))
    plt.errorbar(
        M,
        alpha_i,
        yerr=sigma_alpha_i,
        fmt="o",
        color="C0",
        label="GWTC-3 events",
    )

    # best-fit band (±1σ in alpha_hat)
    M_grid = np.linspace(0.9 * M.min(), 1.1 * M.max(), 200)
    X_grid = X_from_mass(M_grid)
    y_fit  = alpha_hat
    # Plot as horizontal band because alpha_hat is common, not mass-dependent
    plt.axhline(alpha_hat, color="C1", ls="-", label=r"common $\hat{\alpha}$")
    plt.axhline(alpha_hat + sigma_alpha, color="C1", ls="--", lw=1, alpha=0.7)
    plt.axhline(alpha_hat - sigma_alpha, color="C1", ls="--", lw=1, alpha=0.7)

    plt.xlabel(r"$M_{\rm det}\ [{\rm M}_\odot]$")
    plt.ylabel(r"$\hat{\alpha}_i = \delta_{5\ell,i} / X_i\ [{\rm m}^4]$")
    plt.title(r"GWTC-3 PN mass trend: per-event $\hat{\alpha}_i$")
    plt.grid(True, which="both", ls=":")
    plt.legend()
    plt.tight_layout()
    out1 = FIG / "gwtc3_alpha_max_v_mass_plot.png"
    plt.savefig(out1, dpi=220)
    plt.close()
    print(f"[OK] wrote {out1}")

    # 2) delta vs X
    plt.figure(figsize=(6, 4))
    plt.errorbar(
        X,
        d5l,
        yerr=sig,
        fmt="o",
        color="C0",
        label="GWTC-3 events",
    )
    xg = np.linspace(0.9 * X.min(), 1.1 * X.max(), 200)
    plt.plot(xg, alpha_hat * xg, "C1-", label=r"fit $\delta_{5\ell} = \hat{\alpha} X$")
    plt.xlabel(r"$X \equiv 1/(GM/c^2)^4\ [{\rm m}^{-4}]$")
    plt.ylabel(r"$\hat{\delta}_{5\ell}$")
    plt.title(r"GWTC-3 PN mass trend: $\delta_{5\ell}$ vs $X$")
    plt.grid(True, which="both", ls=":")
    plt.legend()
    plt.tight_layout()
    out2 = FIG / "gwtc3_delta_vs_X.png"
    plt.savefig(out2, dpi=220)
    plt.close()
    print(f"[OK] wrote {out2}")

    # 3) residuals vs mass
    plt.figure(figsize=(6, 4))
    plt.errorbar(
        M,
        resid,
        yerr=sig,
        fmt="o",
        color="C0",
    )
    plt.axhline(0.0, color="k", ls="--", lw=1)
    plt.xlabel(r"$M_{\rm det}\ [{\rm M}_\odot]$")
    plt.ylabel(r"$\delta_{5\ell} - \hat{\alpha} X$")
    plt.title("GWTC-3 PN mass-trend residuals")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()
    out3 = FIG / "gwtc3_residuals_vs_M.png"
    plt.savefig(out3, dpi=220)
    plt.close()
    print(f"[OK] wrote {out3}")


if __name__ == "__main__":
    main()
