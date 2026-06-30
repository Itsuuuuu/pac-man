.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	un run python -m src

debug:
	ub run python -m pdb -m src

clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf .mypycache
	rm -rf .pytest_cache

fclean:
	rm -rf .venv

lint:
	uv run flake8 --warn-return-any --warnunused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	uv run mypy		// a compélter

lint-strict:
	uv run flake8 	// a compléter
	uv run mypy	  src/ --strict
