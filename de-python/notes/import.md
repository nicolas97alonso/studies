# Python Imports Cheat Sheet

## How Python finds your code

Python searches a list of folders called `sys.path`. If your code isn't in that list → import fails.

```python
import sys
# see what Python searches
print(sys.path)
# ['/your/project', '/usr/lib/python3', ...]
```

---

## Project structure (src layout)

```
my_project/
├── src/
│   └── dbt_monitor/
│       ├── __init__.py   # makes it a package (can be empty)
│       └── parser.py
├── tests/
│   └── test.py
└── pyproject.toml
```

> `src/` is just a folder convention — never use it in imports. Your package name is `dbt_monitor`.

---

## 3 ways to fix imports

### Option 1 — sys.path hack
Quick but fragile. Breaks if you move files.

```python
import sys
sys.path.append("../src")
from dbt_monitor.parser import fn
```

### Option 2 — PYTHONPATH
Works per terminal session.

```bash
PYTHONPATH=src/ python tests/test.py
```

### Option 3 — uv editable install ✅ recommended
Registers your package permanently. Works everywhere — terminal, pytest, CI.

```bash
# once per project
uv sync

# now this works anywhere
from dbt_monitor.parser import fn  # ✅
```

---

## pyproject.toml — what each part does

```toml
[project]
name = "dbt_monitor"                    # your package name

[build-system]
requires = ["setuptools"]               # WHO does the installing
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]                         # WHERE is the code

[tool.uv]
package = true                          # tells uv to install it too
```

---

## What `uv sync` does step by step

1. Reads `pyproject.toml` — finds dependencies + sees `package = true`
2. Creates `.venv` if missing — isolated environment for this project
3. Installs all dependencies — pytest, pyyaml, requests…
4. Creates a `.pth` pointer file — `.venv/site-packages/dbt_monitor.pth` → points to `/your/project/src`
5. Your package is importable everywhere ✅

---

## Import rules to memorize

| Rule | |
|---|---|
| Use `src/` in imports? | ❌ never |
| `from dbt_monitor.parser import fn` | ✅ correct |
| `from src.dbt_monitor.parser import fn` | ❌ wrong |
| Need `__init__.py` in package folder? | ✅ yes (can be empty) |
| Run `uv sync` every time? | only when deps change |

---

## The mental model in one paragraph

`sys.path` is the list Python searches when you write `import something`. By default it doesn't include your `src/` folder. Running `uv sync` with `package = true` and `where = ["src"]` makes setuptools create a `.pth` file inside `.venv` that permanently adds `src/` to `sys.path`. After that, `from dbt_monitor.parser import fn` works exactly like `import pandas` — same mechanism, you just wrote the package yourself.
