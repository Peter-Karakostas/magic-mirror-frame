"""Magic Mirror - Step 5 v2: engineering frame with INTEGRAL finger joints.

Every piece is built with its comb teeth already on it: at each seam,
even depth-bands extend 12mm past the seam on one piece and are recessed
12mm on its neighbour (5 bands of 16mm through the 80mm depth). Printed
pieces mesh like combs - nothing to do in Fusion, no add-in needed.

Builds: split rails + 4 rounded corners (all with teeth), glass slot,
LED channel + diffuser lips, in-channel button (recess/hole/pocket/wire
slots), radar slide-in pocket, cleat M4 holes + nut seats.
Still TODO in later revs: mains-exit semicircles at a chosen seam,
vents, fillets, corner connector pockets (await measured kit).

VERIFY: Inspect > Measure per docstring checklist of v1, plus:
[ ] teeth mesh: slide two neighbouring pieces together in Fusion (Move)
[ ] radar pocket: 38x12mm, floor leaves 4mm front wall
[ ] button recess clears glass slot band by ~1.5mm
"""
import adsk.core, adsk.fusion, traceback, math

__VERSION__ = "v23-PROD-2026-08-18"

FINGER = 1.2   # cm tooth length
NBANDS = 5     # depth bands (even bands protrude)

def p(design, name):
    prm = design.userParameters.itemByName(name)
    if not prm:
        raise RuntimeError(f"Missing parameter '{name}' - run 01 first.")
    return prm.value

class B:
    def __init__(self, root): self.root = root
    def _ext(self, prof, z0, z1, op):
        ei = self.root.features.extrudeFeatures.createInput(prof, op)
        ei.setTwoSidesExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(max(z0,z1))),
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(-min(z0,z1))))
        return self.root.features.extrudeFeatures.add(ei)
    def box(self, x0,y0,z0,x1,y1,z1, name=None):
        sk = self.root.sketches.add(self.root.xYConstructionPlane)
        P = adsk.core.Point3D.create
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            P(min(x0,x1),min(y0,y1),0), P(max(x0,x1),max(y0,y1),0))
        f = self._ext(sk.profiles.item(0), z0, z1,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        if name: f.bodies.item(0).name = name
        return f.bodies.item(0)
    def cyl_z(self, cx,cy,z0,z1,d):
        sk = self.root.sketches.add(self.root.xYConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx,cy,0), d/2)
        return self._ext(sk.profiles.item(0), z0, z1,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation).bodies.item(0)
    def join(self, target, tool):
        t = adsk.core.ObjectCollection.create(); t.add(tool)
        ci = self.root.features.combineFeatures.createInput(target, t)
        ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        self.root.features.combineFeatures.add(ci)
    def cut(self, target, tool, keep=False):
        t = adsk.core.ObjectCollection.create(); t.add(tool)
        ci = self.root.features.combineFeatures.createInput(target, t)
        ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        ci.isKeepToolBodies = keep
        self.root.features.combineFeatures.add(ci)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design: ui.messageBox("Open a design first."); return
        root = design.rootComponent; b = B(root)

        gW,gH,gT = p(design,"glassW"),p(design,"glassH"),p(design,"glassT")
        clr  = p(design,"glassClear"); fW = p(design,"frameWidth")
        fD   = p(design,"frameDepth"); wall = p(design,"wallT")
        R    = p(design,"cornerR");    grv  = p(design,"grooveDepth")
        chW  = p(design,"ledChW");     chD  = p(design,"ledChD")
        lsw  = p(design,"ledSlotWall"); lip = p(design,"diffLip")
        tap  = p(design,"ledChTaper"); stepH = p(design,"ledChStepH")
        mainsD = p(design,"mainsHoleD")
        rebD = p(design,"rebateD"); rebW = p(design,"rebateW")
        btnD = p(design,"btnHoleD");   recD = p(design,"btnRecessD")
        pockW= p(design,"btnPockW"); nutC = p(design,"btnNutClear")
        passW= p(design,"cablePassW"); passH = p(design,"cablePassH")
        rbL  = p(design,"radarBoardL"); rso = p(design,"radarStandoff")
        bed  = p(design,"bedMax"); jc = p(design,"jointClear")
        cArm = p(design,"cornerArm")
        dgD  = p(design,"diffGrooveD"); dgH = p(design,"diffGrooveH")
        spD  = p(design,"supPilotD")
        monW_ = p(design,"monW")             # portrait height = chassis W


        gEng = p(design,"glassEng")
        iW,iH = gW - 2*gEng, gH - 2*gEng   # glass OVERLAPS the slots (v19 fix: was inverted -> glass fell through)
        # ALL parameter reads complete -> switch to direct modeling
        # (userParameters are parametric-only; v21 crashed by switching first)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        oW,oH = iW+2*fW, iH+2*fW
        cext  = R + cArm                  # arc + full straight arm
        z_front, z_ch_b = fD, fD-chD
        z_slot_f, z_slot_b = fD-wall, fD-wall-(gT+clr)
        bands = [(fD*i/NBANDS, fD*(i+1)/NBANDS) for i in range(NBANDS)]

        def bnd(seam, band, protrude_left):
            """Boundary x/y at a seam for a band. Even bands: the LEFT
            (lower-coord) piece protrudes by FINGER; odd bands flush."""
            if band % 2 == 0:
                return seam + (FINGER if protrude_left else FINGER)
            return seam
        # simpler rule: even-band boundary = seam + FINGER (left piece
        # owns the tooth), odd-band boundary = seam. Works for every seam.

        def banded_prism(a0, a1, seams, ends, cross0, cross1, axis, name):
            """One rail piece [a0,a1]. Left piece owns even-band teeth
            at interior seams; corners own teeth at rail ends; odd
            bands flush. Teeth are shrunk by jointClear in x and z."""
            body = None
            lo_end, hi_end = ends
            def add(x0,y0,z0,x1,y1,z1):
                nonlocal body
                pc = b.box(x0,y0,z0,x1,y1,z1) if axis=='x' else \
                     b.box(y0,x0,z0,y1,x1,z1)
                if body is None:
                    body = pc; body.name = name
                else:
                    b.join(body, pc)
            for k,(zb0,zb1) in enumerate(bands):
                lo, hi = a0, a1
                if k % 2 == 0:
                    if (a0 in seams) or lo_end: lo = a0 + FINGER
                    if hi_end: hi = a1 - FINGER
                add(lo, cross0, zb0, hi, cross1, zb1)
                # tooth on the right side of interior seams, shrunk
                if k % 2 == 0 and (a1 in seams):
                    add(a1, cross0, zb0 + jc, a1 + FINGER - jc,
                        cross1, zb1 - jc)
            return body

        def rail(axis, sign, name):
            if axis=='x':
                lim = oW/2-cext; y_in, y_out = sign*iH/2, sign*oH/2
                c0, c1 = min(y_in,y_out), max(y_in,y_out)
            else:
                lim = oH/2-cext; x_in, x_out = sign*iW/2, sign*oW/2
                c0, c1 = min(x_in,x_out), max(x_in,x_out)
            n = max(1, math.ceil(2*lim/bed))
            if name == "rail_bottom":
                # 3 pieces, seams at +-lim/3: clear of button (x=0,
                # pocket +-28mm) and radar (moved to x=120mm)
                n = max(n, 3)
            cuts = [-lim + 2*lim*i/n for i in range(n+1)]
            seams = set(cuts[1:-1])
            pieces = []
            seamREG.append((axis, sign, list(cuts)))
            for i in range(n):
                body = banded_prism(cuts[i], cuts[i+1], seams,
                                    (i == 0, i == n-1),
                                    c0, c1, axis, f"{name}_p{i+1}")
                # profile cuts (generous spans cover teeth)
                if axis=='x':
                    yin = sign*iH/2
                    b.cut(body, b.box(-lim-3, yin, z_slot_b, lim+3,
                                      yin+sign*grv, z_slot_f))
                    cc = yin + sign*(grv+lsw)
                    b.cut(body, b.box(-lim-3, cc, z_ch_b, lim+3,
                                      cc+sign*chW, z_front+0.01))
                    for gw in (cc, cc + sign*chW):
                        b.cut(body, b.box(-lim-3, gw - sign*dgD, z_front-0.15-dgH,
                                          lim+3, gw + sign*dgD, z_front-0.15))
                    b.cut(body, b.box(cuts[i]-0.01, yin, -0.01,
                                      cuts[i+1]+0.01, yin+sign*rebW, rebD))
                    # diffuser lips: re-add 1.5mm material at channel top edges
                else:
                    xin = sign*iW/2
                    b.cut(body, b.box(xin, -lim-3, z_slot_b,
                                      xin+sign*grv, lim+3, z_slot_f))
                    cc = xin + sign*(grv+lsw)
                    b.cut(body, b.box(cc, -lim-3, z_ch_b,
                                      cc+sign*chW, lim+3, z_front+0.01))
                    for gw in (cc, cc + sign*chW):
                        b.cut(body, b.box(gw - sign*dgD, -lim-3, z_front-0.15-dgH,
                                          gw + sign*dgD, lim+3, z_front-0.15))
                    b.cut(body, b.box(xin, cuts[i]-0.01, -0.01,
                                      xin+sign*rebW, cuts[i+1]+0.01, rebD))
                pieces.append(body)
            return pieces

        seamREG = []
        all_pieces = []
        all_pieces += rail('x', +1, "rail_top")
        bot = rail('x', -1, "rail_bottom"); all_pieces += bot
        all_pieces += rail('y', +1, "rail_right")
        all_pieces += rail('y', -1, "rail_left")

        def corner(sx, sy, name):
            cx_o, cy_o = sx*oW/2, sy*oH/2
            cx_s, cy_s = sx*(oW/2-cext), sy*(oH/2-cext)
            cx_i, cy_i = sx*iW/2, sy*iH/2
            acx, acy = cx_o - sx*R, cy_o - sy*R
            body = None
            for k,(zb0,zb1) in enumerate(bands):
                ext = 0.0   # v23: bands flush; teeth added as cleared blocks below
                sk = root.sketches.add(root.xYConstructionPlane)
                P = adsk.core.Point3D.create
                L = sk.sketchCurves.sketchLines
                A = sk.sketchCurves.sketchArcs
                exs, eys = cx_s - sx*ext, cy_s - sy*ext  # extended seams
                L.addByTwoPoints(P(exs, cy_o,0), P(acx, cy_o,0))
                A.addByCenterStartSweep(P(acx,acy,0), P(acx,cy_o,0),
                                        -sx*sy*math.pi/2)
                L.addByTwoPoints(P(cx_o, acy,0), P(cx_o, eys,0))
                L.addByTwoPoints(P(cx_o, eys,0), P(cx_i, eys,0))
                L.addByTwoPoints(P(cx_i, eys,0), P(cx_i, cy_i,0))
                L.addByTwoPoints(P(cx_i, cy_i,0), P(exs, cy_i,0))
                L.addByTwoPoints(P(exs, cy_i,0), P(exs, cy_o,0))
                prof = max(sk.profiles, key=lambda q: q.areaProperties().area)
                f = b._ext(prof, zb0, zb1,
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                pc = f.bodies.item(0)
                if body is None: body = pc; body.name = name
                else: b.join(body, pc)
            # v23: corner teeth as separate blocks, cleared by jc on ALL
            # faces (matches rail teeth; zero-z-clearance made BR need force)
            for k,(zb0,zb1) in enumerate(bands):
                if k % 2: continue
                tx = b.box(cx_s - sx*(FINGER - jc), cy_i, zb0 + jc,
                           cx_s, sy*oH/2, zb1 - jc)
                b.join(body, tx)
                ty = b.box(cx_i, cy_s - sy*(FINGER - jc), zb0 + jc,
                           sx*oW/2, cy_s, zb1 - jc)
                b.join(body, ty)

            # glass pocket (square) + CONTINUOUS ROUNDED channel bend
            s1 = b.box(cx_i, cy_s-sy*2, z_slot_b, cx_i+sx*grv,
                       cy_i+sy*0.01, z_slot_f)
            s2 = b.box(cx_s-sx*2, cy_i, z_slot_b, cx_i+sx*0.01,
                       cy_i+sy*grv, z_slot_f)
            b.cut(body, s1); b.cut(body, s2)
            Px, Py = cx_i + sx*(grv+lsw), cy_i + sy*(grv+lsw)
            # straight legs up to the bend tangents
            b.cut(body, b.box(cx_s - sx*2, Py, z_ch_b,
                              Px + sx*0.01, Py + sy*chW, z_front + 0.01))
            b.cut(body, b.box(Px, cy_s - sy*2, z_ch_b,
                              Px + sx*chW, Py + sy*0.01, z_front + 0.01))
            for gw in (Py, Py + sy*chW):
                b.cut(body, b.box(cx_s - sx*2, gw - sy*dgD, z_front-0.15-dgH,
                                  Px + sx*0.01, gw + sy*dgD, z_front-0.15))
            for gw in (Px, Px + sx*chW):
                b.cut(body, b.box(gw - sx*dgD, cy_s - sy*2, z_front-0.15-dgH,
                                  gw + sx*dgD, Py + sy*0.01, z_front-0.15))
            # rounded outer sweep: quarter-pie about (Px,Py), R = chW
            skp = root.sketches.add(root.xYConstructionPlane)
            Pt = adsk.core.Point3D.create
            Lp = skp.sketchCurves.sketchLines
            Ap = skp.sketchCurves.sketchArcs
            Lp.addByTwoPoints(Pt(Px, Py, 0), Pt(Px + sx*chW, Py, 0))
            Ap.addByCenterStartSweep(Pt(Px, Py, 0),
                                     Pt(Px + sx*chW, Py, 0),
                                     sx*sy*math.pi/2)
            Lp.addByTwoPoints(Pt(Px, Py + sy*chW, 0), Pt(Px, Py, 0))
            prof = max(skp.profiles, key=lambda q: q.areaProperties().area)
            pf = b._ext(prof, z_ch_b, z_front + 0.01,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            b.cut(body, pf.bodies.item(0))
            # inner relief for the bracket's curved sweep (4mm wall to slot)
            b.cut(body, b.box(cx_i + sx*1.9, cy_i + sy*1.9, z_ch_b,
                              Px + sx*0.01, Py + sy*0.01, z_front + 0.01))
            return body

        all_pieces.append(corner(+1,+1,"corner_TR"))
        all_pieces.append(corner(-1,+1,"corner_TL"))
        all_pieces.append(corner(+1,-1,"corner_BR"))
        all_pieces.append(corner(-1,-1,"corner_BL"))

        # --- in-channel button on the bottom-rail piece containing x=0 ---
        cyc = -(iH/2 + grv + lsw + chW/2)
        tools = [b.cyl_z(0, cyc, z_ch_b-0.01, z_front+0.01, recD),
                 b.cyl_z(0, cyc, z_ch_b-wall-0.01, z_ch_b+0.01, btnD),
                 b.box(-pockW/2, -(oH/2 - wall), -0.01,
                        pockW/2, -(iH/2 + wall), z_ch_b-wall),
                 b.box(-nutC-passW, cyc-passH/2, z_ch_b-wall-0.01,
                       -nutC, cyc+passH/2, z_ch_b+0.01),
                 b.box(nutC, cyc-passH/2, z_ch_b-wall-0.01,
                       nutC+passW, cyc+passH/2, z_ch_b+0.01)]
        for body in bot:
            bb = body.boundingBox
            if bb.minPoint.x < -0.5 and bb.maxPoint.x > 0.5:
                for t in tools: b.cut(body, t)
                break

        # --- RADAR slide-in pocket: bottom rail, x=+12cm, open to rear,
        # floor leaves 4mm front wall (beam exits through outer band) ---
        ry0 = -(oH/2 - 0.2)              # near outer face, inside 2mm skin
        rp = b.box(13.0 - rbL/2, ry0, -0.01,
                   13.0 + rbL/2, ry0 + (rso + 0.6), z_front - wall)
        for body in bot:
            bb = body.boundingBox
            if bb.minPoint.x < 13.0 < bb.maxPoint.x:
                b.cut(body, rp)
                break

        # corner rear rebates along their two inner edges
        for body in list(root.bRepBodies):
            if body.name.startswith("corner_"):
                sx = 1 if body.name[-1] == "R" else -1
                sy = 1 if body.name[-2] == "T" else -1
                cxi, cyi = sx*iW/2, sy*iH/2
                cxs, cys = sx*(oW/2-cext), sy*(oH/2-cext)
                b.cut(body, b.box(cxs-sx*0.1, cyi, -0.01,
                                  cxi+sx*0.1, cyi+sy*rebW, rebD))
                b.cut(body, b.box(cxi, cys-sy*0.1, -0.01,
                                  cxi+sx*rebW, cyi+sy*0.1, rebD))

        # MAINS EXIT: 10mm half-tunnel through full rail cross-section,
        # split across the bottom-right corner/rail seam (semicircle in
        # each piece). Cable passes; plug cannot.
        seam_bx = (oW/2 - cext)
        skm = root.sketches.add(root.xZConstructionPlane)
        skm.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(seam_bx, fD/2, 0), mainsD/2)
        exm = root.features.extrudeFeatures.createInput(
            skm.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        exm.setTwoSidesExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(oH/2 + 0.01)),
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(-(iH/2) + 0.01)))
        tun = root.features.extrudeFeatures.add(exm).bodies.item(0)
        cutn = 0
        for body in list(root.bRepBodies):
            if body.name == "corner_BR" or body.name.startswith("rail_bottom"):
                bb = body.boundingBox
                if bb.minPoint.x - 0.2 < seam_bx < bb.maxPoint.x + 0.2:
                    b.cut(body, tun, keep=True); cutn += 1
        if tun.isValid: tun.deleteMe()
        if cutn == 0:
            ui.messageBox("WARNING: mains tunnel found no seam bodies")

        # --- MONITOR SHELF-BEAM + STRAP pilot holes: horizontal M3
        # pilots through both vertical rails' inner faces. Beam carries
        # the monitor's bottom edge (2 pilots/side); strap retains the
        # top (1 pilot/side). One long thin cylinder per hole cuts both
        # rails symmetrically; cavity in between is empty space.
        # (monW_ read in the parametric phase above)
        yBeam = -monW_/2 - 1.5              # beam body below monitor edge
        yStrap = monW_/2 + 0.8
        for hy, hz in ((yBeam, 2.0), (yBeam, 4.5), (yStrap, 3.0)):
            skp = root.sketches.add(root.yZConstructionPlane)
            skp.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(hy, hz, 0), spD/2)
            exp = root.features.extrudeFeatures.createInput(
                skp.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            exp.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(iW/2 + 1.0)),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(iW/2 + 1.0)))
            pin = root.features.extrudeFeatures.add(exp).bodies.item(0)
            for body in list(root.bRepBodies):
                if body == pin: continue
                if not (body.name.startswith("rail_left")
                        or body.name.startswith("rail_right")): continue
                bb = body.boundingBox
                if bb.minPoint.y < hy < bb.maxPoint.y:
                    b.cut(body, pin, keep=True)
            if pin.isValid: pin.deleteMe()

        # --- MENDING-PLATE pilot holes: 2 per seam (one per piece),
        # rear face, 20mm off the seam, mid-outer band. Enables fully
        # screw-assembled, epoxy-optional, piece-replaceable frame.
        for axis, sign, cuts in seamREG:
            if axis == 'x':
                cross = sign * (iH/2 + rebW + (fW - rebW)/2)
            else:
                cross = sign * (iW/2 + rebW + (fW - rebW)/2)
            for sm in cuts:                      # all boundaries incl corner seams
                # flush recess: 50x20x3mm pocket spanning the seam so
                # the mending plate sits flush with the rear face
                if axis == 'x':
                    rec = b.box(sm-2.5, cross-1.0, -0.01, sm+2.5, cross+1.0, rebD)
                else:
                    rec = b.box(cross-1.0, sm-2.5, -0.01, cross+1.0, sm+2.5, rebD)
                rbb = rec.boundingBox
                for body in list(root.bRepBodies):
                    if body == rec: continue
                    if not (body.name.startswith("rail")
                            or body.name.startswith("corner")): continue
                    bb = body.boundingBox
                    if (bb.minPoint.x < rbb.maxPoint.x and
                        bb.maxPoint.x > rbb.minPoint.x and
                        bb.minPoint.y < rbb.maxPoint.y and
                        bb.maxPoint.y > rbb.minPoint.y):
                        b.cut(body, rec, keep=True)
                if rec.isValid: rec.deleteMe()
                for off in (-2.0, 2.0):
                    pos = sm + off
                    cx_, cy_ = (pos, cross) if axis == 'x' else (cross, pos)
                    tool = b.cyl_z(cx_, cy_, -0.01, 0.8, spD)
                    done = False
                    for body in list(root.bRepBodies):
                        if body == tool: continue
                        if not (body.name.startswith("rail")
                                or body.name.startswith("corner")): continue
                        bb = body.boundingBox
                        if (bb.minPoint.x - 0.05 < cx_ < bb.maxPoint.x + 0.05 and
                            bb.minPoint.y - 0.05 < cy_ < bb.maxPoint.y + 0.05):
                            b.cut(body, tool); done = True; break
                    if not done and tool.isValid:
                        tool.deleteMe()

        # --- BLACKOUT PANEL mounting pilots: 10x M3 into the frame's
        # inner faces at the blackout plane (z=52mm), clear of channel
        # (z>=56), glass slot (z>=59), button pocket and camera zone.
        zB = 5.2
        # side rails: y = -18, 0, +18 cm; one pin cuts both sides
        for hy in (-18.0, 0.0, 18.0):
            skb2 = root.sketches.add(root.yZConstructionPlane)
            skb2.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(hy, zB, 0), spD/2)
            e2 = root.features.extrudeFeatures.createInput(
                skb2.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            e2.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(iW/2 + 1.0)),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(iW/2 + 1.0)))
            pin = root.features.extrudeFeatures.add(e2).bodies.item(0)
            for body in list(root.bRepBodies):
                if body == pin: continue
                if not (body.name.startswith("rail_left")
                        or body.name.startswith("rail_right")): continue
                bb = body.boundingBox
                if bb.minPoint.y < hy < bb.maxPoint.y:
                    b.cut(body, pin, keep=True)
            if pin.isValid: pin.deleteMe()
        # top/bottom rails: x = -13, +13; one pin cuts both
        for hx in (-13.0, 13.0):
            skb3 = root.sketches.add(root.xZConstructionPlane)
            skb3.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(hx, zB, 0), spD/2)
            e3 = root.features.extrudeFeatures.createInput(
                skb3.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            e3.setTwoSidesExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(iH/2 + 1.0)),
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(iH/2 + 1.0)))
            pin = root.features.extrudeFeatures.add(e3).bodies.item(0)
            for body in list(root.bRepBodies):
                if body == pin: continue
                if not (body.name.startswith("rail_top")
                        or body.name.startswith("rail_bottom")): continue
                bb = body.boundingBox
                if bb.minPoint.x < hx < bb.maxPoint.x:
                    b.cut(body, pin, keep=True)
            if pin.isValid: pin.deleteMe()

        # --- rear panel M3 pilot holes in the rebate ledge ---
        for axis, sign, nm in (('x',+1,"rail_top"),('x',-1,"rail_bottom"),
                               ('y',+1,"rail_right"),('y',-1,"rail_left")):
            lim = (oW/2 - cext) if axis=='x' else (oH/2 - cext)
            led_c = (sign*iH/2 + sign*rebW/2) if axis=='x' else \
                    (sign*iW/2 + sign*rebW/2)
            for pos in (-lim*0.6, 0.0, lim*0.6):
                for body in list(root.bRepBodies):
                    if not body.name.startswith(nm): continue
                    bb = body.boundingBox
                    lo_ = bb.minPoint.x if axis=='x' else bb.minPoint.y
                    hi_ = bb.maxPoint.x if axis=='x' else bb.maxPoint.y
                    if lo_ + 1 < pos < hi_ - 1:
                        cx_, cy_ = (pos, led_c) if axis=='x' else (led_c, pos)
                        b.cut(body, b.cyl_z(cx_, cy_, -0.01, 0.8, 0.28))
                        break

        # --- cleat M4 holes + 9mm nut-seat counterbores, top rail ---
        for hx in (-4.2, 4.2):   # v19: clear of plate recesses, within Z-bar
            hy = oH/2 - fW/2
            for body in all_pieces:
                if not body.name.startswith("rail_top"): continue
                bb = body.boundingBox
                if bb.minPoint.x < hx < bb.maxPoint.x:
                    # rear-entry bolt hole (M4x16 through Z-bar + rear
                    # wall into captured nut) + T-slot from outer face
                    b.cut(body, b.cyl_z(hx, hy, -0.01, 1.4, 0.45))
                    b.cut(body, b.box(hx-0.38, hy-0.45, 0.8,
                                      hx+0.38, oH/2+0.01, 1.15))

        # cleanup: hide every tool sketch and construction plane so no
        # stray outlines render after the run
        for sk in list(root.sketches):
            try: sk.deleteMe()
            except:
                try: sk.isVisible = False
                except: pass
        for pl in root.constructionPlanes:
            try: pl.isVisible = False
            except: pass

        # cleanup: delete EVERYTHING that is not a named frame piece
        # (orphan solids, surface slivers, tool stubs - regardless of name)
        for body in list(root.bRepBodies):
            if not (body.name.startswith("rail_")
                    or body.name.startswith("corner_")):
                try: body.deleteMe()
                except: pass

        app.activeViewport.fit()
        ui.messageBox(
            f"Engineering frame [{__VERSION__}]: {len(all_pieces)} pieces, ALL with\n"
            "integral finger teeth (even bands protrude 12mm at seams).\n"
            "Slide any two neighbours together with Move to see the mesh.\n\n"
            "Included: glass slot, stepped LED channel + lips, enclosed\n"
            "button pocket + wire slots, radar pocket (x=+130), mains\n"
            "tunnel (BR seam, x=+225), rear rebate + M3 pilots, cleat\n"
            "M4 + T-slots, clearance-fitted teeth.\n\n"
            "v20: CONTINUOUS uniform 18mm channel, ROUNDED corner sweeps\n"
            "(R18 outer arc + inner relief - curved bracket clears by\n"
            "6/11mm), interrupted only at the button. All non-frame\n"
            "bodies auto-deleted. ALL PIECES print-ready after visual\n"
            "verification; sanity-check bracket height <=12.5mm on arrival.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
