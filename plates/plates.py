"""Magic Mirror - mending plates: 16x printed straps (50x20x3mm, two
M3 clearance holes at +-20mm) that drop flush into the seam recesses
and screw into the pilot holes. Run in ANY fresh design (no parameters
needed). Print flat, 3 walls, any infill, PETG.

__VERSION__ = "v22-PROD-2026-08-17"
"""
import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent
        P = adsk.core.Point3D.create
        n = 0
        for row in range(4):
            for col in range(4):
                x0, y0 = col*6.0, row*3.0        # 10mm gaps in the grid
                sk = root.sketches.add(root.xYConstructionPlane)
                sk.sketchCurves.sketchLines.addTwoPointRectangle(
                    P(x0, y0, 0), P(x0+5.0, y0+2.0, 0))
                for hx in (x0+0.5, x0+4.5):      # holes 20mm off centre
                    sk.sketchCurves.sketchCircles.addByCenterRadius(
                        P(hx, y0+1.0, 0), 0.17)  # 3.4mm M3 clearance
                prof = max(sk.profiles, key=lambda q: q.areaProperties().area)
                ext = root.features.extrudeFeatures.addSimple(
                    prof, adsk.core.ValueInput.createByReal(0.3),
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                ext.bodies.item(0).name = f"plate_{n+1:02d}"; n += 1
        for sk in list(root.sketches):
            try: sk.deleteMe()
            except: pass
        app.activeViewport.fit()
        ui.messageBox(f"[v22-PROD] {n} mending plates built (50x20x3, "
                      "M3 holes at +-20mm).\nExport all, print flat, "
                      "PETG, 3 walls. Screws: M3x10.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
