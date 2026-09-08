.PHONY: install dev test lint check clean run serve eval

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src/ tests/

check: lint test

run:
	forgemind run "What is (12 + 8) * 3? Reply with just the number."

serve:
	forgemind serve

eval:
	forgemind evaluate

clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache .forgemind
	find . -name "__pycache__" -type d -exec rm -rf {} +
