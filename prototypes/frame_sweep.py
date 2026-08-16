"""[DEPRECATED - superseded by 05_frame_engineering.py, kept for reference]
Magic Mirror - Step 2: build the full frame as one swept body.

Requires: run 01_setup_parameters.py first (uses those user parameters).

What it builds:
  1. A rounded-rectangle sweep PATH on the XY plane -- the frame's
     centreline, sized from glass dims + clearances + frame width.
  2. A frame cross-section PROFILE on a plane perpendicular to the path:
       - solid rectangle frameWidth x frameDepth
       - glass slot cut into the inner face (glassT + glassClear wide,
         grooveDepth deep), near the front
       - LED channel cut into the front face (ledChW x ledChD)
  3. Sweeps profile along path -> one continuous frame body.

This produces the MASTER body. Splitting into printable pieces and
adding finger joints is Step 3 (done in the GUI or a later script) --
keeping the master clean makes every downstream change easier.

Coordinate notes: Fusion API lengths are in CM internally; user
parameters are read in cm via .value. All sketch math below is cm.
"""

import adsk.core, adsk.fusion, traceback


def p(design, name):
    """User parameter value in internal units (cm)."""
    prm = design.userParameters.itemByName(name)
    if not prm:
        raise RuntimeError(
            f"Missing user parameter '{name}'. Run 01_setup_parameters.py first.")
    return prm.value


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Open a Fusion design first.")
            return
        root = design.rootComponent
        if ui.messageBox("02 is DEPRECATED - 05_frame_engineering is the\n"
                         "real frame. Run 02 anyway?", "Deprecated",
                         adsk.core.MessageBoxButtonTypes.YesNoButtonType
                         ) != adsk.core.DialogResults.DialogYes:
            return

        # ---- read parameters (cm) ----
        glassH   = p(design, "glassH")
        glassW   = p(design, "glassW")
        glassT   = p(design, "glassT")
        clr      = p(design, "glassClear")
        fW       = p(design, "frameWidth")
        fD       = p(design, "frameDepth")
        cornerR  = p(design, "cornerR")
        groove   = p(design, "grooveDepth")
        ledW     = p(design, "ledChW")
        ledD     = p(design, "ledChD")

        # Path = centreline of the frame ring.
        # Inner opening must fit glass + clearance; centreline sits
        # frameWidth/2 outside the glass edge.
        innerW = glassW + clr
        innerH = glassH + clr
        pathW  = innerW + fW          # centreline rectangle width
        pathH  = innerH + fW          # centreline rectangle height
        pathR  = max(cornerR - fW / 2.0, 0.5)   # centreline corner radius

        # ---- 1) sweep path: rounded rectangle on XY plane ----
        sk_path = root.sketches.add(root.xYConstructionPlane)
        sk_path.name = "frame_path"
        lines = sk_path.sketchCurves.sketchLines
        arcs  = sk_path.sketchCurves.sketchArcs

        hw, hh, r = pathW / 2.0, pathH / 2.0, pathR
        P = adsk.core.Point3D.create

        # Straight segments (clockwise from top edge), gaps left for arcs
        seg = []
        seg.append(lines.addByTwoPoints(P(-hw + r,  hh, 0), P(hw - r,  hh, 0)))
        seg.append(lines.addByTwoPoints(P( hw, hh - r, 0), P(hw, -hh + r, 0)))
        seg.append(lines.addByTwoPoints(P( hw - r, -hh, 0), P(-hw + r, -hh, 0)))
        seg.append(lines.addByTwoPoints(P(-hw, -hh + r, 0), P(-hw,  hh - r, 0)))
        # Corner arcs (centre, start point, sweep angle)
        import math
        ang = math.pi / 2.0
        arcs.addByCenterStartSweep(P( hw - r,  hh - r, 0), P( hw - r,  hh, 0), -ang)
        arcs.addByCenterStartSweep(P( hw - r, -hh + r, 0), P( hw, -hh + r, 0), -ang)
        arcs.addByCenterStartSweep(P(-hw + r, -hh, 0) if False else P(-hw + r, -hh + r, 0), P(-hw + r, -hh, 0), -ang)
        arcs.addByCenterStartSweep(P(-hw + r,  hh - r, 0), P(-hw,  hh - r, 0), -ang)

        # Collect the closed path
        curves = adsk.core.ObjectCollection.create()
        for c in sk_path.sketchCurves:
            curves.add(c)
        path = root.features.createPath(curves.item(0), True)  # chained = True

        # ---- 2) profile sketch on a plane perpendicular to path start ----
        # Path starts on the top edge; a plane normal to it there is XZ-ish.
        # Simpler + robust: sketch on a construction plane through the top
        # edge midpoint, normal to the path (use "distance on path" plane).
        planes = root.constructionPlanes
        planeInput = planes.createInput()
        planeInput.setByDistanceOnPath(path, adsk.core.ValueInput.createByReal(0.0))
        profPlane = planes.add(planeInput)

        sk_prof = root.sketches.add(profPlane)
        sk_prof.name = "frame_profile"
        pl = sk_prof.sketchCurves.sketchLines

        # Local sketch axes: x runs along frame width (radial, +x = outward),
        # y runs along depth (+y = toward wall/back). Origin = path point.
        # Outer solid rectangle, centred on path in width, front face at y=0.
        x0, x1 = -fW / 2.0, fW / 2.0          # inner face .. outer face
        y0, y1 = 0.0, fD                       # front face .. back face
        pl.addTwoPointRectangle(P(x0, y0, 0), P(x1, y1, 0))

        # Glass slot: opens on inner face (x0), starts a wall back from front
        wall = p(design, "wallT")
        slotW = glassT + clr                   # slot width front-to-back
        gy0 = wall                             # slot front wall
        gy1 = wall + slotW
        pl.addTwoPointRectangle(P(x0, gy0, 0), P(x0 + groove, gy1, 0))

        # LED channel: opens on front face (y0), sits centred-outward
        led_x0 = x0 + groove + wall            # keep wall between slot & channel
        led_x1 = led_x0 + ledW
        pl.addTwoPointRectangle(P(led_x0, y0, 0), P(led_x1, y0 + ledD, 0))

        # The profile to sweep = outer rect minus the two cut rects.
        # Fusion computes closed profile regions; pick the big one that
        # is NOT inside either cutout.
        target = None
        best_area = -1.0
        for prof in sk_prof.profiles:
            props = prof.areaProperties()
            # choose largest region -- that's the frame solid with notches
            if props.area > best_area:
                best_area = props.area
                target = prof

        # ---- 3) sweep ----
        sweeps = root.features.sweepFeatures
        sw_in = sweeps.createInput(target, path,
                                   adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sw_in.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        sweep = sweeps.add(sw_in)
        sweep.bodies.item(0).name = "frame_master"

        ui.messageBox(
            "Frame master body created.\n\n"
            "Inspect: glass slot on inner face, LED channel on front.\n"
            "If a cutout landed on the wrong face, the profile-region "
            "auto-pick chose wrong -- tell Claude Code which face is "
            "wrong and iterate.\n\n"
            "Next: 03_test_coupon.py before printing anything big."
        )
    except Exception:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
