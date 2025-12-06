from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path("figures/pn_suppression.png")

# Physical constants (SI)
c = 2.99792458e8  # m/s

def k_from_f(f_hz: np.ndarray) -> np.ndarray:
    """
    Gravitational-wave wavenumber for the dominant mode.
    For our purposes k ~ 2*pi*f/c is sufficient.
    """
    return 2.0 * np.pi * f_hz / c

def main():
    # LIGO/Virgo/KAGRA band
    f = np.logspace(1, 3, 200)  # 10–1000 Hz

    # Representative quadratic-gravity ranges \ell_2
    ell2_list = [3e5, 1e6, 3e6]  # meters (300 km, 1000 km, 3000 km)

    k = k_from_f(f)
    fig, ax = plt.subplots()

    for ell2 in ell2_list:
        eps = (ell2 * k) ** 2
        label = rf"$\ell_2 = {ell2/1e3:.0f}\,\mathrm{{km}}$"
        ax.loglog(f, eps, label=label)

    # Rough region where |delta_hat_phi_5ℓ| ~ (ell_2 k)^2 ≲ 0.1
    ax.axhspan(1e-3, 1e-1, color="0.9", alpha=0.5,
               label=r"$10^{-3} \lesssim (\ell_2 k)^2 \lesssim 10^{-1}$")
    ax.axhline(1e-1, ls="--", color="k", lw=0.8)
    ax.text(11.0, 1.4e-1,
            r"$|\delta\hat\phi_{5\ell}| \sim (\ell_2 k)^2 \lesssim 0.1$",
            fontsize=8, va="bottom")

    ax.set_xlabel(r"GW frequency $f$ [Hz]")
    ax.set_ylabel(r"$(\ell_2 k)^2 \simeq (\ell_2\,2\pi f/c)^2$")
    ax.set_title(r"EFT suppression factor $(\ell_2 k)^2$ in the PN sector")
    ax.grid(True, which="both", ls=":")
    ax.legend(fontsize=8)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")
    print(f"[ok] Wrote {OUT}")

if __name__ == "__main__":
    main()
