.PHONY: install run debug clean fclean lint lint-strict package

install:
	pip install uv
	uv sync
	python3 -m venv .venv

run:
	uv run python -m src config.json

debug:
	uv run python -m pdb -m src config.json

clean:
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build

package:
	uv run pyinstaller --noconfirm --clean pacman.spec
	cp INSTRUCTIONS.txt config.json dist/pacman/
	@echo "Build autonome pret dans dist/pacman/ (et dist/Pac-Man.app sur macOS)"

fclean: clean
	rm -rf .venv

MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

lint:
	uv run flake8 .
	uv run mypy . $(MYPY_FLAGS)

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
