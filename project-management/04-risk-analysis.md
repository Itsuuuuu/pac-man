# Risk Analysis

Scale: probability and impact rated Low / Medium / High. Status reflects the
project as of **2026-09-04**.

## Register

| # | Risk | Prob. | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R1 | The assigned `mazegenerator` package is reinstalled at the defence in a different version and the game breaks | High | High | Ship the package as a wheel in `vendor/`, declare it as a dependency, keep no copy in the import path, and use only its public interface (`MazeGenerator(size=..., seed=...)`, `.maze`) | **Closed** — verified by force-reinstalling the wheel and re-running: level 1 is byte-identical |
| R2 | The reviewer supplies a configuration with values we never tested, and the game crashes | High | High | Validate every field with Pydantic constraints; clamp out-of-range values to safe defaults and continue | **Open** — invalid values currently abort with a Pydantic dump instead of clamping |
| R3 | Style drift in the file everybody edits makes `make lint` fail | Realised | High | Single coding standard, `make lint` run before pushing | **Closed** — `src/ui/app.py` was reformatted and fully annotated; `flake8` and `mypy --strict` are clean |
| R4 | An unhandled exception ends the program during the defence (automatic 0) | Medium | High | `try/except` around every I/O boundary (config, highscores, assets, sound); no bare `except:` | **Closed** — file, asset and configuration paths are all covered |
| R5 | Highscore file grows unbounded or is corrupted between sessions | Realised | Medium | Cap the ranking at 10 entries on write; filter malformed entries on read and fall back to an empty list | **Closed** |
| R6 | Packaging and publication on a gaming platform is left until the end and is not delivered | High | High | Package early, treat publication validation delays as part of the schedule | **Partly closed** — `make package` produces a working standalone build; publication remains |
| R7 | Knowledge silos across four contributors: nobody can explain a module they never touched | Medium | Medium | Module ownership table so every area has a named owner, plus a cross-walkthrough before the defence | **Partly closed** — the ownership table exists, the walkthrough has not happened |
| R8 | A contributor cannot explain code they did not write (defence criterion "Can't support / explain code") | Medium | High | Ownership table; each owner walks the others through their module before the defence | **Open** — the walkthrough has not happened yet |
| R9 | Ghosts trap the player in a corridor with no escape, making levels unwinnable | Low | Medium | `PERFECT=False` produces loops in the maze, so corridors are not dead ends | **Closed** |
| R10 | The game has no reachable end state, so the "win" path is never exercised | Medium | Medium | Bound the number of levels and implement the victory screen | **Closed** — clearing the last configured level ends the game on the victory screen |

## Left to close before the defence

1. **R6** — publish the build. The standalone package is done and
   regenerable, but the platform may need validation time that is not ours to
   shorten, so upload early.
2. **R8** — hold the cross-module walkthrough, so nobody is asked about a
   file they have never opened.