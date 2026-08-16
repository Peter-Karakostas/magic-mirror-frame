# Magic Mirror — Fusion 360 script kit

Parametric starter kit for the Pilkington MirroView 75/20 build
(730 × 505 × 6 mm nominal — use measured actuals; coated side faces room).
Frame: eSUN PETG-CF dark grey, 60 mm rounded corners, edge-mounted COB
LED channel with printed diffusers, Bambu Lab X2D (256 mm bed).

## How to run a script in Fusion 360

1. Open Fusion, create/open a design (save it first).
2. Utilities tab → Add-Ins → Scripts and Add-Ins → Scripts tab → "+"
   → point it at this folder → select script → Run.
3. Run order: `01` → `02` (master frame) and/or `03` (test coupon).

## The scripts

| Script | What it does |
|---|---|
| `01_setup_parameters.py` | Creates/updates every user parameter. Re-runnable. |
| `02_frame_sweep.py` | (superseded by 05 - historical) |
| `05_frame_engineering.py` | THE frame: all pieces with integral finger teeth, button, radar pocket, cleat holes. |
| `04_visual_mockup.py` | Whole-assembly stand-in visualisation. |
| `03_test_coupon.py` | HYBRID all-features coupon (140mm): half button, half mains hole, finger teeth, M4+nut seat, radar pocket, channel+lips, glass slot. **Print TWO, first.** |

## Placeholders you must measure before trusting dimensions

- `glassT` — glass thickness
- `monW`, `monH`, `monD` — monitor incl. bezel; depth at the PSU bulge
- `ledChW`, `ledChD` — from your chosen COB strip's datasheet
- Button diameter (not yet parameterised — add when known)

Change values in Modify → Change Parameters (or edit `01` and re-run);
all geometry regenerates.

## What is deliberately NOT in these scripts yet

- Splitting the master into ≤250 mm printable pieces + finger joints
- Corner-seam cable passage (10 × 6 mm teardrop slot, split across
  the bottom-left joint)
- Monitor support arms, blackout panel, diffuser profile, Z-bar spine
- Vent slots top/bottom rails

Master-first is intentional: split geometry inherits every profile
change. Do splits as Step 4 once the coupon confirms the profile.

## Iterating with Claude Code

Keep this folder under git. When a script errors, paste the full
traceback to Claude Code; when Fusion builds something wrong (cutout on
the wrong face is the likely first bug — the profile-region auto-pick
in `02`/`03` is the fragile part), describe which face is wrong.
Ask Claude Code to refactor the shared profile into one module when the
duplication between 02/03 starts to bite.

## Print settings (structural pieces)

PETG-CF, dried 65 °C/8 h · hardened 0.4 or 0.6 nozzle · 4 walls ·
15 % Adaptive Cubic (top rail: 30 % + 100 % cleat modifier) · 5 shells · pieces lie flat on their back face ·
0.25 mm joint clearance to start · fillet every internal corner 2.5 mm.

## One design per script

Run each geometry script (03/04/05) in its OWN saved design, always
after 01. Mixing them stacks bodies at the origin into a mesh.
