# LX570 dash rail

A U-shaped accessory rail for the center speaker cover (55510-60040) of a
2008-2015 Lexus LX570, in the spirit of the
[Leather & Dirt dash mount](https://leatheranddirt.com/vehicle/2008-2015-lexus-lx570/dash-mount-2008-lexus-lx570/).

A T-slot runs along the middle of the U and opens out of both arm ends, so
T-bolt accessories such as a RAM track ball (RAP-B-354U-TRA1) slide in from
either end and around the corners. Counterbored holes beside the slot take
screws through the speaker cover.

## Status

Not yet test-fitted. The rail is 211 x 172 mm. The bottom is flat: the cover
is close enough to flat that the rail does not need to follow it.

The cover's underside measures 235 x 234 mm inside its walls. Two long ribs
run front to back 168 mm apart, and a moulding line runs across the back 28 mm
in from the rear wall. The rail's slot follows them: each arm's slot runs along
a rib and the base's slot along the moulding line, with the light sensor inside
the U. The holes come in six pairs, one hole either side of the slot, so a rib
or the moulding line passes between the holes of every pair. There is one pair
each side of the base and two along each arm, placed from a photo so that each
nut lands on flat plastic, clear of the clips, felt pads and speaker opening.

The base overlaps the rear edge of the 99 mm speaker opening slightly. Clearing
it would take either a notch in the base or a narrower rail, and so smaller
screws than M4; the overlap is small enough not to matter.

The arms end in semicircles, and the top outside edges have a 2 mm chamfer.

## Outputs

`make lx570-dash-rail` writes, in `build/`:

- `lx570-dash-rail.stl` and `.step`: the rail.
- `lx570-dash-rail-test.stl` and `.step`: one rear corner of the rail, about
  76 x 86 mm, with the slot open at both cut ends and two pairs of holes.
- `lx570-dash-rail-template.svg`: a full-size paper template of the rail.

## Before printing

1. Print the paper template at 100% and confirm its scale bar measures 50 mm.
   Lay it face up on the cover's underside with its dashed slot lines over
   the two ribs and the rear moulding line, and check that every hole has room
   for a washer and nut. The rail is symmetric left to right, so the template
   needs no mirroring on the underside.
2. Print the test piece in the rail's material. Slide a T-bolt in from each
   cut end and around the bend, and seat a screw head in each counterbore.

## Hardware

Per hole: an M4 or #8-32 pan head screw, a washer, and a nylon lock nut under
the cover. The screw passes through 6.5 mm of rail below the counterbore, then
the cover, washer and nut; about 16 mm (5/8") is a starting point, to confirm
once the cover's thickness is known.

## Installing

Mark the holes from the underside, where the ribs and moulding line show where
the rail belongs: tape the paper template on as above, mark through its hole
centres, and drill from below. Then bolt the rail on from the top.

## Printing

Print in ASA, or another material that holds its shape above 90 C: a dash in
the sun gets far hotter than PLA or PETG tolerates. Print flat, bottom down.
The slot's lip bridges the channel.
