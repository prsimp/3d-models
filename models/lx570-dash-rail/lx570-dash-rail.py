"""Accessory rail for the center speaker cover of a 2008-2015 Lexus LX570.

A flat U-shaped plate with a T-slot along its middle, open at both arm ends,
for RAM Tough-Track T-bolts and similar track accessories. It bolts through
the speaker cover (55510-60040) with counterbored holes beside the slot.

The U lies in the XY plane and opens toward +Y, the windshield; Z is up, out
of the slot.
"""

import math

import paper_template
from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Cylinder,
    Part,
    Pos,
    Rectangle,
    RectangleRounded,
    Sketch,
    chamfer,
    extrude,
)

from common.export import export

# The cover's underside measures 235 x 234 mm inside its walls. Two long ribs
# run front to back, 168 mm apart with a 31 mm strip outside each, and a
# moulding line runs across the back 28 mm in from the rear wall. Each arm's
# slot runs along a rib and the base's slot along the moulding line, so that
# the line passes between the two holes of every pair. That leaves the rail's
# rear edge 8 mm in from the rear wall.
RIB_SPACING = 168

# Footprint. The slot runs along the middle of the rail; the arms end in
# semicircles centred on it.
BAND = 43  # width of the rail itself
ARM_LENGTH = 150  # from the base's slot to the tips of the arms
CENTER_RADIUS = 30  # of the slot around the U's two corners
THICKNESS = 10
EDGE_CHAMFER = 2  # on the top outside edges
MIN_EDGE_WALL = 1.2  # left between each counterbore and the chamfer

# T-slot for RAM Tough-Track T-bolts: a 1/4"-20 post with a T-head of
# 0.48" x 0.95" x 0.11" (12.2 x 24.1 x 2.8 mm).
T_HEAD_WIDTH = 12.2
T_HEAD_LENGTH = 24.1
THROAT_WIDTH = 7.2  # the opening the post slides along
LIP = 3  # material over the channel
CHANNEL_WIDTH = 14.5  # the T-head slides in this
CHANNEL_HEIGHT = 3.8

# Counterbored holes for M4 or #8 pan head screws, which go through the
# speaker cover into nylon lock nuts. The heads (8.2 x 3.1 mm at most) sit
# just below the surface.
HOLE_DIAMETER = 4.5
COUNTERBORE_DIAMETER = 9
COUNTERBORE_DEPTH = 3.5

# The slot follows the rail's centreline: a rounded rectangle BAND / 2 in
# from the outside edge.
CENTER_WIDTH = RIB_SPACING
WIDTH = CENTER_WIDTH + BAND  # across the car, X
DEPTH = ARM_LENGTH + BAND / 2  # from the back of the base to the arm tips, Y
BASE_Y = -DEPTH / 2 + BAND / 2
ARM_TIP_Y = DEPTH / 2 - BAND / 2  # centres of the arms' semicircular ends

# Holes come in pairs, one either side of the slot, this far from the
# channel. Widening the rail moves its edges, not the holes.
HOLE_WALL = 1.875  # between each counterbore and the channel
HOLE_OFFSET = CHANNEL_WIDTH / 2 + HOLE_WALL + COUNTERBORE_DIAMETER / 2

# Where the pairs sit along the slot, mirrored left to right: x along the base,
# and along each arm as the distance from the base's slot. The base of the U
# lies along the cover's rear edge, with the light sensor inside the U. Each
# pair keeps its nuts clear of the clips, felt pads and speaker opening under
# the cover, judged from a photo: check them with the paper template before
# drilling.
# The speaker opening and the rear clip rule out a pair in the middle of the
# base; the moulding line curves away from a straight base beyond these.
BASE_PAIRS = [50]
# Between the side clips, either side of the moulding line across the panel,
# and short of the felt pads near the arm ends.
ARM_PAIRS = [43, 124]

# The test piece: one rear corner of the rail, enough to try T-bolts in the
# slot and around the bend, and screws in two pairs of holes.
TEST_MIN_X = 30
TEST_MAX_Y = 0

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def bend_clearance(radius: float) -> float:
    """Channel width a T-head needs to slide around a bend of this radius."""
    outer = math.hypot(radius + T_HEAD_WIDTH / 2, T_HEAD_LENGTH / 2)
    return outer - (radius - T_HEAD_WIDTH / 2)


assert CHANNEL_WIDTH >= bend_clearance(CENTER_RADIUS), (
    f"T-heads jam in the corners: CHANNEL_WIDTH must be at least "
    f"{bend_clearance(CENTER_RADIUS):.1f} mm for CENTER_RADIUS {CENTER_RADIUS}"
)

edge_wall = BAND / 2 - HOLE_OFFSET - COUNTERBORE_DIAMETER / 2 - EDGE_CHAMFER
assert edge_wall >= MIN_EDGE_WALL, (
    f"The chamfer leaves {edge_wall:.2f} mm beside the counterbores; "
    f"widen BAND or reduce EDGE_CHAMFER to leave {MIN_EDGE_WALL} mm"
)

assert max(ARM_PAIRS) + COUNTERBORE_DIAMETER / 2 <= ARM_LENGTH - BAND / 2, (
    "The last arm pair runs into the rounded arm ends"
)


def u_band(width: float) -> Sketch:
    """A U of the given width centred on the centreline, running well past
    the arm ends so that cuts made with it open out of them."""

    def offset_rect(offset: float) -> Sketch:
        height = 2 * DEPTH
        return Pos(0, BASE_Y - offset + height / 2) * RectangleRounded(
            CENTER_WIDTH + 2 * offset, height, CENTER_RADIUS + offset
        )

    return offset_rect(width / 2) - offset_rect(-width / 2)


def hole_positions() -> list[tuple[float, float]]:
    """Both holes of every pair, on both halves of the rail."""
    holes = []
    for side in (-1, 1):
        for x in BASE_PAIRS:
            holes += [(side * x, BASE_Y + d) for d in (-HOLE_OFFSET, HOLE_OFFSET)]
        for distance in ARM_PAIRS:
            arm_x = side * CENTER_WIDTH / 2
            y = BASE_Y + distance
            holes += [(arm_x + d, y) for d in (-HOLE_OFFSET, HOLE_OFFSET)]
    return sorted(holes)


def counterbore() -> Part:
    """A counterbored hole down through the rail, to subtract at (x, y, 0)."""
    hole = Cylinder(HOLE_DIAMETER / 2, THICKNESS, align=BOTTOM)
    bore = Cylinder(COUNTERBORE_DIAMETER / 2, COUNTERBORE_DEPTH, align=BOTTOM)
    return hole + Pos(0, 0, THICKNESS - COUNTERBORE_DEPTH) * bore


# Cut the U off where the arms' rounded ends begin, then add the ends.
outline = u_band(BAND) & Pos(0, ARM_TIP_Y - DEPTH) * Rectangle(2 * WIDTH, 2 * DEPTH)
for side in (-1, 1):
    outline += Pos(side * CENTER_WIDTH / 2, ARM_TIP_Y) * Circle(BAND / 2)

# Chamfer the blank's top edges before cutting the slot and holes, so that
# only the outside edges are chamfered.
rail = extrude(outline, THICKNESS)
rail = chamfer(rail.edges().group_by(Axis.Z)[-1], length=EDGE_CHAMFER)
rail -= Pos(0, 0, THICKNESS - LIP) * extrude(u_band(THROAT_WIDTH), LIP)
rail -= Pos(0, 0, THICKNESS - LIP - CHANNEL_HEIGHT) * extrude(
    u_band(CHANNEL_WIDTH), CHANNEL_HEIGHT
)
for x, y in hole_positions():
    rail -= Pos(x, y) * counterbore()

test_piece = rail & Pos(TEST_MIN_X + WIDTH / 2, TEST_MAX_Y - DEPTH / 2) * Box(
    WIDTH, DEPTH, THICKNESS, align=BOTTOM
)

if __name__ == "__main__":
    export(test_piece, __file__, variant="test")
    export(rail, __file__)
    paper_template.write(
        outline,
        u_band(THROAT_WIDTH) & outline,
        hole_positions(),
        HOLE_DIAMETER,
        COUNTERBORE_DIAMETER,
        __file__,
    )
