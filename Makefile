PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: setup test lint format demo clean

setup:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest --cov=autonomous_dataops --cov-report=term-missing --cov-fail-under=80

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m mypy src

format:
	ruff format src tests
	ruff check --fix src tests

demo:
	mkdir -p out
	$(PYTHON) -m autonomous_dataops.cli run examples/sample_input.json --output out/result.json
	@echo "Wrote out/result.json"

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov out build dist *.egg-info
