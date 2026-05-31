# SmallWorld — common tasks
#
# Usage:  make <target>
# Run `make` or `make help` to list the available targets.
#
# Windows note: GNU make is not bundled with PowerShell. Install via
#   choco install make
# or just copy the commands below and run them manually.

PYTHON ?= python

.DEFAULT_GOAL := help
.PHONY: help install docs docs-serve examples precompute notebooks clean

help:
	@echo "Available targets:"
	@echo "  install      Install Python dependencies from requirements.txt"
	@echo "  examples     Regenerate HTML examples (fast: reads data/ cache)"
	@echo "  precompute   Recompute slow data caches (~15 min). Commit data/*.json after."
	@echo "  docs         Build the static documentation site into site/"
	@echo "  docs-serve   Start a live-reloading docs server on http://localhost:8000"
	@echo "  notebooks    Execute every notebook in-place (reproducibility check)"
	@echo "  clean        Remove __pycache__, the built site, and generated examples"

install:
	$(PYTHON) -m pip install -r requirements.txt

examples:
	$(PYTHON) scripts/build_examples.py

precompute:
	$(PYTHON) -c "from pathlib import Path; [p.unlink() for p in [Path('data/metrics_analytics_data.json'), Path('data/facebook_cache.json')] if p.exists()]"
	$(PYTHON) scripts/build_examples.py

docs: examples
	$(PYTHON) -m mkdocs build --strict

docs-serve: examples
	$(PYTHON) -m mkdocs serve

notebooks:
	$(PYTHON) -c "import subprocess, sys; from pathlib import Path; [subprocess.check_call([sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', str(nb)]) for nb in sorted(Path('notebooks').glob('*.ipynb'))]"

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in list(pathlib.Path('.').rglob('__pycache__')) + [pathlib.Path('site'), pathlib.Path('docs/examples'), pathlib.Path('.ipynb_checkpoints')]]"
