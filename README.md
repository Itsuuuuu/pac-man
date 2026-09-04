*This project has been created as part of the 42 curriculum by rydelepi, guifouqu.*

# Pac-Man

A Pac-Man clone in Python and Pygame: procedurally generated mazes, four
ghosts with distinct behaviours, levels of increasing difficulty, colour
themes, and a cheat menu for reviewers.

```bash
make install     # install dependencies into .venv
make run         # start the game with config.json
make lint        # flake8 + mypy
make lint-strict # flake8 + mypy --strict
make debug       # start under pdb
make clean       # remove caches
```

## Contents

- [Description](#description)
- [Instructions](#instructions)
- [Configuration](#configuration)
- [Highscore](#highscore)
- [Maze Generation](#maze-generation)
- [Implementation](#implementation)
- [General Software Architecture](#general-software-architecture)
- [Project Management](#project-management)
- [Packaging](#packaging)
- [Resources](#resources)

---

## Description

The goal is to clear every maze of its pacgums without being caught by the
ghosts. Eating a super-pacgum reverses the balance for a few seconds: the
ghosts flee and can be eaten for bonus points.

The game is built around three ideas:

- **The maze is not ours.** Every level comes from the `mazegenerator`
  package written by another team. Our loader adapts to their interface; we
  never modify their code.
- **Everything is configurable.** Maze size, pacgum count, speeds, level
  duration and power-pellet duration are per-level entries in a JSON file, so
  the game can be retuned without touching Python.
- **The game engine knows nothing about the display.** `src/` holds the rules,
  `src/ui/` holds Pygame. The dependency only ever goes one way.

**Features**

- Procedurally generated maze per level, with a fixed seed for level 1
- Four ghosts, four targeting behaviours, plus dead and frightened states
- Pacgums, super-pacgums, lives, score, per-level timer
- Main menu, instructions, highscore board, pause menu, end-of-game screens
- Persistent top-10 highscore board
- Four colour themes and four window resolutions
- Cheat menu for peer review
- Keyboard and mouse navigation

## Instructions

**Requirements:** Python 3.10 or later, and [uv](https://docs.astral.sh/uv/).

```bash
make install
make run
```

`make run` is equivalent to:

```bash
uv run python -m src config.json
```

The program takes **exactly one argument**: the path to a JSON configuration
file. Its name does not matter.

**Controls**

| Key | Action |
|---|---|
| Arrow keys | Move Pac-Man, navigate menus |
| Enter | Confirm a menu entry |
| Escape | Pause during a game, go back in a menu, quit from the main menu |
| Mouse | Hover and click the main-menu entries |

**Cheat menu.** Reachable from the main menu, and meant to make the peer
review easy:

| Cheat | Effect |
|---|---|
| Invincibility | Ghosts cannot kill Pac-Man |
| Infinite lives | The life counter never drops |
| Edible ghosts | Ghosts are always edible |
| Level skips | Value settable up to 42 *(not applied yet)* |
| Point additions | Adds up to 9 999 points at the start of a game |

Toggles are switched with Enter; numeric values are adjusted by holding the
left and right arrows, or typed directly after pressing Enter.

## Configuration

`config.json` is validated by Pydantic in
[config_parser.py](src/config_parser.py). Blank lines and lines starting with
`#` are treated as comments and stripped before parsing.

`level` is a **difficulty table with one entry per level**. Completing the last
entry wins the game.

| Key | Meaning | Default |
|---|---|---|
| `highscore_filename` | Path of the highscore file | `highscore.json` |
| `lives` | Starting lives | `1` |
| `points_per_pacgum` | Score for a pacgum | `1` |
| `points_per_super_pacgum` | Score for a super-pacgum | `1` |
| `points_per_ghost` | Score for an edible ghost | `1` |
| `seed` | Base seed; level *n* uses `seed + n * 1000` | `42` |

Per level, inside `level`:

| Key | Meaning | Default |
|---|---|---|
| `width`, `height` | Maze size, must be greater than 9 | `10` |
| `pacgum` | Number of pacgums to scatter | `10` |
| `level_max_time` | Seconds before a life is lost | `90` |
| `pacman_move_ms` | Delay between two Pac-Man steps — **higher is slower** | `200` |
| `ghost_move_ms` | Same, for ghosts | `260` |
| `ghost_frightened_move_ms` | Same, while ghosts are fleeing | `380` |
| `invincible_ms` | Duration of the frightened state; `0` disables it for that level | `6000` |

**Faulty configuration.** The game never stops on a questionable file. Any
value that is out of range, of the wrong type, or missing is replaced by the
model's default, a clear message is printed, and the game continues. Unknown
keys are ignored. The configuration is read and repaired **before** the window
opens, so a broken file is reported in the terminal rather than killing a game
already in progress:

```
$ make run
Warning: config field 'level.0.width' is invalid (Input should be greater than 9), using default 10
Warning: config field 'lives' is invalid (Input should be greater than 0), using default 1
```

Only an unreadable file or malformed JSON stops the program, with a clear
message and no traceback.

## Highscore

Highscores are stored as a JSON array in the file named by
`highscore_filename`, next to the project. The implementation is in
[utils.py](src/ui/utils.py).

**Why a plain JSON file.** Ten records need no database. A text file is
readable and editable by the reviewer, needs no extra dependency, and can be
deleted to test the empty-board case in one command.

**How it works.**

- The board is loaded at start-up and after every save.
- On read, malformed entries — missing key, wrong type, negative score — are
  filtered out rather than raising, and a missing or corrupt file yields an
  empty board.
- The board is always sorted by descending score and capped at 10 entries.
- On write, the new score is first compared to the **worst** kept score. If the
  board is full and the score does not beat it, the file is not rewritten at
  all. Otherwise the insertion point is found by walking up from the end, the
  entry is inserted, and the list is truncated back to 10.
- Names are limited to 10 characters.
- The player enters a name at the end of every game, whether they won or lost.

## Maze Generation

We do not generate mazes ourselves. Each level is produced by the
**A-Maze-ing** package assigned to us by another team, used as-is.

The package is shipped as a wheel in [vendor/](vendor/) and declared as a
regular dependency, so nothing in our sources can shadow or alter it:

```toml
[tool.uv.sources]
mazegenerator = { path = "vendor/mazegenerator-2.0.2-py3-none-any.whl" }
```

To reinstall it from another copy of the wheel during the review:

```bash
uv pip install --force-reinstall --no-deps <path-to-your-wheel>
```

**How we use it.** [game_builder.py](src/game_builder.py) calls
`MazeGenerator(size=(width, height), seed=seed)` and reads its `.maze`
property. That is the whole surface we depend on — no private attribute, no
subclassing. `PERFECT` is left at its default of `False`, which produces the
looping corridors Pac-Man needs instead of a perfect maze with dead ends.

The generator returns a grid of integers where each cell encodes its four
walls as a bitmask (N=1, E=2, S=4, W=8). We keep that encoding as-is in our
`Tile` objects, so no conversion layer is needed.

Level 1 always uses the same seed, so it is reproducible for the reviewer;
level *n* uses `seed + n * 1000` so every level gets its own maze. If the
generator fails, the error is caught and reported without a traceback.

## Implementation

**Tile-based logic, interpolated rendering.** The engine moves entities one
grid cell at a time on their own timers. The renderer interpolates between the
previous and the current cell so movement looks smooth at 60 FPS. Collisions
and pathfinding stay exact integer comparisons, with no floating-point edge
cases.

**Fixed 60 FPS loop with accumulators.** Pac-Man and the ghosts each have their
own timer, fed by the frame delta and drained by whole steps. Ghosts slow down
further while they are fleeing.

**Input buffering.** One pending direction is stored. If the turn is possible
right away it is applied immediately; otherwise Pac-Man keeps going straight
and the turn fires as soon as the corridor opens. This is what makes cornering
feel right.

**A shared base for every character.** `Pacman` and `Ghost` both inherit from
`Entity`, which owns the position, the spawn cell, the previous cell used for
interpolation, and the "do not cross walls" rule. Ghosts apply the step chosen
by the BFS through that same inherited `move_to_next`, so no character can
walk through a wall.

**One pathfinding algorithm.** All four ghosts run the same BFS in
[ghost_algo.py](src/ghost_algo.py). BFS is optimal on an unweighted grid, and
having a single implementation means a single place to debug.

**Personality through target selection only.** Each ghost picks a different
target cell in `Ghost.get_target()`:

| Ghost | Target |
|---|---|
| Blinky | Pac-Man's current cell |
| Pinky | Four cells ahead of Pac-Man's direction |
| Inky | The Blinky→Pac-Man vector, doubled |
| Clyde | A random cell |

Two states override the personality: a dead ghost targets its spawn and
returns as eyes; a frightened ghost memorises one random target so it does not
jitter between two cells.

**Adaptive layout.** `compute_layout()` computes the largest square tile that
fits the window while preserving the maze aspect ratio, so every resolution
works without a separate asset set.

## General Software Architecture

```
src/
├── __main__.py         entry point (python -m src config.json)
├── config_parser.py    Pydantic models: GameConfig, LevelConfig
├── game_builder.py     JSON loading, config repair, level construction
├── game_setting.py     mutable state of a level: map, entities, score, lives
├── tile.py             one maze cell: walls bitmask, type, content
├── characters.py       Entity base, Pacman, Ghost, and ghost targeting
├── ghost_algo.py       BFS pathfinding — the only one in the project
└── ui/
    ├── app.py          PacManApp: state machine, game loop, input
    ├── draw_maze.py    game screen: walls, entities, HUD sidebar
    ├── draw.py         text screens: menu, instructions, scores, pause, end
    ├── assets.py       sprite loading and caching
    └── utils.py        shared types (Theme, Rgb) and highscore persistence
```

**The dependency rule.** `src/ui/` imports from `src/`. `src/` never imports
from `src/ui/`. The game rules can therefore be exercised without opening a
window, which is how the acceptance tests are run headless.

**Data flow of one frame.** `PacManApp.run()` ticks the clock, drains the
Pygame event queue into the state machine, advances the engine by whole steps
when the accumulators allow it, then renders the current state. The renderer
only reads engine state; it never mutates it.

**State machine.** `menu`, `options` (instructions), `highscores`, `cheat`,
`game`, `pause`, `enter_name`. Every screen is one branch in `process_events()`
and one branch in `render()`.

## Project Management

The full project-management record — timeline, team organisation, technical
choices, risk register, acceptance test plan and progress tracking — is in
**[project-management/](project-management/)**.

## Packaging

The build script and its PyInstaller spec are at the root of the repository.
See [PACKAGING.md](PACKAGING.md) for building a standalone executable and
publishing it to itch.io.

```bash
make package
```

## Resources

**Documentation**

- [Pygame documentation](https://www.pygame.org/docs/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [uv documentation](https://docs.astral.sh/uv/)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [PyInstaller manual](https://pyinstaller.org/en/stable/)

**On Pac-Man**

- [The Pac-Man Dossier](https://pacman.holenet.info/) — reference description
  of the original ghost behaviours and their targeting rules
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)

**Use of AI**

AI assistants were used on this project for the following, and every generated
suggestion was reviewed and rewritten before being kept:

- **Ghost targeting.** An assistant was asked for an example of how four
  different behaviours could share a single pathfinding routine. The result was
  used as a starting point for the shape of `Ghost.get_target()`; a trace of
  that exchange is still visible as a comment in
  [ghost_algo.py](src/ghost_algo.py). The BFS implementation itself is ours.
- **Documentation.** Drafting this README and the project-management documents
  from the Git history and the source.
- **Ghosts Algorithms.** To look the real movement of the differents intities.