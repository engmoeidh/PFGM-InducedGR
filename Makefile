.PHONY: setup test figures paper clean
setup:
\tpython -m pip install -r requirements.txt
test:
\tpytest -q
figures:
\tpython scripts/make_figs.py
paper:
\tcd paper && latexmk -pdf main.tex
clean:
\trm -rf results/logs/* figures/* paper/.aux paper/.log paper/.out paper/.bbl paper/.blg paper/.toc paper/*.synctex.gz
