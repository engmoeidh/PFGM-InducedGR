.PHONY: setup test data figures paper clean

setup:
\tpython -m pip install -r requirements.txt

test:
\tpytest -q

data:
\tpython scripts/generate_data.py

figures: data
\tpython scripts/make_figs.py
\tpython scripts/fig_alpha_max_vs_x.py

paper:
\tcd paper && latexmk -pdf main.tex

clean:
\trm -rf results/logs/* figures/* paper/*.aux paper/*.log paper/*.out paper/*.bbl paper/*.blg paper/*.toc paper/*.synctex.gz
