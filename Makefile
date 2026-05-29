.PHONY: install test lint typecheck build clean publish-test publish

install:
	pip install -e ".[dev]"

test:
	PYTHONPATH=src:. pytest -v

lint:
	ruff check src tests

typecheck:
	mypy src

build:
	python -m build

clean:
	rm -rf dist build *.egg-info src/*.egg-info __pycache__ .pytest_cache .mypy_cache

publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine upload dist/*
