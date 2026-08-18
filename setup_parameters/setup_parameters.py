"""Magic Mirror - Step 1: create/update all user parameters.

Run inside Fusion 360: Utilities > Add-Ins > Scripts > + > pick this file > Run.
Safe to re-run: existing parameters are updated, not duplicated.

PLACEHOLDER values are marked; replace them once measured, then re-run.
"""

import adsk.core, adsk.fusion, traceback

__VERSION__ = "v25-PROD-2026-08-18"

# name: (expression_mm, comment)
PARAMS = {
    # --- Glass: Pilkington MirroView 75/20 (VERIFY with tape/calipers) ---
    "glassH":        ("730 mm",  "Glass height NOMINAL - use largest measured"),
    "glassW":        ("505 mm",  "Glass width NOMINAL - use largest measured"),
    "glassT":        ("6 mm",    "6mm nominal - caliper at 4 edge midpoints"),
    "glassClear":    ("1.0 mm",  "Slot thickness clearance (front-back, 0.5/side)"),
    "glassEng":      ("10 mm",   "Glass engagement per side into 15mm slots (v19: opening = glass - 2x this; was inverted!)"),

    # --- Frame profile ---
    "frameDepth":    ("70 mm",   "MEASURED: monitor+PSU 42, mains plug 47 (right-angle lead ordered) -> 60mm cavity"),
    "frameWidth":    ("60 mm",   "Frame width (60 + R25 + lsw20: curved BOXPUT clears glass slot)"),
    "wallT":         ("4 mm",    "Structural wall thickness"),
    "cornerR":       ("25 mm",   "Corner radius (reduced per curved-bracket clearance)"),
    "cornerArm":     ("50 mm",   "Straight arm past the arc on each corner piece (seam kept off the curve)"),
    "diffGrooveD":   ("1.2 mm",  "Diffuser retention groove depth into each channel wall"),
    "diffGrooveH":   ("2 mm",    "Diffuser groove height (1.5mm below front face)"),
    "grooveDepth":   ("15 mm",   "Glass seat depth"),

    # --- LED (BTF FCOB addressable WS2811/WS2814, 10mm strip, FLAT-mounted,
    #     L-corner connectors -> square light path inside rounded exterior) ---
    "ledChW":        ("13 mm",   "Channel width: 10mm strip + 1.5mm/side (coupon v1: shadowed at 11)"),
    "ledChD":        ("14 mm",   "Deep channel: connector fully hidden + 9-10mm LED-to-diffuser gap (kills hotspots)"),
    "brkPockLen":    ("72 mm",   "BOXPUT fold-bracket pocket leg length (64.5 + margin)"),
    "brkPockWiden":  ("5 mm",    "Corner pocket inner widening (channel 13->18mm, wall to slot 4mm)"),
    "diffLip":       ("1.5 mm",  "Cover clip lip - FINAL GEOMETRY PENDING bought cover model"),
    "ledChTaper":    ("1 mm",    "Channel narrows this much per side toward front (grips strip)"),
    "ledChStepH":    ("7 mm",    "Lower tier: connector/bracket body sits fully below upper tier"),
    "mainsHoleD":    ("10 mm",   "Mains cable exit tunnel dia - seam-split at BR corner"),
    "rebateD":       ("3 mm",    "Rear panel rebate depth (panel sits flush)"),
    "rebateW":       ("10 mm",   "Rear panel rebate ledge width"),
    "ledSlotWall":   ("15 mm",   "Slot-to-channel wall (v20 uniform-channel geometry)"),
    "btnRecessD":    ("26 mm",   "Widened channel opening for button head"),
    "btnPockW":      ("56 mm",   "Service pocket (W=H): nut, fingers, JST room (coupon v1)"),
    "btnNutClear":   ("17 mm",   "Wire slots start this far from button centre (clear of nut seat)"),
    "cablePassW":    ("10 mm",   "Wire slot length (radial)"),
    "cablePassH":    ("9 mm",    "Wire slot height - fits JST pre-fitted (coupon v1: too small)"),

    # --- Button: 22mm momentary metal, 3-8V white ring ---
    "btnHoleD":      ("22.3 mm", "22mm barrel + print clearance - coupon test"),
    "btnBossD":      ("32 mm",   "Inner-face boss diameter (nut seat)"),
    "btnBossH":      ("3 mm",    "Boss height"),
    "btnAccess":     ("40 mm",   "Clear space behind boss for nut access"),

    # --- LD2410 radar (bottom rail; VERIFY exact board mm of your variant) ---
    "supPilotD":     ("2.8 mm",  "M3 pilot dia for monitor beam/strap ends"),
    "monEdgeT":      ("20 mm",   "PLACEHOLDER monitor bottom-edge thickness - sets beam groove width"),
    "radarBoardL":   ("35 mm",   "PLACEHOLDER board length - measure"),
    "radarBoardW":   ("7 mm",    "PLACEHOLDER board width - measure"),
    "radarStandoff": ("4 mm",    "Antenna face gap from inner front wall (3-5mm)"),

    # --- Pi Camera pod (VERIFY camera version -> barrel dia) ---
    "camLensD":      ("12 mm",   "PLACEHOLDER lens barrel dia - measure module"),
    "camFloat":      ("2.5 mm",  "Sprung carriage front-back float"),
    "camShieldH":    ("5 mm",    "Light-shield collar height at glass contact"),

    # --- Monitor: debezeled Dell S2721HN (bare panel) ---
    "monActiveW":    ("597.9 mm","FIXED - 27in 16:9 active area width"),
    "monActiveH":    ("336.3 mm","FIXED - 27in 16:9 active area height"),
    "monBorderL":    ("6 mm",    "PLACEHOLDER left chassis border - caliper"),
    "monBorderR":    ("6 mm",    "PLACEHOLDER right chassis border - caliper"),
    "monBorderT":    ("6 mm",    "PLACEHOLDER top chassis border - caliper"),
    "monBorderB":    ("12 mm",   "PLACEHOLDER bottom border (driver board edge)"),
    "monW":          ("monActiveW + monBorderL + monBorderR", "DERIVED chassis width"),
    "monH":          ("monActiveH + monBorderT + monBorderB", "DERIVED chassis height"),
    "monD":          ("42 mm",   "MEASURED at PSU shield box; panel elsewhere ~15-20mm"),

    # --- Vents ---
    "ventSlotL":     ("40 mm",   "Vent slot length, top+bottom rear lips"),
    "ventSlotW":     ("4 mm",    "Vent slot width"),
    "ventPitch":     ("60 mm",   "Spacing between vent slots"),

    # --- Joinery / printing ---
    "jointClear":    ("0.4 mm",  "Joint clearance/side (coupon v1: 0.25 needed hammering; loose+epoxy > tight)"),
    "fingerLen":     ("12 mm",   "Finger joint finger length"),
    "filletR":       ("2.5 mm",  "Internal corner fillet radius - EVERY inside corner"),
    "bedMax":        ("250 mm",  "Usable print length per piece (X2D)"),
}


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Open a Fusion design first, then run this script.")
            return

        ups = design.userParameters
        created, updated = 0, 0
        for name, (expr, comment) in PARAMS.items():
            existing = ups.itemByName(name)
            if existing:
                existing.expression = expr
                existing.comment = comment
                updated += 1
            else:
                ups.add(name, adsk.core.ValueInput.createByString(expr),
                        "mm", comment)
                created += 1

        ui.messageBox(
            "Magic Mirror parameters ready. [" + __VERSION__ + "]\n"
            f"Created: {created}   Updated: {updated}\n\n"
            "PLACEHOLDERS still to measure:\n"
            "  monBorders (4), radarBoard, camLensD, cornerPock\n"
            "Edit them under Modify > Change Parameters, or edit this "
            "file and re-run."
        )
    except Exception:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
