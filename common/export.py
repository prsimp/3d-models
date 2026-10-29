"""Write a model's part to build/ for slicers and other CAD tools."""

from pathlib import Path

from build123d import Shape, export_step, export_stl

BUILD_DIR = Path(__file__).resolve().parent.parent / "build"


def export(part: Shape, source: str) -> None:
    """Write part to build/<name>.stl and build/<name>.step.

    source is the model script's __file__; its file name, minus .py, is <name>.
    """
    name = Path(source).stem
    BUILD_DIR.mkdir(exist_ok=True)
    if not export_stl(part, BUILD_DIR / f"{name}.stl"):
        raise RuntimeError(f"Failed to write {name}.stl")
    # Written last: make treats the STEP file as the sign a model is built.
    export_step(part, BUILD_DIR / f"{name}.step")
