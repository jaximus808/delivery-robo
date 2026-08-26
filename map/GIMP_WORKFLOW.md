# Keepout Mask Editing Workflow (GIMP)

Step-by-step instructions for hand-editing `keepout_draft.pgm` against the
aerial imagery. See `README.md` for georeferencing details and the Nav2
wiring the finished mask plugs into.

## How the mask works (read once)

- **1 pixel = 1 occupancy cell = 0.5 m × 0.5 m of real ground.** Both
  `washu_aerial.png` and `keepout_draft.pgm` are 2720×1860, pixel-aligned
  1:1 — no registration needed, just layer them.
- Pixel value → cell state (per `keepout_draft.yaml`, `negate: 0`):

  | You paint | Cell becomes | Meaning |
  |---|---|---|
  | Pure black (0,0,0) | occupied (100) | keepout — robot may not enter |
  | Pure white (255,255,255) | free (0) | traversable |
  | Any mid-gray | unknown (-1) | ambiguous — never create these |

- Mid-grays come from anti-aliasing / soft brushes. **Pencil tool only,
  100% hardness.**
- GIMP pixel (0,0) is the **top-left**; the map origin is the **southwest
  corner** (bottom-left pixel). The image displays north-up, so editing
  feels natural, but converting RTK coords to pixels flips y:
  `px_x = east_m / 0.5`, `px_y = 1860 − north_m / 0.5`.
- Keepout is permanent from the robot's perspective — it is never
  re-observed or corrected at runtime like lidar obstacles. A wrongly
  blocked sidewalk stays blocked forever; a wrongly free staircase stays
  "driveable" forever. Err toward *safety* on hazards and *accuracy* on
  corridors.

## 1. Layer setup

1. **File → Open** → `map/washu_aerial.png` (base layer, in color).
2. **File → Open as Layers** (Ctrl+Alt+O) → `map/keepout_draft.pgm`.
   It lands exactly on top — same dimensions, auto-aligned.
3. In the Layers panel, set the mask layer **opacity to ~40–50%** so the
   aerial shows through (white haze = free, black = keepout). Layer
   opacity is display-only; painted pixels stay pure black/white.
4. Optional: **View → Show Grid**, then **Image → Configure Grid** →
   spacing **1×1 px**. Zoomed past ~800%, each grid square is one 0.5 m
   occupancy cell.
5. Select the **Pencil (N)**, 100% hardness. Foreground pure black,
   background pure white — press **X** to swap. Always confirm the
   **mask layer** is the active layer before painting.
6. Save a working file as `keepout_edit.xcf` (**File → Save As**) so the
   layer setup survives between sessions.

## 2. Editing passes (coarse → fine)

The draft starts **black everywhere except the traced walkway network**, so
off-campus/roads/grass are already keepout. Editing is mostly verifying and
refining the white network.

### Pass 1 — walk the sidewalks (critical pass)
Zoom to 400–800% and follow every sidewalk route the robot will use, end
to end, like you're driving it. Each corridor must be a **continuous white
strip ≥ 4–6 px wide** (= 2–3 m) that stays on pavement. Fix gaps (canopy
shadow breaks) by painting **white**; fix strips that wander onto grass by
painting the stray part **black**.

### Pass 2 — hazards the aerial can't show (local knowledge)
- **Stairs** — look identical to sidewalk from above. Paint every
  staircase **black**. These are the most dangerous false-free cells on
  the map.
- Steep ramps to avoid, fountains/water, amphitheater seating,
  construction fencing: **black**.

### Pass 3 — crossings policy
White ribbons across roads exist only at designated crossings. Remove any
you don't want the robot to use (paint **black**); add missing ones the
robot genuinely needs (white, ~5 px wide, straight across at the
crosswalk).

### Pass 4 — stray white
Scan for leftover white on rooftops, parking lots, driveways, or anything
off-campus: **black**.

## 3. Export (order matters)

1. Set the mask layer back to **100% opacity**.
2. **Delete the aerial layer** (otherwise the photo gets baked into the
   mask).
3. **Image → Flatten Image**, then **Image → Mode → Grayscale**.
4. **File → Export As** → `map/keepout_draft.pgm`, pick **Raw** in the
   PGM dialog.
5. Confirm the export is still **2720×1860** — any other size means
   something got cropped and the georeferencing is broken.

## 4. Verify in RViz

```bash
cd sim && source install/setup.bash
ros2 launch robo_courier map_server.launch.py
```

The map server re-reads the file every launch. Check:

- [ ] Sidewalk corridors are continuous white end-to-end (no pinch points
      narrower than ~4 px).
- [ ] Everything off-campus is black.
- [ ] All roads black (except intended crossings), all stairs black.
- [ ] No gray speckle along stroke edges (gray = anti-aliasing snuck in —
      it renders as "unknown" cells in RViz).

Repeat edit → export → RViz until clean. Before trusting the mask on the
robot, do the RTK calibration check described in `README.md`.
