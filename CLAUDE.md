# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Development Commands

### Common Tasks
- **Install dependencies**: `make install` (syncs uv and creates venv)
- **Run the game**: `make run` (launches Pac-Man with config.json)
- **Debug mode**: `make debug` (starts with pdb debugger)
- **Clean cache**: `make clean` (removes __pycache__ directories)
- **Full clean**: `make fclean` (also removes .venv)

### Code Quality
- **Lint**: `make lint` (flake8 + mypy)
- **Strict lint**: `make lint-strict` (flake8 + mypy --strict)

### Running Tests
Currently no formal test suite exists. To verify changes:
1. Run the game manually with `make run`
2. Test specific scenarios using cheat codes (accessible via Options menu)
3. Verify level progression and ghost behaviors

## 🏗️ Architecture Overview

### Core Principles
- **Strict separation**: UI layer (`src/ui/`) depends on game engine, never vice versa
- **Single pathfinding algorithm**: All ghost movement uses BFS from `ghost_algo.py`
- **Configuration-driven**: All gameplay parameters come from `config.json` validated by Pydantic
- **Tile-based movement**: Game logic operates on grid positions; rendering handles interpolation

### Key Components

#### Game Engine (`src/`)
- `__main__.py`: Entry point - parses config path and launches PacManApp
- `config_parser.py`: Pydantic models for config validation (LevelConfig, GameConfig)
- `game_builder.py`: Loads config and constructs game levels
- `game_setting.py`: Holds mutable game state (map, entities, score, lives)
- `tile.py`: Represents maze cells with bitmask wall encoding (N=1,E=2,S=4,W=8)
- `characters.py`: PacMan and Ghost classes; Ghost.get_target() defines personalities
- `ghost_algo.py`: Sole pathfinding implementation (BFS with early termination)

#### UI Layer (`src/ui/`)
- `app.py`: Main game loop, state machine (menu/options/game/pause/etc.), input buffering
- `draw_maze.py`: Game screen rendering (walls, entities, sidebar with layout adaptation)
- `draw.py`: Text-based screens (menu, options, highscores, etc.)
- `assets.py`: Sprite loading and caching with directional frames
- `utils.py`: Shared types (Theme, Rgb) and highscore persistence

### Important Details

#### Maze Representation
- Walls stored as bitmask per tile enabling efficient collision checks
- Two wall adapters: `wall_from_grid()` (raw generator) and `wall_from_tiles()` (Tile objects)
- DELTAS maps bits to direction vectors: [(0,-1), (1,0), (0,1), (-1,0)]

#### Ghost AI
- **Single algorithm**: BFS finds shortest path in unweighted grid
- **Personality via target selection**: Each ghost type implements different targeting in `Ghost.get_target()`
  - Blinky: Direct pursuit of PacMan
  - Pinky: 4 tiles ahead of PacMan's direction
  - Inky: Vector doubled from Blinky relative to PacMan
  - Clyde: Random tile (current implementation flaw - should remember target)
- **Special states override personality**:
  - Dead: Target = ghost spawn (eyes return to center)
  - Frightened: Memorized random target prevents jittering

#### Rendering & Timing
- **Fixed 60 FPS loop** with accumulator timers for entity movement
- **Input buffering**: Stores one directional input for smooth cornering
- **Sprite interpolation**: Renders entities between grid positions for smooth animation
- **Adaptive layout**: `compute_layout()` scales tiles to fit window while maintaining aspect ratio

#### Configuration System
- `config.json` defines level progression via array of LevelConfig objects
- Final level repeats indefinitely for endless play
- Parameters control:
  - Maze dimensions (width/height > 9)
  - PacGum count and level timer
  - Movement speeds (higher values = slower movement)
  - Invincibility duration from super pacgums

## 📝 File Conventions
- **Absolute imports**: Use `src.module` style (e.g., `from src.ui.app import PacManApp`)
- **Type hints**: Throughout codebase using Python 3.9+ syntax
- **Constants**: Defined at module level in ALL_CAPS
- **Sprite naming**: Directional sprites follow convention (e.g., pacman_right_0.png)
- **JSON files**: `highscore.json` and `config.json` use UTF-8 encoding

## 🔍 Debugging Tips
1. **Enable cheat menu** for invincibility, infinite lives, etc.
2. **Check console output** for error traces when launching via `make run`
3. **Use debug target** (`make debug`) to step through code with pdb
4. **Inspect ghost behavior** by temporarily modifying `ghost_algo.py` for verbose logging
5. **Verify level generation** by checking that seed derives from level number

## 🛠️ When Modifying
- **Ghost AI changes**: Modify `Ghost.get_target()` in characters.py for new behaviors
- **Movement speed**: Adjust values in config.json (remember: higher = slower)
- **Rendering changes**: Work in draw_maze.py for game screen, draw.py for menus
- **New levels**: Edit config.json to add LevelConfig objects to the level array
- **Maintain separation**: Keep UI independent of game engine logic