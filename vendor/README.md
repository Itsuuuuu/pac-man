# vendor/

`mazegenerator-2.0.2-py3-none-any.whl` is the **A-Maze-ing** package assigned
to us by another group. It is stored here as a distributable wheel and is
never copied into the project sources, so nothing in the repository can shadow
or alter it.

It is declared as a project dependency in `pyproject.toml`:

```toml
[tool.uv.sources]
mazegenerator = { path = "vendor/mazegenerator-2.0.2-py3-none-any.whl" }
```

`make install` installs it into `.venv/` like any other dependency.

## Reinstalling the package during the peer review

To replace it with your own copy of the assigned wheel:

```bash
uv pip install --force-reinstall --no-deps <path-to-your-wheel>
```

The game reads only the package's public interface — `MazeGenerator(size=...,
seed=...)` and its `.maze` property — so any build of the package works
without touching our code.
