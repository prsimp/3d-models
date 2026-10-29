"""Charging dock for three Amazon Basics 20,000 mAh power banks (B0FFM4BY6C).

The banks stand on their port ends in a row, broad faces together, each in a
slot with a right-angle USB-C adapter set into its floor. A bank slides down
its slot onto the adapter's plug and comes to rest on the floor, so the floor
carries its weight and the plug only makes the connection. A cable runs from
the back of each adapter out through the back wall.

X runs along the row, Y from front to back and Z up. Each bank goes in with
its USB-A port toward the front, -Y, as the label on each slot's floor shows.
"""

from build123d import (
    Align,
    Axis,
    Box,
    Part,
    Pos,
    RectangleRounded,
    Text,
    extrude,
    fillet,
)

from common.export import export

# The bank, standing on its port end, measured with calipers.
BANK_THICKNESS = 30.0  # X
BANK_WIDTH = 72.5  # Y

# The ports sit on a panel flush with the end face: USB-A, then two USB-C,
# all centred across the thickness. The dock charges through the nearer USB-C
# port, this far from the USB-A edge. A bank put in backwards then lands on
# plain panel between its ports, where the plug cannot catch; under the other
# USB-C port, 53.9 mm in, a reversed bank would sit half over the USB-A port.
PORT_FROM_EDGE = 40.4

# Slots. The bank's corners were not measured; the slot's corners are kept
# well under what the photos show, so that the bank's flat faces locate it.
CLEARANCE = 0.4  # per side; choose from the clearance test
SLOT_RADIUS = 3
LEAD_IN = 1.5  # chamfer around each slot's mouth
SLOT_X = BANK_THICKNESS + 2 * CLEARANCE
SLOT_Y = BANK_WIDTH + 2 * CLEARANCE
SLOTS = 3

# Body.
WALL = 4  # outside walls and between slots
BACK_WALL = 8  # roofs the cable plugs; see below
WALL_HEIGHT = 45  # above the floor
MIN_SKIN = 1.5  # under the adapter pockets and cable tunnels
CORNER_RADIUS = 6  # outside vertical edges
TOP_FILLET = 1  # outside top edges
LABEL_DEPTH = 0.6

# Right-angle USB-C adapter, male to female, bent within the plane of the
# plug's broad faces: the whole adapter is a flat L. Its plug points up, and
# its body runs toward the back with the female end facing back.
# PLACEHOLDERS: measure an adapter and replace these.
ADAPTER_THICKNESS = 7.5  # X
ADAPTER_HEIGHT = 13  # Z, the body below the plug
ADAPTER_FRONT = 6  # Y, from the plug's centre to the body's front end
ADAPTER_BACK = 19  # Y, from the plug's centre to the female end's face
SOCKET_DEPTH = 6.5  # from the body's top face down to the socket's centre
ADAPTER_DROP = 0.3  # the body's top below the floor, so the bank rests on it
POCKET_CLEARANCE = 0.2  # per side, which lets the plug float into the port

# The C-to-C cable's plug, which enters the adapter's female end through a
# tunnel in the back wall. Pulling a bank out pulls up on the adapter; the
# cable plug's overmould, held under the tunnel's roof, keeps it in place.
# PLACEHOLDERS, as above. The female end's broad faces stand upright.
CABLE_PLUG_THICKNESS = 7  # X
CABLE_PLUG_HEIGHT = 12.5  # Z
CABLE_PLUG_LENGTH = 22  # Y, the overmould
CABLE_CLEARANCE = 0.5  # per side
MIN_ROOF = 3  # length of overmould under the back wall

TUNNEL_HALF_HEIGHT = CABLE_PLUG_HEIGHT / 2 + CABLE_CLEARANCE

# The floor's top sits high enough to leave MIN_SKIN under each pocket and
# tunnel.
FLOOR = MIN_SKIN + max(
    ADAPTER_DROP + ADAPTER_HEIGHT,
    ADAPTER_DROP + SOCKET_DEPTH + TUNNEL_HALF_HEIGHT,
)
DOCK_Y = WALL + SLOT_Y + BACK_WALL

SLOT_FRONT_Y = -DOCK_Y / 2 + WALL
SLOT_BACK_Y = SLOT_FRONT_Y + SLOT_Y
SLOT_CENTER_Y = (SLOT_FRONT_Y + SLOT_BACK_Y) / 2
PLUG_Y = SLOT_FRONT_Y + CLEARANCE + PORT_FROM_EDGE
LABEL_Y = SLOT_FRONT_Y + 8

# The clearance test: a short block with a slot at each clearance, open top
# and bottom, so that a bank can be pushed right through each one.
TEST_CLEARANCES = [0.2, 0.3, 0.4, 0.5]
TEST_HEIGHT = 10
TEST_LABEL_WALL = 9  # in front of the slots, for the labels

# The one-slot dock, to try an adapter, cable and bank together before
# printing all three. Its walls are tall enough to guide a bank well before
# its port meets the plug, and to keep it from levering on the plug.
SINGLE_WALL_HEIGHT = 20

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

assert PLUG_Y + ADAPTER_BACK + CABLE_PLUG_LENGTH >= SLOT_BACK_Y + MIN_ROOF, (
    "The cable plug's overmould stops short of the back wall, so nothing holds "
    "the adapter down: lengthen BACK_WALL or check the adapter's dimensions"
)
assert PLUG_Y + ADAPTER_BACK + POCKET_CLEARANCE < SLOT_BACK_Y, (
    "The adapter runs past the back of the slot, under the back wall"
)


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    """A box spanning the given ranges."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(
        x1 - x0, y1 - y0, z1 - z0, align=BOTTOM
    )


def slot(clearance: float, depth: float) -> Part:
    """A slot for one bank, to subtract from a top face at (x, y, top). It
    runs down depth from there, with a lead-in at its mouth."""
    outline = RectangleRounded(
        BANK_THICKNESS + 2 * clearance, BANK_WIDTH + 2 * clearance, SLOT_RADIUS
    )
    # The lead-in widens at 45 degrees and carries on above the top face, so
    # that the cut never shares a face with it.
    shaft = Pos(0, 0, -depth) * extrude(outline, depth)
    lead_in = Pos(0, 0, -LEAD_IN) * extrude(outline, LEAD_IN + 1, taper=-45)
    return shaft + lead_in


def adapter_cut() -> Part:
    """The adapter's pocket and its cable's channel, to subtract with the
    plug's centre at (x, PLUG_Y) and the adapter's top face at z = 0."""
    half_x = ADAPTER_THICKNESS / 2 + POCKET_CLEARANCE
    pocket = box(
        -half_x,
        half_x,
        -ADAPTER_FRONT - POCKET_CLEARANCE,
        ADAPTER_BACK + POCKET_CLEARANCE,
        -ADAPTER_HEIGHT,
        ADAPTER_DROP + 1,
    )
    # Under the slot the channel is open to the floor, which needs no bridge;
    # through the back wall it becomes a tunnel with a roof.
    half_x = CABLE_PLUG_THICKNESS / 2 + CABLE_CLEARANCE
    bottom = -SOCKET_DEPTH - TUNNEL_HALF_HEIGHT
    to_slot_back = SLOT_BACK_Y - PLUG_Y
    channel = box(-half_x, half_x, 0, to_slot_back, bottom, ADAPTER_DROP + 1)
    tunnel = box(
        -half_x,
        half_x,
        to_slot_back - 1,
        DOCK_Y,
        bottom,
        -SOCKET_DEPTH + TUNNEL_HALF_HEIGHT,
    )
    return pocket + channel + tunnel


def engraving(text: str, x: float, y: float, z: float) -> Part:
    """Text to subtract from a top face at height z, reading from the front."""
    return Pos(x, y, z - LABEL_DEPTH) * extrude(
        Text(text, font_size=5), 1 + LABEL_DEPTH
    )


def build_dock(slots: int, wall_height: float) -> Part:
    """The dock with this many slots in a row and walls this tall above the
    floor."""
    width = slots * SLOT_X + (slots + 1) * WALL
    height = FLOOR + wall_height
    # Round the blank's top edges before cutting the slots, so that only the
    # outside edges are rounded.
    dock = extrude(RectangleRounded(width, DOCK_Y, CORNER_RADIUS), height)
    dock = fillet(dock.edges().group_by(Axis.Z)[-1], radius=TOP_FILLET)
    for i in range(slots):
        x = (i - (slots - 1) / 2) * (SLOT_X + WALL)
        dock -= Pos(x, SLOT_CENTER_Y, height) * slot(CLEARANCE, wall_height)
        dock -= Pos(x, PLUG_Y, FLOOR - ADAPTER_DROP) * adapter_cut()
        dock -= engraving("USB-A", x, LABEL_Y, FLOOR)
    return dock


dock = build_dock(SLOTS, WALL_HEIGHT)
single = build_dock(1, SINGLE_WALL_HEIGHT)

test_pitch = BANK_THICKNESS + 2 * max(TEST_CLEARANCES) + WALL
test_y = TEST_LABEL_WALL + BANK_WIDTH + 2 * max(TEST_CLEARANCES) + WALL
clearance_test = extrude(
    RectangleRounded(len(TEST_CLEARANCES) * test_pitch + WALL, test_y, CORNER_RADIUS),
    TEST_HEIGHT,
)
for i, clearance in enumerate(TEST_CLEARANCES):
    x = (i - (len(TEST_CLEARANCES) - 1) / 2) * test_pitch
    slot_front = -test_y / 2 + TEST_LABEL_WALL
    y = slot_front + BANK_WIDTH / 2 + clearance
    clearance_test -= Pos(x, y, TEST_HEIGHT) * slot(clearance, TEST_HEIGHT + 1)
    label_y = -test_y / 2 + TEST_LABEL_WALL / 2
    clearance_test -= engraving(f"{clearance}", x, label_y, TEST_HEIGHT)

if __name__ == "__main__":
    export(clearance_test, __file__, variant="clearance-test")
    export(single, __file__, variant="single")
    export(dock, __file__)
