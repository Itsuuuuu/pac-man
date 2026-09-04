# Packaging and Deployment

This project ships as a standalone build that runs without Python, uv, or any
dependency installed on the player's machine.

> This document is developer documentation and is not itself required by the
> subject. What the subject requires is the packaging spec at the repository
> root ([pacman.spec](pacman.spec)), the instructions shipped inside the
> package ([INSTRUCTIONS.txt](INSTRUCTIONS.txt)), and the published build.

- Build script: `make package`
- PyInstaller spec: [pacman.spec](pacman.spec)
- Standalone entry point: [launcher.py](launcher.py)

## Building

```bash
make install
make package
```

The build takes about a minute and produces, in `dist/`:

| Output | Platform | Size |
|---|---|---|
| `dist/pacman/` | any — folder with the `pacman` executable next to its data | ~39 MB |
| `dist/Pac-Man.app` | macOS — double-clickable bundle | ~40 MB |

On Windows the same command produces `dist\pacman\pacman.exe`; on Linux,
`dist/pacman/pacman`. **PyInstaller does not cross-compile:** the build must be
run on the target operating system.

`dist/` and `build/` are ignored by Git. Only the spec and the build script are
committed, so the package can be regenerated during the peer review.

## What goes into the build

The spec bundles three sets of data files, mirroring the repository layout
because the code locates its resources relative to `__file__`:

| Source | Destination in the bundle |
|---|---|
| `Assets/` | `Assets/` — sprites and sound |
| `src/ui/font_pacman/` | `src/ui/font_pacman/` — the Pac-Man fonts |
| `config.json` | bundle root — the default configuration |
| `INSTRUCTIONS.txt` | bundle root — the in-package instructions |

`mazegenerator` is listed as a hidden import: it is only ever reached
dynamically, so PyInstaller does not detect it by static analysis. Development
tools (flake8, mypy, tkinter) are excluded.

## How the packaged game finds its configuration

The command-line version requires exactly one argument. A game launched by
double-click has none, so [launcher.py](launcher.py) resolves one:

1. a `config.json` sitting **next to the executable**, if there is one — this
   is how a player retunes the game without rebuilding it;
2. otherwise, the `config.json` **bundled inside** the build.

Running `./dist/pacman/pacman config.json` with an explicit argument still
works and behaves exactly like `make run`.

> **Note.** The packaged build is windowed (`console=False`), so the
> configuration warnings printed on `stderr` are not visible to the player.
> Use `make run` when you need to see them.

## In-package instructions

The subject requires the package itself to carry its instructions, not just
the repository. [INSTRUCTIONS.txt](INSTRUCTIONS.txt) covers controls, menus,
rules and the full configuration reference, and `make package` places it — with
an editable `config.json` — next to the executable:

```
dist/pacman/
├── pacman              the game
├── INSTRUCTIONS.txt    controls, options, configuration
├── config.json         editable, takes priority over the bundled one
└── _internal/          runtime, assets and fonts
```

Zip that whole folder when uploading, so the player gets the instructions with
the game. The same text also works as the itch.io page description.

## Publishing to itch.io

The build is distributed as a **free, unlisted** project, as the subject asks.

**1. Create the project.** On itch.io, *Dashboard → Create new project*:

| Field | Value |
|---|---|
| Kind of project | Downloadable |
| Pricing | No payments |
| Visibility | Draft, or Restricted with a secret URL |
| Platforms | Tick the ones you upload a build for |

Paste the in-package instructions above into the description.

**2. Upload.** Either drag the zipped `dist/pacman/` folder into the uploads
section, or use itch.io's command-line tool:

```bash
# once, to authenticate
butler login

# then, per platform
butler push dist/pacman <user>/<project>:osx
```

Tick *"This file will be played in the browser"* → **no**, and mark the upload
as the executable for its platform.

**3. Verify.** Download the published build on a machine that has neither
Python nor the project checked out, and confirm it starts and plays.

> `TO COMPLETE` — Add the project URL here once published, so the reviewer can
> reach it directly from the repository.

## Regenerating during the peer review

```bash
make package
```

Nothing else is required: the spec, the launcher and the vendored
`mazegenerator` wheel are all in the repository.
