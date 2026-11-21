"""Magic Mirror - frame: all frame pieces, assembled in place.

Run order, in a NEW EMPTY design every time:  setup_parameters -> frame.
(frame_test_pair builds only one short joint pair, from this same file.)

What it builds (17 bodies): 12 rail pieces, 4 corners, radar_window_cap.
  * Joints: every seam has 3 square poles (14 x 16 mm, 40 mm deep; 31 mm
    on the two mid seams of each side rail - bed limit) into 3 holes,
    plus a 2 mm lip all round the pole piece's end that slides over a
    step on the hole piece. No mending plates.
  * Service seams (bottom corner <-> side rail) are left unglued:
    4x M3x12 lock screws each, from the back into the poles. No inner
    lip there (the monitor-beam slot sits next to the seam).
  * Corners: glass slot + rounded LED channel bend (18 mm channel).
  * Bottom rail: closed at the back. Button pocket and radar chamber
    open through the top (cavity) face. LED wires drop through two wire
    slots into the button pocket. Mains lead: rounded groove 16 x 8 mm
    across the back, 160 mm right of centre.
  * Radar (35 x 7 mm LD2410 / LD2410B): chamber 45 x 22 mm, 145 mm
    right of centre; window through the front wall closed by the
    separate 1.5 mm cap - print radar_window_cap in PLAIN PETG/PLA.
  * Monitor rest beam seats: 10 mm slots in both side rails + four 8 mm
    foot sockets in the bottom rail, open to the rear (see supports).
  * Top rail: 6 cleat bolt points (M4 + captured nut) for an 18 inch
    Z-bar punched every inch: x = +-50.8, +-127.0, +-177.8 mm (two per
    top-rail piece, so the bar ties all three pieces together).

Every cut/join is volume-checked: the final dialog lists any operation
that did nothing. If that list is not empty, DO NOT PRINT.
All holes are box cuts or vertical cylinders drawn on the XY plane.
History of earlier versions: see git log and the archive folder.
"""
import adsk.core, adsk.fusion, traceback, math

__VERSION__ = "2026-11-21.2"
MODE = "FULL"        # "FULL" = whole frame.  "TEST" = one short joint pair.

# ---------------- joint constants (cm) ----------------
POLE_LEN      = 4.0    # corner seams + top/bottom rail seams
POLE_LEN_SIDE = 3.1    # the two mid seams of each side rail (bed limit)
POLE_CLR      = 0.03   # glue/fit clearance per side
POLE_ROOF     = 0.02   # extra on the hole roof (bridged layers sag)
SOCK_EXTRA    = 0.10   # hole is this much deeper than the pole
TIP_LEN, TIP_IN = 0.4, 0.05   # lead-in: last 4 mm of a pole is 0.5 mm slimmer/side
LIP_LEN, LIP_T = 0.5, 0.2     # ring lip: 5 mm past the seam, 2 mm thick
LIP_CLR, LIP_END = 0.015, 0.02  # 0.15 mm behind the side lips, 0.2 mm at the tip
LIP_CLR_Z = 0.025             # 0.25 mm under the front lip / over the back lip
LOCK_AT = (1.6, 3.1)          # lock screws: distance from the seam (cm)
# pole layouts: (r0, r1, z0, z1); r = distance from the rail's INNER face
LAY_W = ((0.6, 2.0, 0.9, 2.5), (4.0, 5.4, 0.9, 2.5), (2.3, 3.7, 3.6, 5.2))
LAY_N = ((1.7, 3.1, 0.9, 2.5), (4.1, 5.5, 0.9, 2.5), (2.9, 4.3, 3.6, 5.2))
SIDE_MID = 24.6        # length of the middle side-rail piece

# ---------------- monitor rest-beam seats (cm) ----------------
BEAM_Y0, BEAM_Y1 = -33.5, -30.25   # beam bar; top = monitor bottom edge
BEAM_Z1  = 5.3
SLOT_D   = 1.0         # side-rail slot depth
TAB_Y1, TAB_Z1 = -28.4, 3.0        # screw-tab recess above the slot
TAB_SCREW_Y = -29.3
LEG_X    = ((4.0, 7.0), (18.0, 21.5))   # beam feet (mirrored to -x)
LEG_D    = 0.8         # foot socket depth into the bottom rail
FIT      = 0.05        # clearance per side for the beam parts

# ---------------- bottom-rail services (cm) ----------------
BTN_BACK = 1.0         # solid rear wall behind the button pocket
RADAR_X  = 14.5
RADAR_HALF = 2.25      # chamber half-length (45 mm)
RADAR_TUN  = 1.6       # tunnel/window half-length (32 mm): board ends sit on the ledges
RADAR_R0, RADAR_R1 = 1.9, 2.65   # tunnel/window across the rail (7.5 mm)
CAP_T = 0.15           # window cap thickness
MAINS_X  = 16.0
# M4 cleat points, mirrored to -x (6 in total). All on a 1 inch grid
# from the centre (2, 5, 7 in) to match a Z-bar punched every inch.
CLEAT_X  = (5.08, 12.7, 17.78)
HPIL     = 0.26        # horizontal M3 pilot (square, box cut)


def p(design, name):
    prm = design.userParameters.itemByName(name)
    if not prm:
        raise RuntimeError(f"Missing parameter '{name}' - run setup_parameters first.")
    return prm.value


class B:
    """Box/cylinder builder + volume-checked boolean operations."""
    def __init__(self, root):
        self.root = root; self.n_ops = 0; self.failed = []

    def _ext(self, prof, z0, z1, op):
        ei = self.root.features.extrudeFeatures.createInput(prof, op)
        ei.setTwoSidesExtent(
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(max(z0, z1))),
            adsk.fusion.DistanceExtentDefinition.create(
                adsk.core.ValueInput.createByReal(-min(z0, z1))))
        return self.root.features.extrudeFeatures.add(ei)

    def box(self, x0, y0, z0, x1, y1, z1, name=None):
        sk = self.root.sketches.add(self.root.xYConstructionPlane)
        P = adsk.core.Point3D.create
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            P(min(x0, x1), min(y0, y1), 0), P(max(x0, x1), max(y0, y1), 0))
        f = self._ext(sk.profiles.item(0), z0, z1,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        if name: f.bodies.item(0).name = name
        return f.bodies.item(0)

    def cyl_z(self, cx, cy, z0, z1, d):
        sk = self.root.sketches.add(self.root.xYConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx, cy, 0), d/2)
        return self._ext(sk.profiles.item(0), z0, z1,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation).bodies.item(0)

    def _combine(self, target, tool, op, label, grow):
        self.n_ops += 1
        tname = target.name
        try:
            v0 = target.volume
            t = adsk.core.ObjectCollection.create(); t.add(tool)
            ci = self.root.features.combineFeatures.createInput(target, t)
            ci.operation = op
            self.root.features.combineFeatures.add(ci)
            v1 = target.volume
            ok = (v1 > v0 + 1e-6) if grow else (v1 < v0 - 1e-6)
            if not ok:
                self.failed.append(f"{label} on {tname}: no change")
        except Exception as e:
            self.failed.append(f"{label} on {tname}: ERROR {str(e)[:60]}")

    def join(self, target, tool, label="join"):
        self._combine(target, tool,
            adsk.fusion.FeatureOperations.JoinFeatureOperation, label, True)

    def cut(self, target, tool, label="cut"):
        self._combine(target, tool,
            adsk.fusion.FeatureOperations.CutFeatureOperation, label, False)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get(); ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design: ui.messageBox("Open a design first."); return
        root = design.rootComponent; b = B(root)

        # ---- read EVERY parameter first (parametric mode only) ----
        gW, gH, gT = p(design, "glassW"), p(design, "glassH"), p(design, "glassT")
        clr  = p(design, "glassClear"); fW = p(design, "frameWidth")
        fD   = p(design, "frameDepth"); wall = p(design, "wallT")
        R    = p(design, "cornerR");    grv  = p(design, "grooveDepth")
        chW  = p(design, "ledChW");     chD  = p(design, "ledChD")
        lsw  = p(design, "ledSlotWall")
        rebD = p(design, "rebateD");    rebW = p(design, "rebateW")
        btnD = p(design, "btnHoleD");   recD = p(design, "btnRecessD")
        pockW = p(design, "btnPockW");  nutC = p(design, "btnNutClear")
        passW = p(design, "cablePassW"); passH = p(design, "cablePassH")
        rbL  = p(design, "radarBoardL")
        cArm = p(design, "cornerArm")
        dgD  = p(design, "diffGrooveD"); dgH = p(design, "diffGrooveH")
        spD  = p(design, "supPilotD")
        gEng = p(design, "glassEng")

        if abs(chW - 1.8) > 1e-6:
            ui.messageBox(
                f"STOP [{__VERSION__}]: ledChW is {chW*10:.1f} mm, expected 18.0.\n"
                "Run setup_parameters in a new empty design first, then this script.")
            return

        # ---- all reads done -> direct modeling ----
        design.designType = adsk.fusion.DesignTypes.DirectDesignType

        iW, iH = gW - 2*gEng, gH - 2*gEng        # visible opening
        oW, oH = iW + 2*fW, iH + 2*fW
        cext = R + cArm
        z_front, z_ch_b = fD, fD - chD
        z_slot_f, z_slot_b = fD - wall, fD - wall - (gT + clr)
        limX, limY = oW/2 - cext, oH/2 - cext
        cutsX = [-limX, -limX/3, limX/3, limX]
        cutsY = [-limY, -SIDE_MID/2, SIDE_MID/2, limY]
        ch0, ch1 = grv + lsw, grv + lsw + chW     # channel walls (r)

        PCS = {}                                   # name -> body

        def rbox(axis, sign, a0, a1, r0, r1, z0, z1):
            """Box in rail coordinates: a = along the rail, r = outward
            from the rail's inner face."""
            if axis == 'x':
                return b.box(a0, sign*(iH/2 + r0), z0, a1, sign*(iH/2 + r1), z1)
            return b.box(sign*(iW/2 + r0), a0, z0, sign*(iW/2 + r1), a1, z1)

        def rcyl(axis, sign, a, r, z0, z1, d):
            if axis == 'x':
                return b.cyl_z(a, sign*(iH/2 + r), z0, z1, d)
            return b.cyl_z(sign*(iW/2 + r), a, z0, z1, d)

        def piece(name, cuts, pos):
            for i in range(len(cuts) - 1):
                if cuts[i] < pos < cuts[i+1]:
                    return PCS[f"{name}_p{i+1}"]
            raise RuntimeError(f"no piece of {name} at {pos}")

        # =============== RAILS ===============
        def rail(axis, sign, name, cuts):
            for i in range(len(cuts) - 1):
                a0, a1 = cuts[i], cuts[i+1]
                nm = f"{name}_p{i+1}"
                body = rbox(axis, sign, a0, a1, 0, fW, 0, fD)
                body.name = nm
                e0, e1 = a0 - 0.01, a1 + 0.01
                b.cut(body, rbox(axis, sign, e0, e1, -0.01, grv,
                                 z_slot_b, z_slot_f), "glass slot")
                b.cut(body, rbox(axis, sign, e0, e1, ch0, ch1,
                                 z_ch_b, z_front + 0.01), "LED channel")
                for gw in (ch0, ch1):
                    b.cut(body, rbox(axis, sign, e0, e1, gw - dgD, gw + dgD,
                                     z_front - 0.15 - dgH, z_front - 0.15),
                          "diffuser groove")
                b.cut(body, rbox(axis, sign, e0, e1, -0.01, rebW,
                                 -0.01, rebD), "rear rebate")
                PCS[nm] = body

        rail('x', +1, "rail_top", cutsX)
        rail('x', -1, "rail_bottom", cutsX)
        rail('y', +1, "rail_right", cutsY)
        rail('y', -1, "rail_left", cutsY)

        # =============== CORNERS ===============
        def corner(sx, sy, name):
            cx_o, cy_o = sx*oW/2, sy*oH/2
            cx_s, cy_s = sx*(oW/2 - cext), sy*(oH/2 - cext)
            cx_i, cy_i = sx*iW/2, sy*iH/2
            acx, acy = cx_o - sx*R, cy_o - sy*R
            sk = root.sketches.add(root.xYConstructionPlane)
            P = adsk.core.Point3D.create
            L = sk.sketchCurves.sketchLines
            A = sk.sketchCurves.sketchArcs
            L.addByTwoPoints(P(cx_s, cy_o, 0), P(acx, cy_o, 0))
            A.addByCenterStartSweep(P(acx, acy, 0), P(acx, cy_o, 0),
                                    -sx*sy*math.pi/2)
            L.addByTwoPoints(P(cx_o, acy, 0), P(cx_o, cy_s, 0))
            L.addByTwoPoints(P(cx_o, cy_s, 0), P(cx_i, cy_s, 0))
            L.addByTwoPoints(P(cx_i, cy_s, 0), P(cx_i, cy_i, 0))
            L.addByTwoPoints(P(cx_i, cy_i, 0), P(cx_s, cy_i, 0))
            L.addByTwoPoints(P(cx_s, cy_i, 0), P(cx_s, cy_o, 0))
            prof = max(sk.profiles, key=lambda q: q.areaProperties().area)
            body = b._ext(prof, 0, fD,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                ).bodies.item(0)
            body.name = name

            # glass slot: two legs + the corner square where they meet
            b.cut(body, b.box(cx_i, cy_s - sy*0.01, z_slot_b,
                              cx_i + sx*grv, cy_i + sy*0.01, z_slot_f),
                  "glass slot leg")
            b.cut(body, b.box(cx_s - sx*0.01, cy_i, z_slot_b,
                              cx_i + sx*0.01, cy_i + sy*grv, z_slot_f),
                  "glass slot leg")
            b.cut(body, b.box(cx_i, cy_i, z_slot_b,
                              cx_i + sx*grv, cy_i + sy*grv, z_slot_f),
                  "glass slot corner square")
            # LED channel: straight legs up to the bend + rounded sweep
            Px, Py = cx_i + sx*ch0, cy_i + sy*ch0
            b.cut(body, b.box(cx_s - sx*0.01, Py, z_ch_b,
                              Px + sx*0.01, Py + sy*chW, z_front + 0.01),
                  "channel leg")
            b.cut(body, b.box(Px, cy_s - sy*0.01, z_ch_b,
                              Px + sx*chW, Py + sy*0.01, z_front + 0.01),
                  "channel leg")
            for gw in (Py, Py + sy*chW):
                b.cut(body, b.box(cx_s - sx*0.01, gw - sy*dgD,
                                  z_front - 0.15 - dgH,
                                  Px + sx*0.01, gw + sy*dgD, z_front - 0.15),
                      "diffuser groove")
            for gw in (Px, Px + sx*chW):
                b.cut(body, b.box(gw - sx*dgD, cy_s - sy*0.01,
                                  z_front - 0.15 - dgH,
                                  gw + sx*dgD, Py + sy*0.01, z_front - 0.15),
                      "diffuser groove")
            skp = root.sketches.add(root.xYConstructionPlane)
            Lp = skp.sketchCurves.sketchLines
            Ap = skp.sketchCurves.sketchArcs
            Lp.addByTwoPoints(P(Px, Py, 0), P(Px + sx*chW, Py, 0))
            Ap.addByCenterStartSweep(P(Px, Py, 0), P(Px + sx*chW, Py, 0),
                                     sx*sy*math.pi/2)
            Lp.addByTwoPoints(P(Px, Py + sy*chW, 0), P(Px, Py, 0))
            prof = max(skp.profiles, key=lambda q: q.areaProperties().area)
            pie = b._ext(prof, z_ch_b, z_front + 0.01,
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                ).bodies.item(0)
            b.cut(body, pie, "channel rounded bend")

            # rear rebate along both inner edges + its corner square
            b.cut(body, b.box(cx_s - sx*0.01, cy_i, -0.01,
                              cx_i + sx*0.01, cy_i + sy*rebW, rebD), "rebate")
            b.cut(body, b.box(cx_i, cy_s - sy*0.01, -0.01,
                              cx_i + sx*rebW, cy_i + sy*0.01, rebD), "rebate")
            b.cut(body, b.box(cx_i, cy_i, -0.01,
                              cx_i + sx*rebW, cy_i + sy*rebW, rebD),
                  "rebate corner square")
            PCS[name] = body

        corner(+1, +1, "corner_TR"); corner(-1, +1, "corner_TL")
        corner(+1, -1, "corner_BR"); corner(-1, -1, "corner_BL")

        # =============== SEAMS: 3 POLES -> 3 HOLES ===============
        # (axis, sign, position, lower piece, upper piece,
        #  pole direction, layout, pole length, lock screws?)
        SEAMS = []
        def seams_x(sign, name, cl, cr, lay):
            c = cutsX
            SEAMS.append(('x', sign, c[0], cl, f"{name}_p1", +1, lay, POLE_LEN, False))
            SEAMS.append(('x', sign, c[1], f"{name}_p1", f"{name}_p2", -1, lay, POLE_LEN, False))
            SEAMS.append(('x', sign, c[2], f"{name}_p2", f"{name}_p3", +1, lay, POLE_LEN, False))
            SEAMS.append(('x', sign, c[3], f"{name}_p3", cr, -1, lay, POLE_LEN, False))
        def seams_y(sign, name, cb, ct):
            c = cutsY
            SEAMS.append(('y', sign, c[0], cb, f"{name}_p1", +1, LAY_N, POLE_LEN, True))
            SEAMS.append(('y', sign, c[1], f"{name}_p1", f"{name}_p2", +1, LAY_W, POLE_LEN_SIDE, False))
            SEAMS.append(('y', sign, c[2], f"{name}_p2", f"{name}_p3", -1, LAY_W, POLE_LEN_SIDE, False))
            SEAMS.append(('y', sign, c[3], f"{name}_p3", ct, -1, LAY_W, POLE_LEN, False))
        seams_x(+1, "rail_top", "corner_TL", "corner_TR", LAY_W)
        seams_x(-1, "rail_bottom", "corner_BL", "corner_BR", LAY_N)
        seams_y(+1, "rail_right", "corner_BR", "corner_TR")
        seams_y(-1, "rail_left", "corner_BL", "corner_TL")

        for axis, sign, a, lo, hi, d, lay, L, lock in SEAMS:
            carrier = PCS[lo] if d > 0 else PCS[hi]
            receiver = PCS[hi] if d > 0 else PCS[lo]
            for k, (r0, r1, z0, z1) in enumerate(lay):
                tag = f"pole {k+1} @ {axis}={a*10:.0f}"
                # pole body (rooted 2 mm inside its own piece)
                b.join(carrier, rbox(axis, sign, a - d*0.2,
                                     a + d*(L - TIP_LEN), r0, r1, z0, z1),
                       tag)
                # slimmer tip = lead-in
                b.join(carrier, rbox(axis, sign, a + d*(L - TIP_LEN - 0.05),
                                     a + d*L, r0 + TIP_IN, r1 - TIP_IN,
                                     z0 + TIP_IN, z1 - TIP_IN), tag + " tip")
                # matching hole
                b.cut(receiver, rbox(axis, sign, a - d*0.01,
                                     a + d*(L + SOCK_EXTRA),
                                     r0 - POLE_CLR, r1 + POLE_CLR,
                                     z0 - POLE_CLR, z1 + POLE_CLR + POLE_ROOF),
                      "hole for " + tag)
            # ---- RING LIP: 2 mm skin all round the pole piece's end,
            # matching step all round the hole piece's end ----
            a_in, a_out = a - d*0.2, a + d*LIP_LEN       # rooted 2 mm inside
            ring = [("outer", fW - LIP_T, fW, 0, fD),
                    ("back",  0, fW, 0, LIP_T),
                    ("front", 0, fW, fD - LIP_T, fD)]
            if not lock:
                ring.append(("inner", 0, LIP_T, 0, fD))
            for nm_, r0, r1, z0, z1 in ring:
                b.join(carrier, rbox(axis, sign, a_in, a_out, r0, r1, z0, z1),
                       f"{nm_} lip @ {axis}={a*10:.0f}")
            # re-open the section features through the lip (and through
            # its 2 mm root): glass slot, LED channel, grooves, rebate
            e0, e1 = a - d*0.21, a + d*(LIP_LEN + 0.01)
            if not lock:      # (no inner lip there -> nothing to re-open)
                b.cut(carrier, rbox(axis, sign, e0, e1, -0.01, grv,
                                    z_slot_b, z_slot_f), "lip: glass slot mouth")
            b.cut(carrier, rbox(axis, sign, e0, e1, ch0, ch1,
                                z_ch_b, z_front + 0.01), "lip: channel mouth")
            for gw in (ch0, ch1):
                b.cut(carrier, rbox(axis, sign, e0, e1, gw - dgD, gw + dgD,
                                    z_front - 0.15 - dgH, z_front - 0.15),
                      "lip: diffuser groove")
            b.cut(carrier, rbox(axis, sign, e0, e1, -0.01, rebW,
                                -0.01, rebD), "lip: rebate")
            s0, s1 = a - d*0.01, a + d*(LIP_LEN + LIP_END)
            b.cut(receiver, rbox(axis, sign, s0, s1, fW - LIP_T - LIP_CLR,
                                 fW + 0.01, -0.01, fD + 0.01),
                  f"step for outer lip @ {axis}={a*10:.0f}")
            b.cut(receiver, rbox(axis, sign, s0, s1, -0.01, fW + 0.01,
                                 -0.01, LIP_T + LIP_CLR_Z),
                  f"step for back lip @ {axis}={a*10:.0f}")
            b.cut(receiver, rbox(axis, sign, s0, s1, -0.01, fW + 0.01,
                                 fD - LIP_T - LIP_CLR_Z, fD + 0.01),
                  f"step for front lip @ {axis}={a*10:.0f}")
            if not lock:
                b.cut(receiver, rbox(axis, sign, s0, s1, -0.01,
                                     LIP_T + LIP_CLR, -0.01, fD + 0.01),
                      f"step for inner lip @ {axis}={a*10:.0f}")
            if lock:
                # SERVICE SEAM (bottom corner <-> side rail): left unglued.
                # M3x12 from the rear through the rail wall into the two
                # rear poles = removable shear pins.
                for (r0, r1, z0, z1), la in [(q, t) for q in lay[:2]
                                             for t in LOCK_AT]:
                    rc, al = (r0 + r1)/2, a + d*la
                    b.cut(receiver, rbox(axis, sign, al - 0.325, al + 0.325,
                                         rc - 0.325, rc + 0.325, -0.01, 0.5),
                          "lock screw head pocket")
                    b.cut(receiver, rcyl(axis, sign, al, rc, 0.45, z0, 0.34),
                          "lock screw clearance hole")
                    b.cut(carrier, rcyl(axis, sign, al, rc, z0 - 0.01,
                                        z1 + 0.01, 0.28),
                          "lock screw pilot in pole")

        # =============== BOTTOM RAIL SERVICES ===============
        bmid = PCS["rail_bottom_p2"]
        y_in = -iH/2
        cyc = -(iH/2 + (ch0 + ch1)/2)                 # channel centreline
        z_roof = z_ch_b - wall                        # pocket roof
        b.cut(bmid, b.cyl_z(0, cyc, z_ch_b - 0.01, z_front + 0.01, recD),
              "button head recess")
        b.cut(bmid, b.cyl_z(0, cyc, z_roof - 0.01, z_ch_b + 0.01, btnD),
              "button hole")
        # pocket: CLOSED at the rear (BTN_BACK solid), open only through
        # the inner face of the rail (towards the cavity)
        b.cut(bmid, b.box(-pockW/2, -(oH/2 - wall), BTN_BACK,
                          pockW/2, y_in + 0.01, z_roof),
              "button pocket (opens to cavity)")
        for s in (-1, 1):
            b.cut(bmid, b.box(s*nutC, cyc - passH/2, z_roof - 0.01,
                              s*(nutC + passW), cyc + passH/2, z_ch_b + 0.01),
                  "LED wire slot")

        # radar: chamber opening to the cavity (closed at the back),
        # tunnel up to the front wall, window through the front wall
        # with a recess for a separate plain-plastic cap.
        bR = piece("rail_bottom", cutsX, RADAR_X)
        b.cut(bR, rbox('x', -1, RADAR_X - RADAR_HALF, RADAR_X + RADAR_HALF,
                       -0.01, RADAR_R1, 3.4, 5.6),
              "radar chamber (opens to cavity)")
        b.cut(bR, rbox('x', -1, RADAR_X - RADAR_TUN, RADAR_X + RADAR_TUN,
                       RADAR_R0, RADAR_R1, 5.59, z_front + 0.01),
              "radar tunnel + window")
        b.cut(bR, rbox('x', -1, RADAR_X - RADAR_TUN - 0.2,
                       RADAR_X + RADAR_TUN + 0.2, RADAR_R0 - 0.15, RADAR_R1,
                       z_front - CAP_T, z_front + 0.01),
              "radar cap recess")
        cap = rbox('x', -1, RADAR_X - RADAR_TUN - 0.18,
                   RADAR_X + RADAR_TUN + 0.18, RADAR_R0 - 0.13,
                   RADAR_R1 - 0.02, z_front - CAP_T, z_front)
        cap.name = "radar_window_cap"

        # mains lead groove: 16 wide x 8 deep, rounded (4 stepped boxes),
        # rear face, from the cavity edge to the bottom outer edge
        bM = piece("rail_bottom", cutsX, MAINS_X)
        for hw, za, zb in ((0.80, -0.01, 0.2), (0.75, 0.19, 0.4),
                           (0.62, 0.39, 0.6), (0.40, 0.59, 0.8)):
            b.cut(bM, rbox('x', -1, MAINS_X - hw, MAINS_X + hw, -0.01,
                           fW + 0.01, za, zb), "mains groove step")

        # =============== MONITOR REST-BEAM SEATS ===============
        for sx, nm in ((+1, "rail_right_p1"), (-1, "rail_left_p1")):
            body = PCS[nm]
            # slot floor = beam underside exactly (the beam RESTS on it);
            # 1 mm play above
            b.cut(body, rbox('y', sx, BEAM_Y0, BEAM_Y1 + 2*FIT, -0.01,
                             SLOT_D, -0.01, BEAM_Z1 + FIT), "beam slot")
            b.cut(body, rbox('y', sx, BEAM_Y1, TAB_Y1 + 2*FIT, -0.01,
                             SLOT_D, -0.01, TAB_Z1 + FIT), "beam tab recess")
            b.cut(body, rcyl('y', sx, TAB_SCREW_Y, SLOT_D/2, TAB_Z1,
                             TAB_Z1 + 1.3, 0.28), "beam tab screw pilot")
        for s in (-1, 1):
            for x0, x1 in LEG_X:
                body = piece("rail_bottom", cutsX, s*(x0 + x1)/2)
                b.cut(body, rbox('x', -1, s*(x0 - FIT), s*(x1 + FIT), -0.01,
                                 LEG_D, -0.01, BEAM_Z1 + FIT),
                      "beam foot socket")

        # =============== SMALL FIXINGS ===============
        # top strap pilots
        for sx, nm in ((+1, "rail_right"), (-1, "rail_left")):
            b.cut(piece(nm, cutsY, 31.3),
                  rbox('y', sx, 31.3 - HPIL/2, 31.3 + HPIL/2, -0.01, 1.0,
                       3.0 - HPIL/2, 3.0 + HPIL/2), "strap pilot")
            # blackout pilots, side rails
            for hy in (-18.0, 0.0, 18.0):
                b.cut(piece(nm, cutsY, hy),
                      rbox('y', sx, hy - HPIL/2, hy + HPIL/2, -0.01, 1.0,
                           5.2 - HPIL/2, 5.2 + HPIL/2), "blackout pilot")
        for sy, nm in ((+1, "rail_top"), (-1, "rail_bottom")):
            for hx in (-10.0, 10.0):
                b.cut(piece(nm, cutsX, hx),
                      rbox('x', sy, hx - HPIL/2, hx + HPIL/2, -0.01, 1.0,
                           5.2 - HPIL/2, 5.2 + HPIL/2), "blackout pilot")
        # rear panel M3 pilots in the rebate ledge (same 12 positions as
        # the panel script expects)
        for axis, sign, nm, cuts, lim in (
                ('x', +1, "rail_top", cutsX, limX),
                ('x', -1, "rail_bottom", cutsX, limX),
                ('y', +1, "rail_right", cutsY, limY),
                ('y', -1, "rail_left", cutsY, limY)):
            for pos in (-lim*0.6, 0.0, lim*0.6):
                b.cut(piece(nm, cuts, pos),
                      rcyl(axis, sign, pos, rebW/2, -0.01, 0.8, 0.28),
                      "rear panel pilot")
        # cleat: M4 from the rear + captured-nut T-slot from the top edge
        hy = oH/2 - fW/2
        for s in (-1, 1):
            for cx in CLEAT_X:
                hx = s*cx
                body = piece("rail_top", cutsX, hx)
                b.cut(body, b.cyl_z(hx, hy, -0.01, 1.4, 0.45), "cleat M4 hole")
                b.cut(body, b.box(hx - 0.38, hy - 0.45, 0.8,
                                  hx + 0.38, oH/2 + 0.01, 1.15),
                      "cleat nut slot")

        # =============== TEST MODE: keep one short joint pair ===============
        keep = set(PCS.keys())
        if MODE == "TEST":
            ta, tb = PCS["rail_top_p2"], PCS["rail_top_p3"]
            b.cut(ta, b.box(-13.0, iH/2 - 1, -1, 2.5, oH/2 + 1, fD + 1),
                  "test trim")
            b.cut(tb, b.box(13.5, iH/2 - 1, -1, 24.0, oH/2 + 1, fD + 1),
                  "test trim")
            ta.name = "TEST_pole_piece"; tb.name = "TEST_hole_piece"
            keep = {"TEST_pole_piece", "TEST_hole_piece"}

        # =============== CLEANUP ===============
        for sk in list(root.sketches):
            try: sk.deleteMe()
            except:
                try: sk.isVisible = False
                except: pass
        for pl in root.constructionPlanes:
            try: pl.isVisible = False
            except: pass
        kept = 0
        for body in list(root.bRepBodies):
            if body.name in keep or (MODE != "TEST" and (
                    body.name.startswith("rail_")
                    or body.name.startswith("corner_")
                    or body.name == "radar_window_cap")):
                kept += 1
            else:
                try: body.deleteMe()
                except: pass

        app.activeViewport.fit()
        if b.failed:
            chk = ("SELF-CHECK FAILED - DO NOT PRINT. Send this list back:\n  "
                   + "\n  ".join(b.failed[:14]))
        else:
            chk = f"Self-check: {b.n_ops} cut/join operations, 0 failed."
        ui.messageBox(
            f"Frame [{__VERSION__}] mode {MODE}: {kept} bodies.\n"
            f"{chk}\n\n"
            f"LED channel {chW*10:.1f} mm wide. Poles 14x16 mm, "
            f"{POLE_LEN*10:.0f} mm deep ({POLE_LEN_SIDE*10:.0f} on side mid seams).\n"
            "Look for, before exporting:\n"
            " - corners: rounded channel bend, NO square notch\n"
            " - every seam: 3 poles + a 2 mm lip ALL ROUND on one piece,\n"
            "   3 holes + a step all round on the other. No plate recesses\n"
            " - bottom rail back face: solid, except the mains groove\n"
            " - bottom rail top face: button opening (middle piece),\n"
            "   radar chamber (45x22 mm opening), 4 beam foot sockets\n"
            " - bottom rail FRONT face: radar window + separate thin cap\n"
            "   (print radar_window_cap in plain PETG/PLA, not CF)\n"
            " - side rails, bottom end: beam slot + screw-tab recess\n"
            "Print ONE test pair (frame_test_pair) before the frame.")
    except Exception:
        if ui: ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
