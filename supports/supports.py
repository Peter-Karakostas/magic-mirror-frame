"""Magic Mirror - monitor supports: shelf BEAM (2 halves) + top STRAP
(2 halves). Run in a FRESH design (no parameters needed - measured
values are constants below). Direct mode; export all 4 bodies.

MEASURED INPUTS (2026-08-27): monitor portrait 605x353mm, bottom edge
5mm thick for first 7mm of height, button strip intrudes one end
(wall relieved 100mm - place that half on the button-strip side),
connectors point rearward (clean shelf), PSU near top.

__VERSION__ = "v32-PROD-2026-08-27"
"""
import adsk.core, adsk.fusion, traceback

# ---- constants (cm) ----
SPAN   = 48.3      # opening 48.5 minus 2mm clearance
HALF   = SPAN/2
JC     = 0.04      # joint clearance (validated on frame teeth)
SHELF_Y = -30.25   # shelf top surface: monitor bottom edge height
BODY_Y0, BODY_Y1 = -33.5, SHELF_Y
BODY_Z0, BODY_Z1 = 1.5, 5.3     # rear face 15mm off rear plane
SHELF_Z1 = 5.79                 # shelf stops 1.1mm shy of glass (5.9)
WALL_Y1  = SHELF_Y + 0.6        # 6mm wall (thin-zone safe)
WALL_Z0  = 4.7                  # 6mm thick wall, face at 5.3
RELIEF   = 10.0                 # wall stops this far from one end
PLATE_T  = 0.4                  # end screw-plates
WIN_L    = 2.2                  # driver window length
HOLE_D   = 0.34                 # M3 clearance
BEAM_HOLES = ((-32.0/10, 2.0), (-32.0/10, 4.5))  # (y,z) - y in cm below
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

        def box(x0,y0,z0,x1,y1,z1):
            sk = root.sketches.add(root.xYConstructionPlane)
            sk.sketchCurves.sketchLines.addTwoPointRectangle(
                P(min(x0,x1),min(y0,y1),0), P(max(x0,x1),max(y0,y1),0))
            ei = root.features.extrudeFeatures.createInput(
                sk.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(max(z0,z1))),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(-min(z0,z1))))
            return root.features.extrudeFeatures.add(ei).bodies.item(0)

        def join(a,b_):
            t = adsk.core.ObjectCollection.create(); t.add(b_)
            ci = root.features.combineFeatures.createInput(a,t)
            ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            root.features.combineFeatures.add(ci)
        def cut(a,b_,keep=False):
            t = adsk.core.ObjectCollection.create(); t.add(b_)
            ci = root.features.combineFeatures.createInput(a,t)
            ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            ci.isKeepToolBodies = keep
            root.features.combineFeatures.add(ci)

        def support_half(x_out, name, y0, y1, z0, z1, shelf, holes, relief):
            """One half spanning x 0..x_out (sign gives side)."""
            s = 1 if x_out > 0 else -1
            b_ = box(0, y0, z0, x_out, y1, z1)
            b_.name = name
            if shelf:   # beam only: shelf ledge + wall
                join(b_, box(0, BODY_Y1-0.8, WALL_Z0, x_out, BODY_Y1, SHELF_Z1))
                # v32 CABLE HIGHWAY: clear the rear of the body between
                # the end zones -> 21mm gap behind beam (rear plane to
                # z=2.4), clearing the button passage (18mm) fully
                cut(b_, box(s*0.0, BODY_Y0-0.01, BODY_Z0-0.01,
                            x_out - s*3.0, BODY_Y1-0.8, 2.4))
                # v32 CABLE ARCHES: 20x8mm scallops on the bottom edge
                for ax in (4.0, 12.0, 20.0):
                    if ax < abs(x_out) - 3.2:
                        cut(b_, box(s*ax-1.0, BODY_Y0-0.01, 2.3,
                                    s*ax+1.0, BODY_Y0+0.8, 5.4))
                # v32 ZIP-TIE SLOTS: through-slots for strapping runs
                for zx in (8.0, 16.0):
                    if zx < abs(x_out) - 3.2:
                        cut(b_, box(s*zx-0.2, -31.6, 2.3,
                                    s*zx+0.2, -31.0, 5.4))
                wx1 = x_out - s*RELIEF if relief else x_out
                join(b_, box(0, BODY_Y1, WALL_Z0, wx1, WALL_Y1, 5.3))
            # centre finger joint: 3 vertical teeth on +x half, recesses on -x
            th = (y1-y0)/3
            for k in range(3):
                ty0, ty1 = y0+k*th, y0+(k+1)*th
                if s > 0 and k % 2 == 0:
                    join(b_, box(0, ty0+JC, z0+JC, -1.0+JC, ty1-JC, z1-JC))
                if s < 0 and k % 2 == 0:
                    cut(b_, box(0.01, ty0, z0-0.01, -1.0, ty1, z1+0.01))
            # end plate + driver window
            cut(b_, box(x_out - s*(PLATE_T+WIN_L), y0-0.01, z0+0.2,
                        x_out - s*PLATE_T, y1+0.01, z1-0.3))
            return b_

        halves = []
        halves.append(support_half(+HALF, "beam_relief_half",
            BODY_Y0, BODY_Y1, BODY_Z0, BODY_Z1, True, BEAM_HOLES, True))
        halves.append(support_half(-HALF, "beam_plain_half",
            BODY_Y0, BODY_Y1, BODY_Z0, BODY_Z1, True, BEAM_HOLES, False))
        halves.append(support_half(+HALF, "strap_half_A",
            STRAP_Y0, STRAP_Y1, STRAP_Z0, STRAP_Z1, False, [STRAP_HOLE], False))
        halves.append(support_half(-HALF, "strap_half_B",
            STRAP_Y0, STRAP_Y1, STRAP_Z0, STRAP_Z1, False, [STRAP_HOLE], False))

        # screw holes: symmetric full-span pins (verified pattern) through
        # both end plates at once
        for hy, hz in list(BEAM_HOLES) + [STRAP_HOLE]:
            sk = root.sketches.add(root.yZConstructionPlane)
            sk.sketchCurves.sketchCircles.addByCenterRadius(
                P(hy, hz, 0), HOLE_D/2)
            ei = root.features.extrudeFeatures.createInput(
                sk.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            ei.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(HALF+0.1)),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(HALF+0.1)))
            pin = root.features.extrudeFeatures.add(ei).bodies.item(0)
            for b_ in halves:
                bb = b_.boundingBox
                if bb.minPoint.y - 0.05 < hy < bb.maxPoint.y + 0.05:
                    cut(b_, pin, keep=True)
            if pin.isValid: pin.deleteMe()

        for sk in list(root.sketches):
            try: sk.deleteMe()
            except: pass
        app.activeViewport.fit()
        ui.messageBox(
            "[v31-PROD] Beam halves + strap halves built.\n"
            "Beam: shelf top -302.5 (605mm monitor centred), 6mm wall,\n"
            "relief 100mm on 'beam_relief_half' - install that half on\n"
            "the button-strip side. Screws M3x12 via end plates through\n"
            "driver windows. VERIFY: holes present in all 4 end plates,\n"
            "teeth mesh at centre, shelf/wall on beam halves only.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
