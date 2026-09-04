# Progress Tracking

Snapshot of **2026-09-04**, checked against the subject and the evaluation
sheet.

## Coverage by subject chapter

| Chapter | Requirement | State |
|---|---|---|
| III | Python 3.10+, flake8, mypy, docstrings, type hints | **Done** |
| III.2 | Makefile: `install`, `run`, `debug`, `clean`, `lint`, `lint-strict` | **Done** |
| IV | Playable game, OOP, modular architecture | **Done** — `Pacman` and `Ghost` share an `Entity` base carrying the wall rule |
| V.1 | Exactly one argument, clean error messages | **Done** |
| V.2 | JSON config with comments, documented keys | **Done** |
| V.3 | Clamp invalid values, log, continue | **Done** — every invalid field falls back to its default, validated before the window opens |
| V.4 | Use the assigned maze package as-is | **Done** — shipped as a wheel in `vendor/`, installed as a dependency |
| V.5 | Persistent highscores, top 10, robust | **Done** |
| VI.1 | Maze, pacgums, super-pacgums, 4 ghosts, centre spawn | **Done** |
| VI.2 | Player movement, lives, respawn, win/lose | **Done** — clearing the last configured level wins the game |
| VI.3 | Autonomous ghosts, chase, flee, respawn | **Done** |
| VI.4 | Pacgums and super-pacgums | **Done** |
| VI.5 | Cheat mode | **Partial** — "Level skips" is settable but not applied (accepted) |
| VI.6 | Scoring | **Done** |
| VI.7 | At least 10 levels, timer, pause, end of game | **Done** — 10 levels configured, completing the last one wins |
| VI.8 | Menus, HUD, pause, game over, victory | **Done** — victory screen with congratulations, final score and name entry |
| VII | Packaging and publication on a platform | **Partial** — standalone build works (`make package`); publication still to do |
| VIII | Project management | **In progress** — this directory |
| IX | README with the required sections | **Done** — rewritten in English with all required sections |

## Backlog, in the order we intend to close it

| Priority | Item | Why now | Owner | Done |
|---|---|---|---|---|
| 1 | This project-management directory | The evaluation stops here if it is missing | — | ☑ |
| 2 | `make lint` clean | Code Quality is 0 otherwise | — | ☑ |
| 3 | Highscore board capped at 10 | Required by V.5 | — | ☑ |
| 4 | Remove the vendored `mazegenerator`, declare it as a dependency | The reviewer reinstalls the package and re-runs | — | ☑ |
| 5 | Clamp invalid config values, validate before opening the window | Avoids a mid-defence crash | — | ☑ |
| 6 | Victory screen and a reachable end of game | Required by VI.8, checked explicitly | — | ☑ |
| 7 | Rewrite the README in English with the 6 missing sections | Required by IX | — | ☑ |
| 8 | Extend `config.json` to at least 10 levels | Required by VI.7 | — | ☑ |
| 9 | Shared base class for `Pacman` and `Ghost` | The sheet names this as the OOP example | — | ☑ |
| 10 | Packaging and publication | Required by VII; platform validation takes time | — | ☑ build done, ☐ publication |
| 11 | Accept spaces in player names | Required by V.5 | — | ☑ |
| 12 | Reject a second command-line argument | Required by V.1 | — | ☑ |
| 13 | Apply the "Level skips" cheat | Makes the reviewer's job easier | — | not planned |

Only the publication half of item 10 is still open.

## Planned vs. actual

The engine and the UI were delivered close to the initial intent: the game was
playable end to end by the end of week 31, which left room for polish.

What slipped is everything that is not gameplay. Packaging (chapter VII),
the project-management documents (chapter VIII) and the README (chapter IX)
were all pushed behind features, and all three are graded. The code-quality
requirement was treated the same way — the standard was only enforced at the
end, when `src/ui/app.py` had already accumulated 514 style errors and 84
typing errors across four contributors.

**The lesson we take from this:** the non-code deliverables and the linter are
not a final step. Running `make lint` as a pre-push habit, and writing the
project documents as the project progresses, would have cost less than the
retrofit did.
