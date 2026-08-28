"""Magic Mirror - REAR PANEL: 6 tiles (2 cols x 3 rows), 3mm, flush in
the rebate, screwed to the 12 rebate pilots. Vent arrays throughout.
Fresh design, direct mode, no parameters. Box cuts only.

>>> MAINS_X below = distance (cm) from frame centre to the mains groove.
>>> 16.0 matches the modeled groove. IF YOUR GROOVE IS HAND-CUT
>>> ELSEWHERE, measure and change this number BEFORE running.

__VERSION__ = "v36-PROD-2026-08-28"
"""
import adsk.core, adsk.fusion, traceback

MAINS_X = 16.0          # cm from frame centre to mains groove centre
T       = 0.29          # tile thickness (0.1mm under the 3mm rebate)
PW, PH  = 50.2, 72.7    # panel outer (engages 8.5mm of the 10mm ledge)
COLS, ROWS = 2, 3
GAP     = 0.05          # clearance between tiles at seams
HOLE    = 0.18          # half-side of 3.6mm square screw holes
# rebate pilot positions from the frame model (cm):
PILOTS = [(-13.65, 36.0), (0.0, 36.0), (13.65, 36.0),
          (-13.65,-36.0), (0.0,-36.0), (13.65,-36.0),
          (-24.75, 20.4), (-24.75, 0.0), (-24.75,-20.4),
          ( 24.75, 20.4), ( 24.75, 0.0), ( 24.75,-20.4)]

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
        def cut(a,b_):
            t = adsk.core.ObjectCollection.create(); t.add(b_)
            ci = root.features.combineFeatures.createInput(a,t)
            ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            root.features.combineFeatures.add(ci)

        cw, rh = PW/COLS, PH/ROWS
        made = 0
        for r in range(ROWS):
            for c in range(COLS):
                x0 = -PW/2 + c*cw + (GAP if c>0 else 0)
                x1 = -PW/2 + (c+1)*cw - (GAP if c<COLS-1 else 0)
                y0 = -PH/2 + r*rh + (GAP if r>0 else 0)
                y1 = -PH/2 + (r+1)*rh - (GAP if r<ROWS-1 else 0)
                b_ = box(x0,y0,0, x1,y1,T)
                b_.name = f"panel_r{r+1}_c{c+1}"
                # screw holes (half-holes where a pilot sits on a seam)
                for px,py in PILOTS:
                    if x0-0.19 < px < x1+0.19 and y0-0.19 < py < y1+0.19:
                        cut(b_, box(px-HOLE, py-HOLE, -0.01,
                                    px+HOLE, py+HOLE, T+0.01))
                # vent slots: grid of 40x5mm in the tile's central zone
                vx = x0+3.0
                while vx + 4.0 < x1-3.0:
                    vy = y0+4.0
                    while vy + 0.5 < y1-4.0:
                        cut(b_, box(vx, vy, -0.01, vx+4.0, vy+0.5, T+0.01))
                        vy += 2.0
                    vx += 6.0
                # mains notch: bottom edge tile crossing MAINS_X
                if r == 0 and x0 < MAINS_X < x1:
                    cut(b_, box(MAINS_X-0.85, y0-0.01, -0.01,
                                MAINS_X+0.85, y0+1.2, T+0.01))
                made += 1
        for sk in list(root.sketches):
            try: sk.deleteMe()
            except: pass
        app.activeViewport.fit()
        ui.messageBox(f"[v36-PROD] {made} panel tiles built. Tiles are\n"
            f"{cw*10:.0f}x{rh*10:.0f}mm (fit the X2D's 256mm bed; small\n"
            "brim). VERIFY: square screw holes align over the 12 pilot\n"
            "positions, half-holes on the centre seam, mains notch at\n"
            f"x={MAINS_X*10:.0f}mm bottom edge, vents everywhere.\n"
            "PRINT ONE TILE FIRST and test-fit before the other five.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
