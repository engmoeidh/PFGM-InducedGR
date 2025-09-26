"""
Generate an example figure into figures/.
Replace/extend with your real pipelines.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

Path("figures").mkdir(parents=True, exist_ok=True)

x = np.logspace(-10, -1, 200)
y = np.ones_like(x)
fig, ax = plt.subplots()
ax.semilogx(x, y)
ax.set_xlabel("x = (v/c)^2")
ax.set_ylabel("reference")
ax.set_title("PN suppression — placeholder")
ax.grid(True, which="both", ls=":")
fig.savefig("figures/pn_suppression.png", dpi=180, bbox_inches="tight")
print("Wrote figures/pn_suppression.png")
