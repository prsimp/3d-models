# 3d-models

[build123d](https://build123d.readthedocs.io/) models and other files for my
3D printing.

## Layout

```
common/               code shared between models
models/<name>/
  <name>.py           the model; `make` runs this file
  *.py                helpers used only by this model
  README.md           notes: purpose, material, print settings
  *.3mf               slicer project (Bambu Studio / OrcaSlicer)
  *.stl, *.step       meshes and solids with no source here, e.g. downloads
build/                rendered output (ignored by git)
```

Name model folders in kebab-case; a model's name is its folder's name.

## Setup

```sh
mise install    # Python and uv, pinned in mise.toml
uv sync         # .venv with build123d, ocp-vscode and ruff
```

Once `uv.lock` exists, mise activates `.venv` whenever you enter the directory.
Commit `uv.lock` so every machine gets the same build123d.

For live preview, install the OCP CAD Viewer extension in VS Code. It shows
whatever a script passes to `ocp_vscode.show()`.

## Writing a model

Each model builds a part and, when run as a script, exports it:

```python
"""Wall hook for a 20 mm rail."""

from build123d import Axis, Box, BuildPart, fillet

from common.export import export

WIDTH = 40
DEPTH = 20
THICKNESS = 4

with BuildPart() as hook:
    Box(WIDTH, DEPTH, THICKNESS)
    fillet(hook.edges().filter_by(Axis.Z), radius=3)

if __name__ == "__main__":
    export(hook.part, __file__)
```

`export` writes `build/<name>.stl` and `build/<name>.step`. Bambu Studio and
OrcaSlicer import either; STEP keeps true curves rather than a mesh.

Keep parameters as constants at the top of the file. Helpers in a model's
folder import directly (`import clip`); shared code goes in `common/`.

## Building

```sh
make           # build every out-of-date model
make <name>    # build one model
make list      # list model names
make lint      # ruff check and ruff format --check
make clean     # remove build/
```

Rendered output is not committed. Commit a slicer `.3mf` project when its print
settings are worth keeping, and leave sliced G-code out.
