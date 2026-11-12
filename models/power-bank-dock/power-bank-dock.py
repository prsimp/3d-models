"""Charging dock for three Amazon Basics 20,000 mAh power banks (B0FFM4BY6C).

The banks stand on their port ends in a row, broad faces together, each in a
slot with a right-angle USB-C adapter glued into its floor. A bank slides down
its slot onto the adapter's plug and comes to rest on the floor, so the floor
carries its weight and the plug only makes the connection. A cable plugs into
the back of each adapter through a tunnel in the back wall, and unplugs again.

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
from common.preview import preview

# The bank, standing on its port end, measured with calipers.
BANK_THICKNESS = 30.0  # X
BANK_WIDTH = 72.5  # Y

# The ports sit on a panel flush with the end face: USB-A, then two USB-C.
# The dock charges through the nearer USB-C port, this far from the USB-A
# edge. A bank put in backwards then lands on plain panel between its ports,
# where the plug cannot catch; under the other USB-C port, 53.9 mm in, a
# reversed bank would sit half over the USB-A port.
PORT_FROM_EDGE = 40.4

# Across the thickness the port sits off centre, toward the broad face without
# the charge LEDs: its centre is 13.7 mm from that face and 15.2 mm from the
# LED face. Those add up to less than the thickness, so the port goes midway
# between where each puts it. With USB-A toward the front, the LED face is on
# the right, +X, so the port sits left of the slot's centre.
PORT_FROM_PLAIN_FACE = 13.7
PORT_FROM_LED_FACE = 15.2
PORT_X = (PORT_FROM_PLAIN_FACE - PORT_FROM_LED_FACE) / 2

# Slots. The bank's corners were not measured; the slot's corners are kept
# well under what the photos show, so that the bank's flat faces locate it.
# The first test print, at 0.4 mm all round, let the bank rock front to back.
CLEARANCE_X = 0.4  # per side, across the thickness
CLEARANCE_Y = 0.2  # per side, front to back
SLOT_RADIUS = 3
LEAD_IN = 1.5  # chamfer around each slot's mouth
SLOT_X = BANK_THICKNESS + 2 * CLEARANCE_X
SLOT_Y = BANK_WIDTH + 2 * CLEARANCE_Y
SLOTS = 3

# Body.
WALL = 4  # outside walls and between slots
BACK_WALL = 8  # around the cable tunnels
WALL_HEIGHT = 45  # above the floor
MIN_SKIN = 1.5  # under the adapter pockets and cable tunnels
CORNER_RADIUS = 6  # outside vertical edges
TOP_FILLET = 1  # outside top edges
LABEL_DEPTH = 0.6

# Right-angle USB-C adapter (Silkland), male to female, bent within the plane
# of the plug's broad faces: a flat L, 24 x 21 x 6.4 mm overall. From the
# bottom up it is a 12 mm body, a 2.5 mm collar round the plug's root, and
# 6.5 mm of plug. The plug points up near the body's front end; the female
# socket, upright in the back end, faces back.
ADAPTER_THICKNESS = 6.4  # X
ADAPTER_LENGTH = 24  # Y
ADAPTER_HEIGHT = 21  # Z, from the body's bottom to the plug's tip
PLUG_LENGTH = 6.5  # above the collar
PLUG_FROM_FRONT = 5.5  # Y, the plug's centre from the body's front end
SOCKET_HEIGHT = 5.5  # the socket's centre above the body's bottom
# The collar's top sits this far below the floor, so that the bank rests on
# the floor and the plug reaches PLUG_LENGTH - ADAPTER_DROP into its port.
ADAPTER_DROP = 0.3
# Per side around the body, which lets the plug find the port when the
# adapter is glued in with a bank seated on it.
POCKET_CLEARANCE = 0.3

# The cable is not chosen yet. The tunnel through the back wall, centred on
# the socket, passes any C-to-C plug whose overmould fits through it.
TUNNEL_WIDTH = 8.5  # X
TUNNEL_HEIGHT = 14  # Z

BELOW_PLUG = ADAPTER_HEIGHT - PLUG_LENGTH  # the collar's top above the bottom
SOCKET_Z = SOCKET_HEIGHT - BELOW_PLUG  # from the collar's top

# The floor's top sits high enough to leave MIN_SKIN under each pocket and
# tunnel.
FLOOR = MIN_SKIN + ADAPTER_DROP + max(BELOW_PLUG, -SOCKET_Z + TUNNEL_HEIGHT / 2)
DOCK_Y = WALL + SLOT_Y + BACK_WALL

SLOT_FRONT_Y = -DOCK_Y / 2 + WALL
SLOT_BACK_Y = SLOT_FRONT_Y + SLOT_Y
SLOT_CENTER_Y = (SLOT_FRONT_Y + SLOT_BACK_Y) / 2
PLUG_Y = SLOT_FRONT_Y + CLEARANCE_Y + PORT_FROM_EDGE
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

assert PLUG_Y + ADAPTER_LENGTH - PLUG_FROM_FRONT + POCKET_CLEARANCE < SLOT_BACK_Y, (
    "The adapter runs past the back of the slot, under the back wall"
)


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    """A box spanning the given ranges."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * Box(
        x1 - x0, y1 - y0, z1 - z0, align=BOTTOM
    )


def slot(clearance_x: float, clearance_y: float, depth: float) -> Part:
    """A slot for one bank, to subtract from a top face at (x, y, top). It
    runs down depth from there, with a lead-in at its mouth."""
    outline = RectangleRounded(
        BANK_THICKNESS + 2 * clearance_x, BANK_WIDTH + 2 * clearance_y, SLOT_RADIUS
    )
    # The lead-in widens at 45 degrees and carries on above the top face, so
    # that the cut never shares a face with it.
    shaft = Pos(0, 0, -depth) * extrude(outline, depth)
    lead_in = Pos(0, 0, -LEAD_IN) * extrude(outline, LEAD_IN + 1, taper=-45)
    return shaft + lead_in


def adapter_cut() -> Part:
    """The adapter's pocket and its cable's channel, to subtract with the
    plug's centre at (x, y) and the collar's top at z = 0."""
    half_x = ADAPTER_THICKNESS / 2 + POCKET_CLEARANCE
    to_back = ADAPTER_LENGTH - PLUG_FROM_FRONT
    pocket = box(
        -half_x,
        half_x,
        -PLUG_FROM_FRONT - POCKET_CLEARANCE,
        to_back + POCKET_CLEARANCE,
        -BELOW_PLUG,
        ADAPTER_DROP + 1,
    )
    # Under the slot the channel is open to the floor, which needs no bridge;
    # through the back wall it becomes a tunnel with a roof.
    half_x = TUNNEL_WIDTH / 2
    bottom = SOCKET_Z - TUNNEL_HEIGHT / 2
    to_slot_back = SLOT_BACK_Y - PLUG_Y
    channel = box(-half_x, half_x, to_back, to_slot_back, bottom, ADAPTER_DROP + 1)
    tunnel = box(
        -half_x,
        half_x,
        to_slot_back - 1,
        DOCK_Y,
        bottom,
        SOCKET_Z + TUNNEL_HEIGHT / 2,
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
        dock -= Pos(x, SLOT_CENTER_Y, height) * slot(
            CLEARANCE_X, CLEARANCE_Y, wall_height
        )
        dock -= Pos(x + PORT_X, PLUG_Y, FLOOR - ADAPTER_DROP) * adapter_cut()
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
    clearance_test -= Pos(x, y, TEST_HEIGHT) * slot(
        clearance, clearance, TEST_HEIGHT + 1
    )
    label_y = -test_y / 2 + TEST_LABEL_WALL / 2
    clearance_test -= engraving(f"{clearance}", x, label_y, TEST_HEIGHT)

if __name__ == "__main__":
    export(clearance_test, __file__, variant="clearance-test")
    export(single, __file__, variant="single")
    preview(dock, __file__)
    export(dock, __file__)
