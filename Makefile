SHELL := env PYTHON_VERSION=3.12 /bin/bash
.SILENT: install devinstall tools test run lint format precommit precommit-run
PYTHON_VERSION ?= 3.12

setup:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install:
	uv python pin $(PYTHON_VERSION)
	uv sync --no-dev

devinstall:
	uv python pin $(PYTHON_VERSION)
	uv sync --all-extras --dev
	@echo "Tip: run 'make precommit' to enable automatic linting on commit"

test:
	uv run pytest tests/ --ignore=tests/integration

run: 
	uv run python main.py

lint:
	uv run ruff check -q

format:
	uv run ruff format

# Developer tools:
#   make precommit       → installs git pre-commit hooks (one-time, per dev)
#   make precommit-run   → runs all pre-commit hooks on the entire repo
# These are optional but recommended for contributors.

precommit:
	uv run pre-commit install
	@echo "pre-commit hooks installed."

precommit-run:
	uv run pre-commit run --all-files

all: devinstall tools lint format test