.PHONY: install run debug clean lint lint-strict

install:
	uv sync
	python3 -m venv .venv

run:
	uv run python -m src config.json

debug:
	uv run python -m pdb -m src config.json

clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf .mypycache
	rm -rf .pytest_cache

fclean:
	rm -rf .venv

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

lint:
	uv run flake8 src/
	uv run mypy src/ $(MYPY_FLAGS)

lint-strict:
	uv run flake8 src/
	uv run mypy src/ --strict $(MYPY_FLAGS)
