# Caseta rack mount

![The left-hand mount from the front left and the back right](preview.png)

A corner rack mount for a Lutron Caseta Smart Bridge (L-BDG2), in the style
of a Philips Hue Bridge corner mount: an open tray with hexagon windows,
whose front wall carries on past one side as a 1U ear.

The ear screws to a rack post, and the tray sits beside the post. A wide
notch in the tray's back wall lets the power and Ethernet cables out. The ear
stands a full rack unit tall over the screws, then curves down to the walls.

## Status

Not yet test-fitted.

The bridge is 2.75 x 2.75 x 1.19 in (69.9 x 69.9 x 30.2 mm) by Lutron's
spec sheet; the pocket allows 1.5 mm around it, and the walls come up to its
top. The bridge's corner radius has not been measured: the pocket's corners
have an 8 mm radius, which fits any bridge corner of about 3 mm or more.

The ear's slots, wall thicknesses and window pattern match the Hue mount, so
this mount should fit wherever that one does. The slots are 10 x 7 mm, at the
EIA-310 hole heights (6.35, 22.225 and 38.1 mm up the unit), 10 mm out from
the side of the tray.

The Hue mount has recesses in its floor for that bridge's feet; this one has
a flat floor. Its wall tops are also square rather than lightly rounded.

## Outputs

`make caseta-rack-mount` writes, in `build/`:

- `caseta-rack-mount.stl` and `.step`: the left-hand mount, with three
  slots. Seen from the front, the ear is on the left of the tray.
- `caseta-rack-mount-right.stl` and `.step`: its mirror image.
- `caseta-rack-mount-2-hole.stl` and `-right-2-hole`: both hands with only
  the top and bottom slots.

## Printing

Print floor down, with no supports. The slots are 7 mm tall and bridge
cleanly. PETG, like the rack.
