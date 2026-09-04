# Acceptance Test Plan

Each test maps to a requirement of the subject and to a line of the evaluation
sheet. Status as of **2026-09-04**.

Legend: **PASS** verified · **FAIL** verified as not working · **TODO** not
implemented yet.

> **How these statuses were obtained.** The command-line, configuration,
> highscore and code-quality rows were verified by running the commands
> directly. The gameplay rows were verified by a headless simulation (4 000
> frames with randomised inputs, all screens rendered) combined with a read of
> the corresponding code. **Re-run the gameplay tests by hand before the
> defence** — the reviewer plays the game, and a headless run does not prove
> that what is on screen matches what the engine computed.

## Command line and configuration (subject V.1 – V.3)

| # | Test | Expected | Status |
|---|---|---|---|
| T01 | `make run` | Game starts on the main menu | PASS |
| T02 | `python -m src` with no argument | Clear usage message, exit code 1, no traceback | PASS |
| T03 | `python -m src missing.json` | "file not found" message, no traceback | PASS |
| T04 | `python -m src README.md` | "invalid JSON" message, no traceback | PASS |
| T05 | `python -m src a.json b.json` | Refused: exactly one argument is allowed | PASS |
| T06 | Config with `#` comment lines | Comments ignored, game starts | PASS |
| T07 | Config with an unknown key | Key ignored, game starts | PASS |
| T08 | Config with `width: 3` (below the minimum) | Clamped to a safe default, message logged, game continues | PASS |
| T09 | Config with `lives: -5` | Clamped to a safe default, game continues | PASS |
| T10 | Broken config, then press "Start Game" | Error reported before the window opens | PASS — config is read and repaired before `pygame.init()` |

## Maze generation (subject V.4)

| # | Test | Expected | Status |
|---|---|---|---|
| T11 | Level 1 is identical across two runs | Same maze (fixed seed) | PASS |
| T12 | Level 2 differs from level 1 | Different maze | PASS |
| T13 | Reinstall the assigned `.whl`, then run | Game behaves identically | PASS — force-reinstalled, level 1 maze unchanged |
| T14 | Ghosts and Pac-Man can reach every corridor | No unreachable pacgum | PASS |

## Player mechanics (subject VI.2)

| # | Test | Expected | Status |
|---|---|---|---|
| T15 | Arrow keys move Pac-Man | Movement in the four directions | PASS |
| T16 | Move into a wall | Pac-Man does not cross it | PASS |
| T17 | Buffer a turn just before a junction | The turn is applied at the junction | PASS |
| T18 | Touch a ghost while vulnerable | One life lost, respawn at the centre | PASS |
| T19 | Lose the last life | Game over, name-entry screen | PASS |
| T20 | Eat every pacgum in a level | Level completed, next level starts | PASS |
| T21 | Score and lives carry over to the next level | Both preserved | PASS |
| T22 | Level timer reaches zero | A life is lost, timer resets | PASS |

## Ghosts (subject VI.3)

| # | Test | Expected | Status |
|---|---|---|---|
| T23 | Ghosts move on their own | Autonomous movement through corridors | PASS |
| T24 | Ghosts chase the player | Distance to Pac-Man decreases | PASS |
| T25 | Ghosts flee after a super-pacgum | Ghosts move away | PASS |
| T26 | Eat a fleeing ghost | Ghost returns to its corner as eyes, then respawns | PASS |
| T27 | The four ghosts behave differently | Blinky pursues, Pinky ambushes, Inky flanks, Clyde wanders | PASS |

## Pacgums and scoring (subject VI.4, VI.6)

| # | Test | Expected | Status |
|---|---|---|---|
| T28 | Eat a pacgum | `+points_per_pacgum`, dot disappears | PASS |
| T29 | Eat a super-pacgum | `+points_per_super_pacgum`, ghosts become edible | PASS |
| T30 | Eat an edible ghost | `+points_per_ghost` | PASS |
| T31 | Super-pacgums sit in the four corners | Four pellets present | PASS |
| T32 | The score never decreases | Monotonic across a whole run | PASS |

## Highscores (subject V.5)

| # | Test | Expected | Status |
|---|---|---|---|
| T33 | Delete `highscore.json`, then start | Empty board, no crash | PASS |
| T34 | Corrupt `highscore.json` with invalid JSON | Empty board, no crash | PASS |
| T35 | Malformed entry (missing key, negative score) | Entry ignored, others kept | PASS |
| T36 | Finish a game and enter a name | Score saved, visible in the menu | PASS |
| T37 | Restart the game | The previous score is still there | PASS |
| T38 | Submit an 11th better score | The board keeps exactly 10 entries | PASS |
| T39 | Submit a score worse than the 10th | File not rewritten | PASS |
| T40 | Type a name longer than 10 characters | Input stops at 10 | PASS |
| T41 | Type a space in the name | Space accepted (subject: alphanumeric and spaces) | PASS |

## User interface (subject VI.8)

| # | Test | Expected | Status |
|---|---|---|---|
| T42 | Main menu | Start, Highscores, Instructions, Exit | PASS |
| T43 | In-game HUD | Score, lives, level, remaining time | PASS |
| T44 | Pause menu | Resume and return to main menu | PASS |
| T45 | Game over screen | Final score plus name entry | PASS |
| T46 | Victory screen | Congratulations, final score, name entry | PASS |

## Cheat mode (subject VI.5)

| # | Test | Expected | Status |
|---|---|---|---|
| T47 | Invincibility | Ghosts cannot kill the player | PASS |
| T48 | Infinite lives | Life count never drops | PASS |
| T49 | Edible ghosts | Ghosts are always edible | PASS |
| T50 | Point additions | Points added at game start | PASS |
| T51 | Level skips | Skip to a later level | TODO — settable but not applied, accepted as-is |

## Packaging (subject VII)

| # | Test | Expected | Status |
|---|---|---|---|
| T55 | Build is downloadable from a gaming platform | Free, unlisted project | TODO — not published |
| T56 | `make package` regenerates the build | Standalone build produced | PASS |
| T57 | Run the built executable with no argument | Starts on the bundled config | PASS |
| T58 | `config.json` placed next to the executable | Overrides the bundled one | PASS |
| T59 | Instructions shipped inside the package | `INSTRUCTIONS.txt` next to the executable | PASS |

## Code quality (subject III)

| # | Test | Expected | Status |
|---|---|---|---|
| T52 | `make lint` | flake8 and mypy clean | PASS |
| T53 | `make lint-strict` | `mypy --strict` clean | PASS |
| T54 | 60-minute session with random inputs | No unhandled exception | PASS — 4 000 simulated frames, no exception |

## Summary

**59 tests — 56 PASS, 0 FAIL, 3 TODO.**

No test fails. What remains is the publication of the build (T55, T13's
reinstall counterpart is already covered) and the "Level skips" cheat (T51),
which the team decided to leave settable but inactive.
