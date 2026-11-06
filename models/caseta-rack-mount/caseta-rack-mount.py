"""Corner rack mount for a Lutron Caseta Smart Bridge.

An open tray holds the bridge beside a rack post. Its front wall carries on
past one side of the tray as a 1U ear, which screws to the post; the tray's
far wall has a wide notch for the bridge's cables. The style follows a
Philips Hue Bridge corner mount: hexagon windows in the walls, and the ear
rising above the walls in a smooth curve.

The front of the ear lies in the XZ plane at Y = 0, facing -Y, with the tray
behind it in +Y. Z is up, the tray's floor on Z = 0. The left mount's ear is
on the left (-X) when seen from the front; the right mount mirrors it.
"""

from build123d import (
    Align,
    Axis,
    Circle,
    Part,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    RectangleRounded,
    RegularPolygon,
    Sketch,
    SlotCenterToCenter,
    Spline,
    extrude,
    fillet,
    make_face,
)

from common.export import export

# The Smart Bridge (L-BDG2) is 2.75 x 2.75 x 1.19 in.
BRIDGE_WIDTH = 69.9
BRIDGE_HEIGHT = 30.2
CLEARANCE = 1.5  # around the bridge, each side

# The tray. The walls come up to the top of the bridge.
FLOOR = 2
WALL = 3
CORNER_RADIUS = 11  # outside; the front corner beside the ear is square
POCKET = BRIDGE_WIDTH + 2 * CLEARANCE
WIDTH = POCKET + 2 * WALL  # across the rack, X
DEPTH = WIDTH  # front to back, Y
WALL_HEIGHT = FLOOR + BRIDGE_HEIGHT

# The ear: one rack unit tall, with slots at the EIA-310 hole heights.
RACK_UNIT = 44.45
EAR_WIDTH = 18.8  # past the side of the tray
EAR_CORNER_RADIUS = 2
SLOT_INSET = 10  # from the side of the tray to the slots' centres
SLOT_LENGTH = 10
SLOT_HEIGHT = 7
HOLE_HEIGHTS = {3: [6.35, 22.225, 38.1], 2: [6.35, 38.1]}

# Above the walls the front wall stays a full unit tall for a little way into
# the tray, then curves down to the walls. The side wall beside the ear rises
# to meet it in a concave curve.
EAR_SHOULDER = 4  # into the tray, at full height
EAR_SLOPE_END = 52  # into the tray, where the front wall is back to height
GUSSET_RUN = 14  # along the side wall

# Hexagon windows, point up, in the front and side walls: a row of four with
# a row of three above, centred on each wall.
HEX_HEIGHT = 12  # point to point
HEX_PITCH = 13.4  # across, leaving 3 mm between windows
HEX_ROW_PITCH = HEX_PITCH * 3**0.5 / 2

# The cable notch in the back wall, for the bridge's power and Ethernet.
NOTCH_WIDTH = 45
NOTCH_BOTTOM = FLOOR + 3
NOTCH_RADIUS = 8  # at the bottom corners
NOTCH_FLARE = 5  # rounding the top of the wall into the notch

CORNER = (Align.MIN, Align.MIN)


assert EAR_SLOPE_END <= WIDTH - CORNER_RADIUS, (
    "The ear's curve runs into the far front corner of the tray"
)
assert NOTCH_WIDTH + 2 * NOTCH_FLARE <= WIDTH - 2 * CORNER_RADIUS, (
    "The cable notch runs into the back corners of the tray"
)
assert NOTCH_BOTTOM + NOTCH_RADIUS <= WALL_HEIGHT - NOTCH_FLARE, (
    "The cable notch's corners overlap"
)


# Each wall's openings and profile are drawn in 2D, (u, v) with v up, then
# placed on the wall: front walls on Plane.XZ, where (u, v) is (X, Z), and side
# walls on Plane.YZ, where (u, v) is (Y, Z).


def front(sketch: Sketch, y: float, thickness: float) -> Part:
    """Extrude a front-wall sketch from Y = y to y + thickness."""
    return Pos(0, y + thickness, 0) * extrude(Plane.XZ * sketch, thickness)


def side(sketch: Sketch, x: float, thickness: float) -> Part:
    """Extrude a side-wall sketch from X = x to x + thickness."""
    return Pos(x, 0, 0) * extrude(Plane.YZ * sketch, thickness)


def tray() -> Part:
    """The floor and walls, without the ear or any openings."""
    centre = Pos(WIDTH / 2, DEPTH / 2)
    outline = centre * RectangleRounded(WIDTH, DEPTH, CORNER_RADIUS)
    outline += Rectangle(CORNER_RADIUS, CORNER_RADIUS, align=CORNER)
    pocket = centre * RectangleRounded(POCKET, POCKET, CORNER_RADIUS - WALL)
    return extrude(outline, FLOOR) + extrude(outline - pocket, WALL_HEIGHT)


def ear(holes: int) -> Part:
    """The ear and the raised part of the front wall, with the screw slots."""
    edge = Polyline(
        (EAR_SLOPE_END, WALL_HEIGHT),
        (EAR_SLOPE_END, 0),
        (-EAR_WIDTH, 0),
        (-EAR_WIDTH, RACK_UNIT),
        (EAR_SHOULDER, RACK_UNIT),
    ) + Spline(
        (EAR_SHOULDER, RACK_UNIT),
        (EAR_SLOPE_END, WALL_HEIGHT),
        tangents=[(1, 0), (1, 0)],
    )
    plate = make_face(edge)
    plate = fillet(plate.vertices().group_by(Axis.X)[0], EAR_CORNER_RADIUS)
    for z in HOLE_HEIGHTS[holes]:
        plate -= Pos(-SLOT_INSET, z) * SlotCenterToCenter(
            SLOT_LENGTH - SLOT_HEIGHT, SLOT_HEIGHT
        )
    return front(plate, 0, WALL)


def gusset() -> Part:
    """The side wall beside the ear, rising to the ear's full height."""
    base = WALL_HEIGHT - 1  # overlapping the wall below
    edge = Polyline(
        (WALL + GUSSET_RUN, WALL_HEIGHT),
        (WALL + GUSSET_RUN, base),
        (0, base),
        (0, RACK_UNIT),
        (WALL, RACK_UNIT),
    ) + Spline(
        (WALL, RACK_UNIT),
        (WALL + GUSSET_RUN, WALL_HEIGHT),
        tangents=[(0, -1), (1, 0)],
    )
    return side(make_face(edge), 0, WALL)


def hexagons(centre: float) -> Sketch:
    """The windows for one wall, centred along it at u = centre."""
    gap = WALL_HEIGHT - FLOOR - HEX_HEIGHT - HEX_ROW_PITCH
    z = FLOOR + gap / 2 + HEX_HEIGHT / 2
    windows = Sketch()
    for row, count in ((0, 4), (1, 3)):
        for i in range(count):
            u = centre + (i - (count - 1) / 2) * HEX_PITCH
            windows += Pos(u, z + row * HEX_ROW_PITCH) * RegularPolygon(
                HEX_HEIGHT / 2, 6, rotation=30
            )
    return windows


def notch() -> Sketch:
    """The cable notch in the back wall, a front-wall sketch."""
    top = WALL_HEIGHT + 1
    cut = Pos(WIDTH / 2, NOTCH_BOTTOM) * Rectangle(
        NOTCH_WIDTH, top - NOTCH_BOTTOM, align=(Align.CENTER, Align.MIN)
    )
    cut = fillet(cut.vertices().group_by(Axis.Y)[0], NOTCH_RADIUS)
    for end in (-1, 1):
        x = WIDTH / 2 + end * (NOTCH_WIDTH / 2 + NOTCH_FLARE / 2)
        corner = Pos(x, WALL_HEIGHT - NOTCH_FLARE / 2 + 0.5) * Rectangle(
            NOTCH_FLARE, NOTCH_FLARE + 1
        )
        corner -= Pos(x + end * NOTCH_FLARE / 2, WALL_HEIGHT - NOTCH_FLARE) * Circle(
            NOTCH_FLARE
        )
        cut += corner
    return cut


def mount(holes: int = 3) -> Part:
    """The left-hand mount, with 2 or 3 screw slots in the ear."""
    part = tray() + ear(holes) + gusset()
    part -= side(hexagons(DEPTH / 2), -1, WIDTH + 2)
    part -= front(hexagons(WIDTH / 2), -1, WALL + 2)
    part -= front(notch(), DEPTH - WALL - 1, WALL + 2)
    return part


def right(part: Part) -> Part:
    """The mirror image of a left-hand mount, its ear on the right."""
    return part.mirror(Plane.YZ)


left_3 = mount(3)
left_2 = mount(2)

if __name__ == "__main__":
    export(right(left_3), __file__, variant="right")
    export(left_2, __file__, variant="2-hole")
    export(right(left_2), __file__, variant="right-2-hole")
    export(left_3, __file__)
