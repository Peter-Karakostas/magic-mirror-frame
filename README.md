# Magic Mirror - 3D models

Fusion 360 Python scripts that generate every printed part of the mirror
frame. Versions are tracked with git, not in file names.

Glass: Pilkington MirroView 730 x 505 x 6 mm. Monitor: debezeled Dell
S2721HN, portrait. Printer bed: 256 mm (pieces are kept to 250 mm or less,
except the beam halves and rear panel tiles at 251 mm).

## Scripts

Each script lives in a folder of the same name (Fusion requires that).

| Script | Run in | Builds |
|---|---|---|
| `setup_parameters` | new empty design, FIRST | user parameters (sizes) |
| `frame` | same design, after setup | 16 frame pieces, assembled in place |
| `frame_test_pair` | same design, after setup (instead of `frame`) | two-piece test section: joint, button, radar chamber, mains groove, bolt and screw points |
| `supports` | its own new design, or after `frame` to see it in place | monitor rest beam (2 halves) + top strap (2 halves) |
| `rear_panel` | its own new design | 6 rear panel tiles |

`frame_test_pair` runs `frame/frame.py` in test mode, so keep the two
folders side by side.

## Running

1. Fusion: Shift+S (Utilities > Add-Ins > Scripts and Add-Ins), add each
   folder with the + on the Scripts tab.
2. File > New Design. Run `setup_parameters`, then `frame` or
   `frame_test_pair`. Always a new design: setup fails in a design where
   the frame has already been built.
3. Check the dialog: it shows the script's date stamp and
   "Self-check: N operations, 0 failed". If it lists failed operations,
   do not print.
4. Export: right-click a body > Save As Mesh.

## Printing notes

- Print the test pair first; the pieces should push together by hand.
- Frame pieces print back face down. Poles, the front lip and the back
  step need supports from the plate.
- `rail_bottom_p2`: supports inside the button pocket (not plate-only).
- Poles: make them solid (100% modifier or 6 walls). Hole ends: 6 walls
  over the first 45 mm.
- Beam halves: flat on the back face, no supports; rotate 45 degrees if
  the slicer says they do not fit.

## Assembly notes

- Slow-cure epoxy on every seam except the two bottom-corner-to-side-rail
  seams. Those stay unglued (4x M3x12 lock screws each) so the bottom
  section comes off and the glass can drop out.
- Not yet proven in plastic: pole/lip fit, joint stiffness under load,
  and whether the radar works through the 4 mm carbon-fibre front wall.

## Open items

- Radar: when the new sensor arrives, test it behind the frame's front
  wall and behind the mirror glass. If the glass works, add a seat for it
  on the monitor beam; the frame chamber is the fallback.
- Printed diffusers, corner LED strip holders, blackout fabric clamps.

Everything before this layout (old numbered/versioned scripts, STLs for
the first frame) is in the archive folder next to this one.
