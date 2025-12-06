from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Physical constants
G = 6.67430e-11
c = 299792458.0
M_SUN = 1.98847e30

def GM_over_c2_m(M_Msun: np.ndarray) -> np.ndarray:
    """Schwarzschild length GM/c^2 in meters for detector-frame mass in Msun."""
    return G * (M_Msun * M_SUN) / (c**2)

def X_from_mass(M_Msun: np.ndarray) -> np.ndarray:
    """X ≡ 1 / (GM/c^2)^4 in m^{-4}."""
    L = GM_over_c2_m(M_Msun)
    return 1.0 / (L**4)

def weighted_fit_alpha(M_Msun, delta, sigma, kappa_25: float = 1.0):
    """
    Fit delta_5l = S * X with X = 1/(GM/c^2)^4, forcing intercept=0.

    Returns alpha_hat (m^4) where S = kappa_2.5 * alpha_hat, and diagnostics.
    """
    M_Msun = np.asarray(M_Msun, dtype=float)
    delta = np.asarray(delta, dtype=float)
    sigma = np.asarray(sigma, dtype=float)

    X = X_from_mass(M_Msun)
    w = 1.0 / (sigma**2)

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
    chi2 = np.sum((resid / sigma)**2)
    dof = delta.size - 1

    return alpha_hat, sigma_alpha, ci68, ci90, (X, resid, chi2, dof)

def main():
    if len(sys.argv) != 4:
        print("Usage: python gwtc3_fit_common_alpha.py "
              "mass_table.csv par_dchi5l_summary_gwtc3.csv out_prefix")
        sys.exit(1)

    mass_table_csv = Path(sys.argv[1])
    dchi_summary_csv = Path(sys.argv[2])
    out_prefix = Path(sys.argv[3])

    if not mass_table_csv.exists():
        print(f"Missing mass table: {mass_table_csv}")
        sys.exit(1)
    if not dchi_summary_csv.exists():
        print(f"Missing dchi5l summary: {dchi_summary_csv}")
        sys.exit(1)

    print(f"[INFO] reading mass table: {mass_table_csv}")
    df_mass = pd.read_csv(mass_table_csv)
    print("[INFO] mass table shape:", df_mass.shape)
    print("[INFO] mass columns:", list(df_mass.columns))

    print(f"[INFO] reading dchi5l summary: {dchi_summary_csv}")
    df_dchi = pd.read_csv(dchi_summary_csv)
    print("[INFO] dchi5l summary shape:", df_dchi.shape)
    print("[INFO] dchi columns:", list(df_dchi.columns))

    # Normalise mass table event id
    if "event" in df_mass.columns and "event_id" not in df_mass.columns:
        df_mass = df_mass.rename(columns={"event": "event_id"})

    required = {
        "event_id",
        "delta_phi_5l_median",
        "delta_phi_5l_90pc_low",
        "delta_phi_5l_90pc_high",
    }
    missing = required - set(df_dchi.columns)
    if missing:
        print(f"[ERROR] dchi5l summary missing columns: {missing}")
        sys.exit(1)

    # Merge: keep delta_phi_5l_* from df_dchi, but mass table already has NaN
    cols_keep = [
        "event_id",
        "delta_phi_5l_median",
        "delta_phi_5l_90pc_low",
        "delta_phi_5l_90pc_high",
    ]
    m = df_mass.merge(df_dchi[cols_keep], on="event_id", how="left", suffixes=("", "_from_par"))

    # Build effective median/low/high columns, preferring *_from_par if present
    for base in ["delta_phi_5l_median", "delta_phi_5l_90pc_low", "delta_phi_5l_90pc_high"]:
        par_col = base + "_from_par"
        if par_col in m.columns:
            m[base + "_eff"] = m[par_col].where(m[par_col].notna(), m[base])
        else:
            m[base + "_eff"] = m[base]

    # Compute sigma from 90% width: sigma ≈ (high - low) / (2 * 1.64)
    width90 = (m["delta_phi_5l_90pc_high_eff"] - m["delta_phi_5l_90pc_low_eff"]).astype(float)
    m["sigma_delta_5l_1sigma"] = width90 / (2.0 * 1.64)

    # Select rows with PN-test info
    sel = m.dropna(subset=["delta_phi_5l_median_eff", "sigma_delta_5l_1sigma"])
    print(f"[INFO] PN-test events with usable posteriors: {len(sel)}")

    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    # If nothing usable, still write joined + report but skip fit
    if sel.empty:
        joined_csv = out_prefix.with_name(out_prefix.name + "_mass_trend_joined.csv")
        m.to_csv(joined_csv, index=False)
        print(f"[WARN] No PN-test events with usable posteriors; wrote {joined_csv} and empty report.")

        report_path = out_prefix.with_name(out_prefix.name + "_fit_report.txt")
        with report_path.open("w") as f:
            f.write("No PN-test events with usable posteriors; check inputs.\n")
        return

    # For Induced-GR we use kappa_2.5 = 1
    kappa_25 = 1.0
    alpha_hat, sigma_alpha, ci68, ci90, diag = weighted_fit_alpha(
        sel["Mtot_det_Msun"].values,
        sel["delta_phi_5l_median_eff"].values,
        sel["sigma_delta_5l_1sigma"].values,
        kappa_25=kappa_25,
    )
    X, resid, chi2, dof = diag

    # Save joined CSV
    joined_csv = out_prefix.with_name(out_prefix.name + "_mass_trend_joined.csv")
    m.to_csv(joined_csv, index=False)
    print(f"[INFO] wrote joined table: {joined_csv}")

    # Save report
    report_path = out_prefix.with_name(out_prefix.name + "_fit_report.txt")
    with report_path.open("w") as f:
        f.write(f"alpha_hat [m^4] = {alpha_hat:.6e}\n")
        f.write(f"sigma_alpha [m^4] = {sigma_alpha:.6e}\n")
        f.write(f"68% CI: [{ci68[0]:.6e}, {ci68[1]:.6e}]\n")
        f.write(f"90% CI: [{ci90[0]:.6e}, {ci90[1]:.6e}]\n")
        f.write(f"chi^2 / dof = {chi2:.2f} / {dof}\n")
        f.write(f"kappa_2.5 used = {kappa_25:.3f}\n")
        f.write("\nNotes: detector-frame masses, X = 1/(GM/c^2)^4.\n")
    print(f"[INFO] wrote fit report: {report_path}")

    # Plots (under results/gwtc3_mass_trend)
    fig1 = out_prefix.with_name(out_prefix.name + "_delta_vs_X.png")
    plt.figure(figsize=(6, 4))
    plt.errorbar(
        X,
        sel["delta_phi_5l_median_eff"].values,
        yerr=sel["sigma_delta_5l_1sigma"].values,
        fmt="o",
        label="GWTC-3 events",
    )
    xg = np.linspace(0.9 * X.min(), 1.1 * X.max(), 200)
    plt.plot(
        xg,
        (alpha_hat * kappa_25) * xg,
        label=r"fit: $\delta_{5\ell} = \kappa_{2.5}\,\alpha\,X$",
    )
    plt.xlabel(r"$X \equiv 1/(GM/c^2)^4\ [{\rm m}^{-4}]$")
    plt.ylabel(r"$\delta\hat{\phi}_{5\ell}$")
    plt.title("Mass trend: $\delta_{5\ell}$ vs $X$ (GWTC-3)")
    plt.grid(True, which="both", ls=":")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig1, dpi=200)
    plt.close()
    print(f"[INFO] wrote {fig1}")

    fig2 = out_prefix.with_name(out_prefix.name + "_residuals_vs_M.png")
    plt.figure(figsize=(6, 4))
    plt.errorbar(
        sel["Mtot_det_Msun"].values,
        resid,
        yerr=sel["sigma_delta_5l_1sigma"].values,
        fmt="o",
    )
    plt.axhline(0.0, linestyle="--", color="k", linewidth=1)
    plt.xlabel(r"Total mass $M_{\rm tot}$ [M$_\odot$] (detector-frame)")
    plt.ylabel(r"Residual $\delta_{5\ell} - \kappa_{2.5}\,\alpha X$")
    plt.title("Residuals of common-alpha fit (GWTC-3)")
    plt.grid(True, which="both", ls=":")
    plt.tight_layout()
    plt.savefig(fig2, dpi=200)
    plt.close()
    print(f"[INFO] wrote {fig2}")

if __name__ == "__main__":
    main()
