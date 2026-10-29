"""A full-size paper template of the rail, for checking hole positions against
the speaker cover before printing the rail itself."""

from pathlib import Path

from build123d import (
    Circle,
    ExportSVG,
    Line,
    LineType,
    Pos,
    Sketch,
    Text,
    Unit,
)

from common.export import BUILD_DIR

CROSSHAIR = 7  # half-length of the lines marking each hole's centre
SCALE_BAR = 50  # mm; measure it on the printout to confirm the scale


def write(
    outline: Sketch,
    slot: Sketch,
    holes: list[tuple[float, float]],
    hole_diameter: float,
    counterbore_diameter: float,
    source: str,
) -> None:
    """Write build/<name>-template.svg at 1:1 scale, viewed from above.

    The rail is symmetric left to right, so the template also works face up on
    the underside of the cover.
    """
    top = outline.bounding_box().max.Y
    svg = ExportSVG(unit=Unit.MM, margin=1)
    svg.add_layer("outline", line_weight=0.4)
    svg.add_layer("slot", line_weight=0.2, line_type=LineType.DASHED)
    svg.add_layer("holes", line_weight=0.2)
    svg.add_layer("text", fill_color=(0, 0, 0), line_weight=0)

    svg.add_shape(outline.edges(), layer="outline")
    svg.add_shape(slot.edges(), layer="slot")
    for i, (x, y) in enumerate(holes, start=1):
        for diameter in (hole_diameter, counterbore_diameter):
            svg.add_shape(Pos(x, y) * Circle(diameter / 2).edges(), layer="holes")
        svg.add_shape(Line((x - CROSSHAIR, y), (x + CROSSHAIR, y)), layer="holes")
        svg.add_shape(Line((x, y - CROSSHAIR), (x, y + CROSSHAIR)), layer="holes")
        label = Pos(x + CROSSHAIR + 3, y + 3) * Text(str(i), font_size=4)
        svg.add_shape(label, layer="text")

    notes = [
        "FRONT (windshield)",
        "Print at 100% / actual size.",
        f"This bar should measure {SCALE_BAR} mm:",
    ]
    for i, note in enumerate(notes):
        y = top - 10 - i * 7
        svg.add_shape(Pos(0, y) * Text(note, font_size=5), layer="text")
    bar_y = top - 10 - len(notes) * 7
    svg.add_shape(
        Line((-SCALE_BAR / 2, bar_y), (SCALE_BAR / 2, bar_y)), layer="outline"
    )
    for x in (-SCALE_BAR / 2, SCALE_BAR / 2):
        svg.add_shape(Line((x, bar_y - 2), (x, bar_y + 2)), layer="outline")

    svg.write(BUILD_DIR / f"{Path(source).stem}-template.svg")
