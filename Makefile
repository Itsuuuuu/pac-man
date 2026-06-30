.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python -m src config.json

debug:
	uv run python -m pdb -m src

clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf .mypycache
	rm -rf .pytest_cache

fclean:
	rm -rf .venv

lint:
	uv run flake8 src/
	uv run mypy src/ --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 	src/
	uv run mypy	  src/ --strict
