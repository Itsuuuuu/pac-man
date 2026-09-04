# Project Analysis and Technical Choices

## Problem analysis

The subject asks for a complete Pac-Man in Python with four hard constraints
that shaped the whole design:

1. **The maze comes from someone else's package.** We do not control the maze
   format, so the engine must adapt to `mazegenerator`'s output, not the
   reverse.
2. **No crash is tolerated.** Any unhandled exception during the defence means
   a non-functional project, so error handling is a feature, not a detail.
3. **The configuration is changed by the reviewer during the defence.** The
   game must survive values we have never tested.
4. **`flake8` and `mypy` must be clean.** Type hints and style are part of the
   deliverable, not an afterthought.

## Choices

### C1 — Strict separation between engine and UI

`src/` holds the game logic, `src/ui/` holds everything Pygame. The engine
never imports from the UI.

*Why:* the game rules can be tested and reasoned about without opening a
window, and the rendering can be rewritten without touching the rules.
*Cost:* the UI has to re-read engine state every frame instead of being
notified of changes.

### C2 — Tile-based logic, interpolated rendering

The engine moves entities one grid cell at a time on its own timer; the
renderer interpolates between the previous and current cell to draw smooth
movement at 60 FPS.

*Why:* collision and pathfinding stay exact integer comparisons — no
floating-point edge cases — while the player still sees fluid motion.
*Cost:* the renderer needs a progress ratio (`move_progress()`), and the
entities must remember their previous position purely for display.

### C3 — Walls stored as a bitmask per tile

Each `Tile` encodes its four walls in one integer (N=1, E=2, S=4, W=8), which
is also the format `mazegenerator` returns.

*Why:* a wall check is a single bit test, and no conversion layer is needed
between the generator's output and our map.
*Cost:* less readable than four booleans; mitigated by `Tile.has_wall()`.

### C4 — One pathfinding algorithm, four personalities

All four ghosts run the same BFS in `ghost_algo.py`. What differs is only the
target cell each ghost asks for, in `Ghost.get_target()`.

*Why:* the maze is an unweighted grid, so BFS is already optimal — A* would
add a heuristic for no gain at this size. One algorithm means one place to
debug, and ghost behaviour becomes a data question rather than a code
question.
*Cost:* behaviours that are not expressible as "shortest path to a cell"
(such as the original game's scatter mode) do not fit the model.

### C5 — Pydantic for configuration validation

`config_parser.py` declares the config as Pydantic models with per-field
constraints instead of hand-written checks.

*Why:* the constraints are declared once and enforced everywhere, unknown keys
are ignored for free, and the parsed config is a typed object that `mypy`
understands.
*Cost:* an external dependency, and the default failure mode is an exception
with a developer-facing message — which is why the clamping behaviour required
by the subject (V.3) is still on the backlog.

### C6 — Configuration-driven difficulty

Speeds, maze size, pacgum count, level duration and power-pellet duration are
per-level entries in `config.json`, read through `GameConfig.level_params()`.

*Why:* the reviewer can retune the game without touching Python, which is
exactly what the defence asks for.
*Cost:* the last level repeats indefinitely, which conflicts with the
subject's "win the game when all levels are completed" — see the backlog.

### C7 — Seed derived from the level number

Level *n* uses `config.seed + n * 1000`.

*Why:* level 1 is reproducible for the reviewer (fixed seed, as required),
every level still gets a different maze, and no global random state has to be
carried between levels.

### C8 — A shared `Entity` base for Pac-Man and the ghosts

`Pacman` and `Ghost` both inherit from `Entity`, which owns the position, the
spawn cell, the previous cell used for display interpolation, and the
"do not cross walls" rule (`can_move`, `move_to_next`).

*Why:* the rule is identical for every character, so it is written once. The
ghosts' BFS now chooses a target cell and applies the step through the
inherited `move_to_next`, which means a pathfinding mistake can no longer walk
a ghost through a wall.
*Cost:* one more level of indirection in a small class hierarchy.

## Rejected alternatives

| Considered | Rejected because |
|---|---|
| Writing our own maze generator | Explicitly forbidden by the subject |
| A* instead of BFS | No gain on an unweighted grid of this size |
| Pixel-precise movement | Makes collisions and turns fragile for no visible benefit |
| Hand-written config validation | More code, weaker guarantees, no typing |
| SQLite for highscores | Ten records in a JSON file need no database |
