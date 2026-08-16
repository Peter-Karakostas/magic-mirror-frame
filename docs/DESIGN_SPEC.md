# Magic Mirror — Casing Design Spec v2

Full redesign incorporating: rounded corners, edge-mounted addressable COB
strip + printed diffusers, LD2410 radar in bottom rail, Pi Camera glass-
contact pod, 22mm illuminated button, seam-split cable passages, vents,
Z-bar spine. PENDING: monitor W/H/D + PSU pattern, power-strip envelope.

## 1. Frame ("husk")

- Material: eSUN PETG-CF dark grey. 4 walls, 0.2mm layers. TWO-TIER
  INFILL: standard pieces 15% Adaptive Cubic (walls are the strength;
  ~40% filament saving, less warp); TOP RAIL pieces 30% gyroid + 100%
  modifier volume at cleat spine. Test prints: 3 walls / 8% / 3 shells
  ("Test - lightweight" preset) - never for final parts.
  printed flat on back face, hardened 0.4/0.6 nozzle, dried 65°C/8h.
- Profile (subject to monitor depth): 40mm face width × 80mm depth,
  4mm walls, closed-box with internal glass slot + front LED channel.
- Glass slot: opens on inner face, 6mm glass + 1.0mm total clearance
  (0.5/side), 15mm groove depth, front wall 4mm. Slot floor + both walls
  lined with 3mm closed-cell neoprene foam tape (compresses to ~2mm).
  NO hot glue in channel. Optional: neutral-cure silicone dabs.
- LED channel: front face, 11mm wide × 8mm deep interior. Strip (10mm
  FCOB addressable WS2811/WS2814) mounts FLAT on channel floor, LEDs
  firing forward into diffuser. Corners: BTF L-shaped FCOB 3PIN 10mm
  solderless connectors (kit must state FCOB + WS2811/WS2814 - SMD-only
  kits incompatible) in enlarged corner pockets; light path turns square
  inside the rounded exterior. Expect ~2-3cm dimmer zones at corners,
  bridged by corner diffusers. Press copper clips fully home (flicker/
  glitched pixels downstream = bad clip). Diffuser clip lips 1.5mm.
- Outer corners: 60mm radius. Glass corners remain square inside —
  corner pieces gain solid material in the web between square pocket
  and round exterior (natural reinforcement).
- Internal fillets 2.5mm on EVERY inside corner (CF filament rule).
- Optional finish: fuzzy skin 0.1mm/0.25mm on visible faces ONLY —
  excluded from all mating surfaces. Decide via twin coupon test.

## 2. Piece plan (X2D, 250mm usable)

- 4 × corner pieces: one-piece Ls containing the full 60mm arc plus
  ~60mm of straight each side. Highest-stress parts. Never seam a corner.
- Vertical rails (730mm minus corner extents ≈ 490mm each): 2 pieces
  per side ≈ 245mm → 4 pieces.
- Horizontal rails (505mm minus corner extents ≈ 265mm each): 2 pieces
  per rail (~132mm) OR 1 piece if ≤250mm after corner-arm extension →
  plan 2 per rail = 4 pieces (seam offset from centre on bottom rail to
  avoid the button).
- Total: ~12 frame pieces. Finger joints (12mm fingers, 0.25mm/side
  clearance), epoxied (slow-cure structural) after fit confirmed.
  Optional interior friction-weld bead as second bond.
- Bond 3 sides + corners permanently into a U. TOP RAIL BOLTED,
  REMOVABLE (M4 + captured hex nuts): glass slides in from top forever.

## 3. Top rail / hanging

- Hangman Z-12 (12", 30.5cm) aluminium Z-bar — fits the ~38cm flat span
  between 60mm corner arcs. Bar bridges the top-rail seam(s).
- Cleat spine: continuous 10mm-thick 100% infill rail (slicer modifier)
  along top rail rear face, spanning all top pieces. M4 through-bolts
  with washers + captured hex-nut pockets on inside. NO screws into
  bare plastic threads.
- Hanging load ≈ 12–13kg total (glass 5.5kg) vs 45kg bracket rating.

## 4. Vents (required — monitor near full brightness behind 75/20 glass)

- Top rail rear lip: row of slots ~40 × 4mm, every ~60mm (hot air out).
- Bottom rail rear lip: matching row (cool air in). Convection loop.
- If monitor PSU bulge runs hot: louvre section in blackout panel above
  it (offset overlapping slats — light-tight, air-open).

## 5. LED system

- BTF FCOB WS2814 RGBW 3000K DC24V 784LED/m 10mm IP30, 5m reel
  (amazon.co.uk B0CFXMMPSL). Pixel = 71.42mm segment, 14/m.
  One continuous ~2.45m loop, all four corners in ribbon-direction bend
  (60mm radius >> minimum). Cut on marked cut lines only; ends meet at
  bottom-centre or tucked at bottom-left corner; addressable segments
  can feather the join gap.
- Data direction: strip DI end starts at the cable passage. Check arrows.
- Cable passage: 10 × 6mm angled (≈45°) slot, teardrop ceiling, SPLIT
  ACROSS the bottom-left corner-to-rail seam (half-channel each piece;
  wires laid in before epoxy closes that seam). 3-pin JST on cavity side
  = disconnect point. Matte-black printed grommet + black hot glue plug
  (light leak + strain relief). Hot glue is for cables ONLY.
- Diffusers: ALL PRINTED, milky/opal translucent PETG (not clear).
  Straight snap-leg strips (coupon-validated profile) sized to the
  stepped channel's 11mm opening + 4 CURVED CORNER CAPS: quarter-arc
  visible face following the 60mm radius, clip feet engaging the
  straight channel ends. Strip path stays SQUARE underneath
  (connectors unchanged) - the caps round the visible glow line.
  Corners glow dimmer than straights: mitigate in WLED by boosting the
  1-2 addressable segments adjacent to each corner. Print: 2 walls, 0%
  infill, 3-4 top layers; straights on their side (legs flex along
  layers), caps flat.
Channel is STEPPED and DEEP (14mm): 13mm floor
  tier 7mm tall - connector/bracket bodies sit FULLY below the upper
  tier, invisible - narrowing 1mm/side above to retain the strip,
  leaving ~9-10mm LED-to-diffuser air gap (hotspot-free diffusion;
  gap > emitter pitch rule). Corner product: verify electrical
  (3-pin 10mm FCOB, cut strip) vs mechanical fold-bracket (uncut
  strip - electrically preferable) before ordering; pocket dims from
  the real part either way.
- PSU: BTF 24V 5A 120W SEALED BRICK adapter (ETL/UKCA Class 2 - the
  laptop-style one, NOT their metal-case unit of the same rating).
  Lies in bottom margin in a printed cradle/velcro - no mounting, no
  mains wiring. Barrel plug -> included female barrel-to-screw-terminal
  adapter -> strip V+/GND. Barrel = service disconnect. Load ~51W max
  (RGBW 21W/m x 2.45m); set WLED current limit anyway.
- ESP32: bottom margin CLOSE to strip DI (data run <30cm). Runs WLED.
  74AHCT125 level shifter = £2 insurance if flicker. Snap-clip mount.
  PROVEN WLED settings for this strip (from field report): length =
  number of WS2814 ICs not LEDs (~34 for 2.45m loop), Color Order BRG,
  Swap W & G enabled. (Alt: BTF SP803E is a prebuilt ESP32 WLED box.)

## 6. Sensors

- LD2410/B/C radar: inside BOTTOM RAIL cavity, below glass edge —
  beam exits through 4mm printed front wall ONLY (never the coated
  glass, never shadowed by monitor metal). Board vertical, antenna
  patches face room, 3–5mm standoff from inner wall face (U-channel
  edge-grip clip; parameterise to measured board). Keep clear of LED
  PSU wiring. Wire: 5V/GND/OUT (+TX/RX later) → Pi GPIO. Tune range
  gates via Bluetooth app to room depth.
- Pi Camera: top-centre, LENS RESTING against glass back — sprung pod:
  sliding carriage, 2–3mm float, 10mm foam pad behind, felt/foam washer
  ring at contact + 5mm matte-black light-shield collar (blocks LED
  edge-piped light). Ribbon (300–500mm, Pi-5 22-pin type) runs down
  panel rear face across tile-seam channels to Pi. Pod bulges rearward
  from its blackout tile; keep ≥20mm from monitor cutout.

## 7. Button (IN-CHANNEL, bottom-centre of the LED line)

- 22mm momentary metal button, 3-8V white ring, mounted IN the LED
  channel at bottom-centre: 26mm recess in locally-widened channel,
  head ~flush with diffuser line, barrel through the 4mm channel floor,
  nut in a 46mm service pocket open to the rear (continuous flat
  nut seat >=34mm dia around the hole; finger room to thread the nut). Diffuser strips end in
  concave semicircular tips hugging the barrel from each side.
- Geometry enablers: frameWidth 48mm + ledSlotWall 9mm keep the recess
  1.5mm clear of the glass slot band and 5.5mm off the outer face.
- Twin wire slots (cablePassW x cablePassH) enter the pocket ceiling
  at btnNutClear (17mm) from centre - outside the nut's corner radius: the strip's two ends feed the same pocket as the
  button terminals - ONE service opening for the whole bottom-centre.
- Switch: C/NO -> GPIO + GND (internal pull-up). Ring: GPIO 3.3V or 5V.
  Crimp spades. Hand-tight + 1/4 turn.

## 8. Blackout panel (light-seal sheet + monitor collar)

- SHAPE: thin sheet (2-3mm matte black PLA) sitting ~2mm BEHIND the
  glass, spanning the ENTIRE opening - the light seal for everything.
  Monitor-shaped opening with a rearward COLLAR skirt hugging the
  monitor's edges back to its rear plane; the monitor's own metal back
  seals the middle. Foam strip at collar-to-chassis junction
  (light-tight, zero stress). Whole feature within ~1cm envelope.
  NON-STRUCTURAL - nothing may rest on or show through the glass
  except this panel.
- ~6 tiles, dovetail/puzzle joins, SEPARABLE (no adhesive). Light-duty
  clips to frame inner walls (no load carried).
- Provisions: camera aperture barrel-snug at top-centre; cable
  pass-through notches at tile seams with SLACK space and soft edges
  (camera ribbon, radar lead, OSD ribbon) - slotted notches, never
  tight holes; sheet stops ~2cm short of the bottom edge so the radar
  clip slides into the bottom rail unobstructed (radar sits below the
  glass line - no aperture needed). Radar SLIDE-IN POCKET is modelled
  in the bottom rail at x=+80mm: open to the rear, floor leaves the
  4mm front wall, sized radarBoardL x (standoff+board).
- Tile seams double as cable channels closed by the neighbouring tile.

## 9. Monitor mount (DEBEZELED Dell S2721HN - bare panel + metal shield)

- Panel is stripped to metal chassis; factory internal metal shield
  retained over PSU/driver boards (primary mains barrier - keep it).
- GROUNDING CHECK before first powered use in build: mains plug earth
  pin <-> bare chassis continuity ~0 ohms; refit any ground straps/screws
  disturbed during disassembly. Non-deferrable.
- Mounting: printed brackets SCREWED into the chassis's existing casing
  holes (measure thread, typ. M3), bolted back to frame/blackout panel.
  BEAM PROFILE (final): L-STEP, not a groove - shelf under the
  monitor's bottom edge + rear wall behind it. NO plastic on the glass
  side: monitor face presses flat against the glass, nothing between.
  Rear wall face at (glass back) - (monEdgeT) - ~1mm, with a thin foam
  strip on the wall face taking up tolerance (gentle sprung press).
  Shelf stops ~1mm short of the glass. Top strap: same rear-side-only
  principle.
  REMOVABILITY RULE: no adhesive anywhere in monitor mounting - every
  bracket/cross-rod removes with a screwdriver only.
  Glass contact via thin foam strips at panel face edges - gentle
  preload only; brackets set position, not pressure. Support >=3 edges;
  never span load across the bare panel middle.
- MOUNTS IN PORTRAIT: mirror is portrait (730x505) and a 27" panel
  landscape (~610mm) is wider than the mirror - chassis long side runs
  VERTICAL. Rotate display 90 deg in software (MagicMirror2 is
  portrait-native; on Pi 5 set display rotation in screen config).
  Brackets/cutout dims below are pre-rotation panel dims - swap W/H
  when placing.
- Active area (fixed, 27" 16:9): 597.9 x 336.3 mm = blackout cutout
  (336.3 wide x 597.9 tall once mounted portrait).
  Chassis dims = active + measured border offsets per edge.
- Sheet-metal edges: deburr/tape before handling. LVDS ribbon: strain-
  relieve, route nothing across it. OSD button board: printed clip,
  reachable behind blackout panel (set brightness max / sleep off once).
- PSU insulating skirt: DEFERRED by design - clip-on box slightly larger
  than shield, fitted from open rear later. Rules when built: 10mm air
  standoff above metal, louvred top, removable fit, PETG near PSU.
  Bank shield footprint/height/screw positions during measuring session.
- Depth: stripped stack likely 25-40mm -> frameDepth may tighten to
  65-70mm. Set from measurement.

## 10. Electronics bay + power

- REAR PANEL: frame's rear inner edge carries a 3mm-deep x 10mm-wide
  REBATE around the whole opening - flat rear tiles drop in and sit
  FLUSH with the frame back, screwed to bosses (M3). Removable always.
- Tiling: Pi 5 side margin (not below monitor — heat), ESP32 + LED PSU
  bottom margin, monitor brick (if Pattern A/C) cradled bottom margin.
- Mains exit: cable-sized hole SPLIT ACROSS a bottom-rail seam
  (semicircle each piece) + printed strain-relief clip. Consider flat
  3-way block instead of full power strip (3 sockets suffice: monitor,
  Pi USB-C, 24V PSU). MEASURE with plugs inserted.
- HDMI: right-angle adapters ×2 (£4 each) to keep depth at 80mm.

## 11. Assembly order (glass safety)

1. Print + fit-test coupons (glass slot, finger joint, diffuser clip,
   22.3mm button hole) in cheap PETG. Iterate clearances.
2. Print frame pieces (final CF). Epoxy into U (sides + bottom + corners),
   laying LED wires into the split passage before closing its seam.
3. Foam-line slot. Button, radar clip, ESP32, PSU into bottom rail.
4. Strip into channel (edge-mount, DI at passage), diffusers on. Test.
5. Slide glass in from top (coated side OUT — gap-test + label first).
   Bolt top rail on. Z-bar to spine.
6. Grounding check on monitor chassis. Blackout tiles + camera pod +
   chassis brackets + monitor. Wire everything.
7. Hang. Configure radar gates. WLED presets. MagicMirror² software.

## Open parameters (blocking final dimensions only)

monitor border offsets (4 edges) / monD at tallest component /
chassis hole map + thread / shield footprint+screws /
power-strip-or-block envelope with plugs / LD2410 exact board variant mm /
Pi Camera version (v2/v3/HQ → lens barrel dia + ribbon type)
