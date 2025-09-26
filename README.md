# PFGM-InducedGR — Reproducible bundle

This repository is a minimal, end-to-end, *reproducible* bundle for the
Proto-Field Gravity Model (PFGM) and its Induced GR development.

## Quick start (Windows Git Bash)
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
pytest -q
python scripts/make_figs.py

## Layout
- input/   (not versioned): raw or private data you don't upload
- data/    (small, versioned): derived CSVs used by figures/tables
- scripts/ pipelines to go input → data → figures
- figures/ final plots used by the paper
- results/ logs, tables
- tests/   unit/smoke tests
- paper/   LaTeX manuscript (CQG-ready)
