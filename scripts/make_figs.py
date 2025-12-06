"""
Regenerate all core figures for the Induced-GR paper.

Right now this just calls the PN-suppression generator; you can
extend it to call the other fig_* scripts if you like.
"""
from fig_pn_suppression import main as make_pn_suppression

if __name__ == "__main__":
    make_pn_suppression()
