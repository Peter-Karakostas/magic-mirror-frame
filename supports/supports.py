"""Magic Mirror - supports: monitor rest beam + top strap.

Run in a FRESH design (no parameters needed). Builds 4 bodies:
  beam_relief_half, beam_plain_half  - the REST BEAM the monitor sits on
  strap_half_A, strap_half_B         - top strap (hook slot + M3)

REST BEAM - drops into the frame from behind, no side screws:
  * each end has a 10 mm tongue that sits in the slot in the side rail
  * two feet per half stand in 8 mm sockets in the bottom rail
    (feet at 40-70 and 180-215 mm from centre: clear of the button
    opening, radar slot and mains groove)
  * one M3x12 per end, driven straight in from the back through the
    thin tab above the tongue
  * between the feet the beam is open underneath (20 mm high) and the
    whole 21 mm behind the beam is free for cables
  * prints flat on its back face, no supports. 251 mm long: if the
    slicer says it does not fit, rotate it 45 degrees on the plate.
The relief half (lip stops 100 mm short) goes on the monitor's
button-strip side, as before.

Only fits the pole-joint frame (frame.py), not the first printed frame.
"""
import adsk.core, adsk.fusion, traceback

__VERSION__ = "2026-11-21"

# ---- constants (cm) - must match frame/frame.py ----
IN_X    = 24.25            # side rail inner face (opening 485)
IN_Y    = -35.5            # bottom rail inner face
GAP     = 0.1              # beam body stops 1 mm short of the rail face
TONGUE  = 0.9              # tongue length inside the 10 mm slot
BEAM_Y0, BEAM_Y1 = -33.5, -30.25   # bar; top = monitor bottom edge
Z0, Z1  = 2.4, 5.3         # bar back / front (glass back is 5.9)
SHELF_Z1 = 5.79            # shelf ledge stops 1.1 mm shy of the glass
LIP_Y1  = BEAM_Y1 + 0.6    # 6 mm lip behind the monitor's bottom edge
RELIEF  = 10.0             # lip stops this far from one end
LEG_X   = ((4.0, 7.0), (18.0, 21.5))
LEG_Y0  = IN_Y - 0.8                   # foot bottom = socket floor (8 deep)
TAB_X0  = 23.4
TAB_Y1  = -28.4
TAB_Z1  = 3.0
TAB_SCREW = (IN_X + 0.5, -29.3)        # matches the pilot in the rail
CENTRE_GAP = 0.02

# ---- top strap ----
SPAN = 48.3; HALF = SPAN/2; JC = 0.04
PLATE_T = 0.4; WIN_L = 2.2
STRAP_Y0, STRAP_Y1 = 30.4, 32.4
STRAP_Z0, STRAP_Z1 = 2.6, 5.35
STRAP_HOLE = (31.3, 3.0)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent
        P = adsk.core.Point3D.create
        failed = []

        def box(x0, y0, z0, x1, y1, z1):
            sk = root.sketches.add(root.xYConstructionPlane)
            sk.sketchCurves.sketchLines.addTwoPointRectangle(
                P(min(x0, x1), min(y0, y1), 0), P(max(x0, x1), max(y0, y1), 0))
            ei = root.features.extrudeFeatures.createInput(
                sk.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(max(z0, z1))),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(-min(z0, z1))))
            return root.features.extrudeFeatures.add(ei).bodies.item(0)

        def _comb(a, b_, op, label, grow):
            nm = a.name
            try:
                v0 = a.volume
                t = adsk.core.ObjectCollection.create(); t.add(b_)
                ci = root.features.combineFeatures.createInput(a, t)
                ci.operation = op
                root.features.combineFeatures.add(ci)
                v1 = a.volume
                if not ((v1 > v0 + 1e-6) if grow else (v1 < v0 - 1e-6)):
                    failed.append(f"{label} on {nm}: no change")
            except Exception as e:
                failed.append(f"{label} on {nm}: ERROR {str(e)[:60]}")
        def join(a, b_, label="join"):
            _comb(a, b_, adsk.fusion.FeatureOperations.JoinFeatureOperation,
                  label, True)
        def cut(a, b_, label="cut"):
            _comb(a, b_, adsk.fusion.FeatureOperations.CutFeatureOperation,
                  label, False)

        # ------------------------------------------------ REST BEAM
        def beam_half(s, name, relief):
            xin = s*CENTRE_GAP
            xb  = s*(IN_X - GAP)               # body end
            xt  = s*(IN_X + TONGUE)            # tongue end
            # bar + tongue (one box, same section)
            b_ = box(xin, BEAM_Y0, Z0, xt, BEAM_Y1, Z1)
            b_.name = name
            # shelf ledge towards the glass (not inside the slot)
            join(b_, box(xin, BEAM_Y1 - 0.8, Z1 - 0.01, xb, BEAM_Y1, SHELF_Z1),
                 "shelf ledge")
            # lip behind the monitor's bottom edge
            wx = s*(IN_X - GAP - (RELIEF if relief else 0.0))
            join(b_, box(xin, BEAM_Y1 - 0.01, Z0, wx, LIP_Y1, Z1), "lip")
            # feet
            for x0, x1 in LEG_X:
                join(b_, box(s*x0, LEG_Y0, Z0, s*x1, BEAM_Y0 + 0.01, Z1),
                     "foot")
            # screw tab above the tongue (thin, at the back) + M3 hole
            join(b_, box(s*TAB_X0, BEAM_Y1 - 0.01, Z0, xt, TAB_Y1, TAB_Z1),
                 "screw tab")
            tx, ty = s*TAB_SCREW[0], TAB_SCREW[1]
            cut(b_, box(tx - 0.18, ty - 0.18, Z0 - 0.01,
                        tx + 0.18, ty + 0.18, TAB_Z1 + 0.01), "tab screw hole")
            # zip-tie slots through the bar
            for zx in (10.0, 15.0):
                cut(b_, box(s*zx - 0.2, -32.2, Z0 - 0.01,
                            s*zx + 0.2, -31.6, Z1 + 0.01), "zip-tie slot")
            return b_

        # ------------------------------------------------ TOP STRAP
        def strap_half(x_out, name):
            s = 1 if x_out > 0 else -1
            y0, y1, z0, z1 = STRAP_Y0, STRAP_Y1, STRAP_Z0, STRAP_Z1
            b_ = box(0, y0, z0, x_out, y1, z1)
            b_.name = name
            th = (y1 - y0)/3
            for k in range(3):
                ty0, ty1 = y0 + k*th, y0 + (k+1)*th
                if s > 0 and k % 2 == 0:
                    join(b_, box(0, ty0 + JC, z0 + JC, -1.0 + JC, ty1 - JC,
                                 z1 - JC), "strap tooth")
                if s < 0 and k % 2 == 0:
                    cut(b_, box(0.01, ty0, z0 - 0.01, -1.0, ty1, z1 + 0.01),
                        "strap tooth recess")
            cut(b_, box(x_out - s*(PLATE_T + WIN_L), y0 - 0.01, z0 + 0.2,
                        x_out - s*PLATE_T, y1 + 0.01, z1 - 0.3),
                "driver window")
            hy, hz = STRAP_HOLE
            # hook slot: open upward - pre-set the screw, lower strap on
            cut(b_, box(x_out - s*(PLATE_T + 0.05), hy - 0.18, hz - 0.18,
                        x_out + s*0.05, y1 + 0.01, hz + 0.18), "hook slot")
            return b_

        beam_half(+1, "beam_relief_half", True)
        beam_half(-1, "beam_plain_half", False)
        strap_half(+HALF, "strap_half_A")
        strap_half(-HALF, "strap_half_B")

        for sk in list(root.sketches):
            try: sk.deleteMe()
            except: pass
        app.activeViewport.fit()
        chk = ("SELF-CHECK FAILED - DO NOT PRINT:\n  " + "\n  ".join(failed)
               if failed else "Self-check: 0 failed operations.")
        ui.messageBox(
            f"Supports [{__VERSION__}]\n{chk}\n\n"
            "Rest beam: 2 halves. Each has an end tongue (side-rail slot),\n"
            "2 feet (bottom-rail sockets) and a thin tab with one M3 hole.\n"
            "Drops in from the back; relief half on the button-strip side.\n"
            "Strap halves: hook slot + M3.\n"
            "Print beams flat on the back face; rotate 45 deg if too long.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
