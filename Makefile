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
.PHONY: help install docs docs-serve notebooks clean

help:
	@echo "Available targets:"
	@echo "  install      Install Python dependencies from requirements.txt"
	@echo "  docs         Build static API documentation into docs/api/"
	@echo "  docs-serve   Start a live-reloading docs server on http://localhost:8080"
	@echo "  notebooks    Execute every notebook in-place (reproducibility check)"
	@echo "  clean        Remove __pycache__ and the generated docs"

install:
	$(PYTHON) -m pip install -r requirements.txt

docs:
	$(PYTHON) -m pdoc src --output-directory docs/api --math

docs-serve:
	$(PYTHON) -m pdoc src --math

notebooks:
	$(PYTHON) -c "import subprocess, sys; from pathlib import Path; [subprocess.check_call([sys.executable, '-m', 'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', str(nb)]) for nb in sorted(Path('notebooks').glob('*.ipynb'))]"

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in list(pathlib.Path('.').rglob('__pycache__')) + [pathlib.Path('docs/api'), pathlib.Path('.ipynb_checkpoints')]]"
