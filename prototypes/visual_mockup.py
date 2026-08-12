"""Magic Mirror - Step 4 (visual): full-assembly mockup with stand-in bodies.

Self-contained: builds EVERYTHING as simple positioned solids so you can
see the complete sandwich - frame ring, glass, monitor, blackout panel,
button, camera pod, radar, PSU brick, Pi. Square corners and box shapes
(this is a mockup for visualisation + collision sanity, NOT the print
master - script 02 remains the real frame).

Run after 01_setup_parameters.py, ideally in a FRESH design (or it will
add bodies alongside whatever exists).

Coordinates: XY plane = the wall. Origin = mirror centre.
+Z points OUT of the wall toward the viewer.
Front face of frame at z = frameDepth; back (wall side) at z = 0.

After running, make it look real (manual, 2 minutes):
  Right-click each body > Appearances:
    glass      -> Glass > "Glass (Dark Grey)" or Mirror appearance
    frame_ring -> Plastic > matte dark grey
    monitor    -> Paint > black
    blackout   -> Paint > matte black
  Then try: Inspect > Section Analysis (slice through the sandwich),
  and the RENDER workspace (top-left dropdown) for a photoreal view.
"""

import adsk.core, adsk.fusion, traceback


def p(design, name):
    prm = design.userParameters.itemByName(name)
    if not prm:
        raise RuntimeError(f"Missing parameter '{name}' - run 01 first.")
    return prm.value


def box(root, name, x0, y0, z0, x1, y1, z1):
    """Axis-aligned solid box between two corners (cm)."""
    sk = root.sketches.add(root.xYConstructionPlane)
    P = adsk.core.Point3D.create
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P(x0, y0, 0), P(x1, y1, 0))
    prof = sk.profiles.item(0)
    ext = root.features.extrudeFeatures.createInput(
        prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.setTwoSidesExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(z1)),
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(-z0)))
    f = root.features.extrudeFeatures.add(ext)
    f.bodies.item(0).name = name
    return f.bodies.item(0)


def ring(root, name, ow, oh, iw, ih, z0, z1):
    """Rectangular ring (outer minus inner opening), extruded z0..z1."""
    sk = root.sketches.add(root.xYConstructionPlane)
    P = adsk.core.Point3D.create
    L = sk.sketchCurves.sketchLines
    L.addTwoPointRectangle(P(-ow/2, -oh/2, 0), P(ow/2, oh/2, 0))
    L.addTwoPointRectangle(P(-iw/2, -ih/2, 0), P(iw/2, ih/2, 0))
    # ring profile = the one whose area ~= outer - inner
    target, want = None, ow*oh - iw*ih
    for prof in sk.profiles:
        if abs(prof.areaProperties().area - want) < want * 0.05:
            target = prof
    if target is None:                       # fallback: largest
        target = max(sk.profiles, key=lambda q: q.areaProperties().area)
    ext = root.features.extrudeFeatures.createInput(
        target, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.setTwoSidesExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(z1)),
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(-z0)))
    f = root.features.extrudeFeatures.add(ext)
    f.bodies.item(0).name = name
    return f.bodies.item(0)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Open a design first.")
            return
        root = design.rootComponent

        gW, gH, gT = p(design,"glassW"), p(design,"glassH"), p(design,"glassT")
        clr        = p(design,"glassClear")
        fW, fD     = p(design,"frameWidth"), p(design,"frameDepth")
        wall       = p(design,"wallT")
        mW = p(design,"monActiveW") + p(design,"monBorderL") + p(design,"monBorderR")
        mH = p(design,"monActiveH") + p(design,"monBorderT") + p(design,"monBorderB")
        mD         = p(design,"monD")
        btnD       = p(design,"btnHoleD")

        innerW, innerH = gW + clr, gH + clr          # frame opening
        outerW, outerH = innerW + 2*fW, innerH + 2*fW

        # z stack (0 = wall side, +z = toward viewer)
        z_front       = fD                            # frame front face
        z_glass_front = fD - wall                     # glass behind front wall
        z_glass_back  = z_glass_front - gT
        z_mon_back    = z_glass_back - mD
        z_black       = z_mon_back                    # blackout at monitor rear

        # 1) frame ring
        ring(root, "frame_ring", outerW, outerH, innerW, innerH, 0.0, z_front)

        # 2) glass
        box(root, "glass", -gW/2, -gH/2, z_glass_back, gW/2, gH/2, z_glass_front)

        # 3) monitor - PORTRAIT orientation (mirror is portrait; a 27"
        # panel landscape is wider than the whole mirror). Chassis long
        # side runs vertically; display rotated 90 deg in software.
        pW, pH = mH, mW                       # portrait: width<->height
        box(root, "monitor", -pW/2, -pH/2, z_mon_back, pW/2, pH/2, z_glass_back)

        # 4) blackout panel v2: thin SHEET just behind the glass spanning
        # the full opening (light seal), with monitor-shaped opening and
        # a rearward COLLAR hugging the monitor's edges. Monitor's own
        # metal back seals the middle. Sheet stops 2cm short at the
        # bottom so the radar clip slides into the rail unobstructed.
        z_sheet_f = z_glass_back - 0.2            # 2mm behind glass
        z_sheet_b = z_sheet_f - 0.3               # 3mm material
        ring(root, "blackout_sheet", innerW, innerH - 2.0, pW, pH,
             z_sheet_b, z_sheet_f)
        # collar: hugs monitor sides from sheet back to monitor rear
        ring(root, "blackout_collar", pW + 0.8, pH + 0.8, pW, pH,
             z_mon_back, z_sheet_b)

        # 5) button: recessed IN the LED channel at bottom-centre.
        # Approximate channel centreline; head sits within channel depth.
        grv = p(design,"grooveDepth"); lsw = p(design,"ledSlotWall")
        chW = p(design,"ledChW"); chD = p(design,"ledChD")
        cyb = -(innerH/2 + grv + lsw + chW/2)
        skb = root.sketches.add(root.xYConstructionPlane)
        skb.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(0, cyb, 0), btnD/2)
        ext = root.features.extrudeFeatures.createInput(
            skb.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext.setTwoSidesExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(z_front - 0.2)),
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(-(z_front - chD - 0.5)))) 
        root.features.extrudeFeatures.add(ext).bodies.item(0).name = "button"

        # 6) small stand-ins: camera pod, radar, PSU brick, Pi 5
        box(root, "camera_pod", -1.5, gH/2 - 4.0, z_glass_back - 2.0,
            1.5, gH/2 - 1.0, z_glass_back)
        box(root, "radar_LD2410", 8.0 - 1.8, cyb - 0.5, z_front - wall - 1.0,
            8.0 + 1.8, cyb + 0.5, z_front - wall)
        box(root, "psu_brick", -innerW/2 + 1, -innerH/2 + 1, 0.5,
            -innerW/2 + 14, -innerH/2 + 6, 3.8)
        box(root, "raspberry_pi5", innerW/2 - 10, -3, 0.5,
            innerW/2 - 1, 3, 3.0)

        # fit whole assembly in view
        app.activeViewport.fit()

        ui.messageBox(
            "Full-assembly mockup built (9 stand-in bodies).\n\n"
            "Now: right-click bodies > Appearances (glass/plastic/paint),\n"
            "Inspect > Section Analysis to slice the sandwich,\n"
            "or switch to the RENDER workspace for photoreal.\n\n"
            "Square corners + boxes = deliberate simplification;\n"
            "script 02 remains the real printable frame."
        )
    except Exception:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
