# SmallWorld

## Overview

This is a course project for **Modelitzacio i Simulacio** (MatCAD, UAB, 2025-2026). The project studies the **Watts-Strogatz small-world model** by building the standard reference networks, comparing their average path length `L` and clustering coefficient `C` as the rewiring parameter `beta` changes, and simulating random walks to estimate **mixing time** and **cover time**. The work ends with a short comparison against a real network.

For a quick orientation inside this README:

- [Reading Guide](#reading-guide)
- [Repository Structure](#repository-structure)
- [Running The Project](#running-the-project)
- [Documentation](#documentation)
- [Tests](#tests)

The nicest way to see the project is in the browser through the local documentation website, because that view is cleaner, more visual, and includes interactive exploration. The notebooks are still very useful, but mainly as a guided reading path that shows step by step how the ideas are developed and how the results are obtained. In that sense, the browser is the best place to look at the final presentation, while the notebooks are the best place to follow the reasoning.

## Reading Guide

If one wants a simple path to understand how the project works without reading everything in detail, the most pleasant option is to start by opening the local documentation website in the browser and then use notebooks `02` and `03` as the reading backbone. Notebook `01_visualise_networks.ipynb` introduces the graph constructions. Notebook `02_small_world_window.ipynb` shows the core of the small-world phenomenon, and notebook `03_random_walks.ipynb` explains the random-walk part and its interpretation. Notebook `04_real_network.ipynb` is a final extension to a real network. If notebooks `02` and `03` are clear and coherent, then the central part of the assignment is already visible.

The main expected conclusion is that the Watts-Strogatz network preserves a relatively high clustering coefficient, like the regular graph, while also achieving much shorter effective distances and faster exploration properties. That combination is the main signature of the small-world phenomenon and the most important thing to check.

## Repository Structure

The repository is organized as follows:

```text
SmallWorld/
|-- README.md
|-- LICENSE
|-- Makefile
|-- requirements.txt
|-- pytest.ini
|-- mkdocs.yml
|-- src/
|   `-- smallworld/
|       |-- __init__.py
|       |-- networks.py
|       |-- networks_nx.py
|       |-- calculate_metrics.py
|       |-- simulation.py
|       |-- plotting.py
|       |-- visualization.py
|       |-- real_network.py
|       `-- templates/
|-- notebooks/
|   |-- 01_visualise_networks.ipynb
|   |-- 02_small_world_window.ipynb
|   |-- 03_random_walks.ipynb
|   `-- 04_real_network.ipynb
|-- docs/
|   |-- index.md
|   |-- theory.md
|   |-- explore.md
|   |-- real_network.md
|   |-- api/
|   |-- javascripts/
|   `-- examples/
|-- scripts/
|   `-- build_examples.py
|-- tests/
|   |-- test_unit_calculate_metrics.py
|   `-- test_unit_simulation.py
|-- data/
|   |-- metrics_analytics_data.json
|   `-- facebook_cache.json
`-- figures/
```

The `docs/` folder is the most presentation-friendly part of the repository, because it is what gets rendered in the browser. The `notebooks/` folder is the clearest place to follow the development step by step. The `src/smallworld/` folder contains the reusable implementation, and `tests/` contains the unit checks for the most important pieces.

## Running The Project

Python **3.10+** is recommended. A simple setup is:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

After that, the project can be viewed in two natural ways. The most visual one is to launch the documentation website locally and open it in the browser. The most guided one is to open the notebooks in **VS Code** or with **Jupyter Notebook**.

## Documentation

The folder `docs/` contains a small documentation website and is the best place to see the project in a clean and visual format. It is especially useful for browsing the results comfortably in the browser and for using the interactive views. The most useful pages are `docs/index.md` for the project overview, `docs/theory.md` for the model and metrics, `docs/explore.md` for interactive exploration, and `docs/real_network.md` for the final comparison.

The documentation is also available online:

https://natansisoev.github.io/SmallWorld/

To open that documentation locally, the easiest option is:

```bash
make install
make docs-serve
```

Then open `http://localhost:8000` in the browser. If `make` is not available, the equivalent commands are:

```bash
pip install -r requirements.txt
python -m mkdocs serve
```

## Tests

If you want to verify the internal consistency of the code, you can run:

```bash
pytest
```

This is optional for correction, but it is a quick technical check.

## Authors

Lluis Gay, Sergi Prats, Ferran Villarta and Natan Sisoev.
