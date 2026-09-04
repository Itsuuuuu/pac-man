# Team Organization

## Measured contributions

From `git shortlog -sne` and `git log --numstat`, excluding binary assets.
Commits by the same person under several Git identities have been merged
(`Itsu` → Guillaume, `Ely Al Haiba` → elal-hai).

| Contributor | Commits | Lines added | Lines removed |
|---|---:|---:|---:|
| Guillaume | 23 | 1 617 | 328 |
| Ryan | 12 | 4 140 | 2 837 |
| elal-hai | 8 | 1 328 | 459 |
| Nicolas27500 | 8 | 253 | 162 |

The project was carried out by a team of **four**. All four identities above
are team members; the duplicate Git identities come from members committing
from several machines (school workstation, personal laptop, GitHub web
interface).

The root `README.md` credits the two logins registered on the project,
`rydelepi` and `guifouqu`. The other two contributors worked on the project
without being registered on it, which is why they appear in the Git history
but not in the README header.

## Module ownership

Derived from the commit count per file. "Owner" means the person who can
explain and defend that module during the defence.

| Module | Owner | Contributors |
|---|---|---|
| `src/config_parser.py`, `src/game_builder.py` | Guillaume | Ryan, elal-hai |
| `src/characters.py` (Pac-Man, ghosts, targeting) | Guillaume | Ryan |
| `src/ghost_algo.py` (BFS pathfinding) | Ryan | Guillaume |
| `src/game_setting.py`, `src/tile.py` | Guillaume | Ryan |
| `src/ui/app.py` (state machine, game loop) | shared | Ryan, Nicolas27500, elal-hai, Guillaume |
| `src/ui/draw_maze.py` (game screen, HUD) | Ryan | elal-hai, Guillaume |
| `src/ui/draw.py` (text screens, menus) | elal-hai | Ryan, Guillaume |
| `src/ui/utils.py` (highscores, themes) | Ryan | elal-hai |

`src/ui/app.py` is the only file with no single owner — every contributor
touched it. This is visible in its history and was the direct cause of the
style drift fixed during the code-quality pass (see
[04-risk-analysis.md](04-risk-analysis.md), risk R3).

## Working method

- **Version control:** a single `main` branch, direct pushes, no pull requests.
- **Integration:** each member pushed working increments; conflicts were
  resolved locally before pushing.
- **Task allocation:** by module rather than by feature — each member took an
  area and kept it (see the ownership table above). The engine went to
  Guillaume and Ryan, the screens to elal-hai and Nicolas.
- **Code review:** informal and in person, no review gate in the tooling.

## Decision log

The decisions below are the ones with a visible trace in the repository. Each
one is a fork in the road the team actually took, with the commit that records
it.

| # | Decision | When | Evidence (find the commit with) | Rationale |
|---|---|---|---|---|
| D1 | Validate the configuration with Pydantic rather than by hand | 2026-07-03 | `git log --grep "feat(config): make run fonctionne"` | Constraints declared once, unknown keys ignored for free, and a typed config object for mypy |
| D2 | Split the Pygame code into its own `src/ui/` package instead of leaving it beside the engine | 2026-07-24 | `git log --grep "refactor(ui): deplace le code Pygame"` | The engine had started importing display concerns; the split made the dependency one-way and is now the project's main architectural invariant |
| D3 | One BFS for all four ghosts, personality expressed only through the target cell | 2026-07-16 | `git log --grep "feat(ghosts): deplacement autonome"` | Four separate behaviours would have meant four things to debug; the maze is an unweighted grid so BFS is already optimal |
| D4 | Move per-level difficulty into `config.json` rather than hard-coding it | 2026-07-28 | `git log --grep "feat(ui): HUD complet"` | The reviewer changes the configuration during the defence, so difficulty had to be data |
| D5 | Add colour themes and selectable resolutions | 2026-07-29 | `git log --grep "feat(ui): option de theme"`, `git log --grep "feat(ui): couleur des murs"` | Scope addition, accepted because the maze renderer already scaled to the window |
| D6 | Store highscores in a plain JSON file rather than a database | 2026-07-19 | `git log --grep "feat(ui): systeme de highscore"` | Ten records need no database, and a text file is inspectable by the reviewer |
| D7 | Enforce the coding standard late, in one pass, instead of continuously | 2026-09-01 | see [06](06-progress-tracking.md) | This one turned out to be a mistake — see the retrospective below |

## Retrospective on the method

What the history shows, and what we would change:

- **No commit convention was agreed at the start.** The original messages were
  written ad hoc and several were placeholders, so the history could not be
  read as documentation. They were normalised to `type(scope): description`
  near the end of the project, each message rewritten from the diff of the
  commit it describes. Rewriting them afterwards made the log readable, but it
  did not give us what a convention would have given us *during* the project:
  the ability to see, at a glance, that four commits on 28/07 were undoing each
  other.
- **No branches means no review gate.** Every commit landed straight on `main`,
  so nothing checked a change before it was in the shared history. Two
  regressions came straight from this:
  - **28/07** — the pause menu was added, removed, and added again across four
    commits, and the cheat-value input was lost and restored in between.
  - **14/08** — the whole codebase was reformatted to the coding standard
    (4-space indentation, docstrings, type annotations), then `src/ui/app.py`
    alone was reverted to an older copy two commits later, losing that work
    for that file only.
- **Uploading files through the GitHub web interface caused most of the
  churn.** Eight commits were made that way, from copies that were not in sync
  with `main`. Every overwrite regression above comes from one of them. Using
  `git` from the working copy would have surfaced the conflicts instead of
  silently overwriting.
- **The style drift concentrated in the single shared file.** Modules with one
  owner stayed consistent. `src/ui/app.py`, the only file all four of us
  edited, is the one that ended up out of norm — 514 style errors and 84 typing
  errors, all of them the consequence of the 14/08 revert above.

**What we would do differently:** agree the commit convention and a
`make lint` pre-push habit on day one, and never push through the web
interface. Both cost nothing at the start of a project and would have removed
every problem in this list.
