"""Magic Mirror - Step 3 v2: HYBRID all-features test coupon.

TWO printable pieces (70mm each of bottom-rail profile) that MESH at a
real finger-joint seam - slide them together to feel the connection -
plus a snap-in diffuser clip. Together they carry every
feature to measure and fit-test in cheap PLA/PETG before CF printing:

  [ ] glass slot        - real glass slides in, light friction w/ foam
  [ ] LED channel+lips  - strip lies flat; diffuser blank snaps in
  [ ] HALF button       - recess/hole halved at LEFT end face: barrel
                          rests in the half-cup to verify diameter
  [ ] HALF mains hole   - 10mm semicircle on the LEFT end face through
                          the outer wall (the seam-split cable exit)
  [ ] wire slot         - one strip-end slot beside the button half
  [ ] FINGER JOINT      - pieces A and B mesh at the centre seam:
                          slide together by hand; tune jointClear until
                          firm-but-hand-tight, no mallet, no rattle
  [ ] M4 T-SLOT capture - slide M4 nut down the slot from the outer
                          face; drive M4x16 bolt in from the rear -
                          this is the real cleat/top-rail fastener
  [ ] radar pocket      - LD2410 board slides in from the back
  [ ] DIFFUSER CLIP     - separate 60mm body prints alongside: snap it
                          into the channel (legs flex, barbs click under
                          the lips). Should press in by thumb, hold with
                          a light rattle-free grip, and pry out by
                          lifting one long edge. Print it ON ITS SIDE so
                          the legs flex along layer lines, not across.
      NOTE: channel looks wider over the finger teeth - correct: the
      neighbouring piece's lips complete the line there when meshed.

Print flat on its back face (z=0 face down), 4 walls, 45% gyroid.
"""
import adsk.core, adsk.fusion, traceback

LEN = 14.0; FINGER = 1.2; NBANDS = 5

def p(design, name):
    prm = design.userParameters.itemByName(name)
    if not prm:
        raise RuntimeError(f"Missing '{name}' - run 01 first.")
    return prm.value

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design: ui.messageBox("Open a design first."); return
        root = design.rootComponent
        P = adsk.core.Point3D.create

        gT  = p(design,"glassT");  clr = p(design,"glassClear")
        fW  = p(design,"frameWidth"); fD = p(design,"frameDepth")
        wall= p(design,"wallT");   grv = p(design,"grooveDepth")
        chW = p(design,"ledChW");  chD = p(design,"ledChD")
        lsw = p(design,"ledSlotWall"); lip = p(design,"diffLip")
        tap = p(design,"ledChTaper"); stepH = p(design,"ledChStepH")
        rebD = p(design,"rebateD"); rebW = p(design,"rebateW")
        btnD= p(design,"btnHoleD"); recD = p(design,"btnRecessD")
        pockW=p(design,"btnPockW"); nutC=p(design,"btnNutClear")
        passW=p(design,"cablePassW"); passH=p(design,"cablePassH")
        rbL = p(design,"radarBoardL"); rso = p(design,"radarStandoff")

        z_front, z_ch_b = fD, fD-chD
        z_slot_f, z_slot_b = fD-wall, fD-wall-(gT+clr)
        bands = [(fD*i/NBANDS, fD*(i+1)/NBANDS) for i in range(NBANDS)]

        def extr(prof, z0, z1, op):
            ei = root.features.extrudeFeatures.createInput(prof, op)
            ei.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(z1)),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(-z0)))
            return root.features.extrudeFeatures.add(ei)
        def box(x0,y0,z0,x1,y1,z1):
            sk = root.sketches.add(root.xYConstructionPlane)
            sk.sketchCurves.sketchLines.addTwoPointRectangle(
                P(min(x0,x1),min(y0,y1),0), P(max(x0,x1),max(y0,y1),0))
            return extr(sk.profiles.item(0), min(z0,z1), max(z0,z1),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                ).bodies.item(0)
        def cyl(cx,cy,z0,z1,d):
            sk = root.sketches.add(root.xYConstructionPlane)
            sk.sketchCurves.sketchCircles.addByCenterRadius(P(cx,cy,0), d/2)
            return extr(sk.profiles.item(0), min(z0,z1), max(z0,z1),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                ).bodies.item(0)
        def join(t, tool):
            c = adsk.core.ObjectCollection.create(); c.add(tool)
            ci = root.features.combineFeatures.createInput(t, c)
            ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
            root.features.combineFeatures.add(ci)
        def cut(t, tool):
            c = adsk.core.ObjectCollection.create(); c.add(tool)
            ci = root.features.combineFeatures.createInput(t, c)
            ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
            root.features.combineFeatures.add(ci)

        # base: TWO pieces meshing at seam x=7cm. Even depth-bands of A
        # protrude FINGER past the seam; B's even bands recessed to match.
        SEAM = 7.0
        def banded(x_lo, x_hi, tooth_right, notch_left, name):
            body = None
            for k,(z0,z1) in enumerate(bands):
                lo = x_lo + (FINGER if (notch_left and k%2==0) else 0)
                hi = x_hi + (FINGER if (tooth_right and k%2==0) else 0)
                pc = box(lo, 0, z0, hi, fW, z1)
                if body is None: body = pc; body.name = name
                else: join(body, pc)
            return body
        A = banded(0, SEAM, True, False, "coupon_A")
        Bp = banded(SEAM, LEN, False, True, "coupon_B")

        def profile_cuts(body):
            cut(body, box(-0.1, 0, z_slot_b, LEN+FINGER+0.1, grv, z_slot_f))
            c0_ = grv + lsw
            cut(body, box(-0.1, c0_, z_ch_b, LEN+FINGER+0.1, c0_+chW,
                          z_ch_b+stepH))
            cut(body, box(-0.1, c0_+tap, z_ch_b+stepH, LEN+FINGER+0.1,
                          c0_+chW-tap, z_front+0.01))
            cut(body, box(-0.1, 0, -0.01, LEN+FINGER+0.1, rebW, rebD))
            bb = body.boundingBox
            join(body, box(bb.minPoint.x+0.01, c0_+tap, z_front-0.15,
                           bb.maxPoint.x-FINGER-0.01 if body.name=="coupon_A"
                           else bb.maxPoint.x-0.01, c0_+tap+lip, z_front))
            join(body, box(bb.minPoint.x+0.01, c0_+chW-tap-lip, z_front-0.15,
                           bb.maxPoint.x-FINGER-0.01 if body.name=="coupon_A"
                           else bb.maxPoint.x-0.01, c0_+chW-tap, z_front))
            return c0_
        c0 = profile_cuts(A)
        profile_cuts(Bp)

        cyc = c0 + chW/2
        cyc = c0 + chW/2
        # HALF button at LEFT end (centre on x=0 face -> half emerges)
        cut(A, cyl(0, cyc, z_ch_b-0.01, z_front+0.01, recD))
        cut(A, cyl(0, cyc, z_ch_b-wall-0.01, z_ch_b+0.01, btnD))
        cut(A, box(0-0.01, cyc-pockW/2, -0.01, pockW/2, cyc+pockW/2,
                      z_ch_b-wall))
        # wire slot right of the button half
        cut(A, box(nutC, cyc-passH/2, z_ch_b-wall-0.01,
                      nutC+passW, cyc+passH/2, z_ch_b+0.01))
        # HALF mains hole: 10mm semicircle on LEFT end, axis through the
        # outer wall band (y), i.e. horizontal cylinder along y
        skm = root.sketches.add(root.xZConstructionPlane)
        skm.sketchCurves.sketchCircles.addByCenterRadius(
            P(0, fD/2, 0), 0.5)
        em = root.features.extrudeFeatures.createInput(
            skm.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        em.setTwoSidesExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(-(0) + 0.01)),
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(fW + 0.01)))
        cut(A, root.features.extrudeFeatures.add(em).bodies.item(0))
        # M4 CLEAT FASTENER, as on the real top rail: bolt enters from
        # the REAR face (z=0), 14mm deep; nut slides down a T-slot cut
        # in from the OUTER face and captures at the hole. Test: slide
        # a real M4 nut down the slot, drive an M4x16 from the rear.
        hx, hy = 12.8, grv + lsw + chW + (fW-grv-lsw-chW)/2
        cut(Bp, cyl(hx, hy, -0.01, 1.4, 0.45))          # rear-entry hole
        cut(Bp, box(hx-0.38, hy-0.45, 0.8,               # nut T-slot
                    hx+0.38, fW+0.01, 1.15))
        # radar pocket from the rear, near outer face
        cut(Bp, box(8.2, fW-0.2-(rso+0.6), -0.01,
                      8.2+rbL, fW-0.2, z_front-wall))

        # --- diffuser test clip: 60mm section, placed beside the coupon.
        # Face plate rests ON the lips; legs drop through the lip gap;
        # barbs click under the lips. All boxes; snap flex is the legs.
        DL = 6.0                      # test length
        gap = chW - 2*lip             # opening between lips
        legT, legClr, barb = 0.15, 0.02, 0.06
        oy = fW + 2.0                 # park it beside the coupon
        plate = box(0, oy, 0.15, DL, oy + chW - 0.04, 0.30)
        dbody = plate; dbody.name = "diffuser_test_clip"
        legIn = oy + lip + legClr
        legOut = oy + chW - lip - legClr
        # legs hang below plate (printed upside-down here; slicer will lay
        # it on its side per docstring)
        join(dbody, box(0, legIn, -0.17, DL, legIn + legT, 0.16))
        join(dbody, box(0, legOut - legT, -0.17, DL, legOut, 0.16))
        # barbs at leg tips, protruding outward toward the lips
        join(dbody, box(0, legIn - barb, -0.17, DL, legIn, -0.07))
        join(dbody, box(0, legOut, -0.17, DL, legOut + barb, -0.07))

        app.activeViewport.fit()
        ui.messageBox(
            "TWO-PIECE coupon (mesh A into B at the seam!) + diffuser clip built. Export: right-click body > Save As Mesh.\n"
            "Print TWO to test the finger mesh. Work the checklist in\n"
            "this script's docstring with real glass/strip/button/board.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
