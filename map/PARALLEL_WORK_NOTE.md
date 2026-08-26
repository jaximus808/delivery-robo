# ⚠️ Parallel work in flight — read before building on this

**Written 2026-08-13.** Everything on branch `feat/arerial-map` under `map/`
(campus-cropped aerial, keepout mask + tools, `georef.yaml` datum plumbing)
plus the `gps_to_map` node in `my_bringup` was produced as one approach to
campus mapping + RTK georeferencing.

**Another dev has unpushed work covering some of the same ground** (expected
to land within ~a week of the date above, so around 2026-08-20). Until that
push arrives, treat this branch's map/RTK work as *provisional* — it may be
partially superseded.

What we know about the other approach (dev's own description, 2026-08-13):
a March demo that used **OSM data** for the campus path network, computed
shortest path between two nodes, and fed that into a **hand-rolled
navigation stack** (deliberately not Nav2, which they find clunky). Only the
east end was downloaded/simulated, but they consider it "mostly complete
end-to-end navigation around campus" modulo bug fixes and tuning. Known
gaps they named: obstacle detection (planned as a lidar-integrating cost
function), then battery life and unexpected route closures.

So the two approaches differ in kind, and are likely **complementary**
rather than strictly competing:

| Concern | A (this branch) | B (dev) |
|---|---|---|
| Path knowledge | raster keepout mask traced from NAIP aerial | OSM vector path graph |
| Global planning | Nav2 on costmap + keepout filter | own shortest-path over graph nodes |
| Nav stack | Nav2 | custom |
| Georeferencing / RTK→map | georef.yaml datum + gps_to_map node | unknown — check how OSM lat/lon is grounded |
| Obstacle handling | Nav2 local costmap (lidar) — standard but unproven here | planned lidar cost function — not built |

Plausible merge shape to evaluate (not a foregone conclusion): OSM graph for
route-level planning, this branch's raster mask as the safety net / keepout
enforcement and RTK georeferencing as the shared lat/lon→map foundation —
under whichever nav stack survives review. Watch for datum mismatches: OSM
coordinates are WGS84 lat/lon like `georef.yaml`, so both can share one
datum if B's conversion is made to read it.

## When the other dev's work is pushed

Don't hand-pick a winner. Run a Claude agent review that treats the two as
independent approaches and merges the best of each:

```
claude "Two independent approaches to WashU campus mapping/RTK exist:
(A) branch feat/arerial-map (see map/PARALLEL_WORK_NOTE.md for scope), and
(B) the newly pushed branch <NAME>. Review both end-to-end and produce a
merge plan: for each concern — aerial imagery + crop, georeferencing/datum
handling, keepout mask content and editing workflow, lat/lon->map conversion,
RTK calibration, launch wiring — say which approach is stronger and why,
what to keep from each, and what conflicts. Then apply the merge on a new
branch."
```

Judging criteria to hold both against:

- **Georeferencing correctness** — is the datum defined once and propagated
  (here: `map/georef.yaml` → `map/tools/update_georef.py`), or duplicated by
  hand? Is the lat/lon→meters math ellipsoidal (see `gps_to_map.py`) or
  spherical/approximate?
- **Mask safety direction** — unknown areas should default to *keepout*
  (approach A frees only the traced walkway network; anything missed is
  blocked, not a hazard). A mask that defaults free fails dangerous.
- **Reproducibility** — can the mask/georef be regenerated from scripts and
  vector edits, or is it a one-off binary artifact?
- **Verification** — `map/tools/check_mask.py` (size, trinary purity,
  network connectivity) should pass on whatever merges.
- **RTK usability** — one-edit datum updates; live fix→map-frame topics
  (`/gps/map_pose`, `/gps/map_pixel`); calibration path
  (`map/tools/rtk_calibrate.py`).

## What this branch's approach contains (approach A inventory)

- `map/washu_aerial.png` — NAIP aerial cropped to campus (2720x1860, 0.5 m/px)
- `map/base_map.pgm/.yaml`, `map/keepout_draft.pgm/.yaml` — Nav2 maps
- `map/georef.yaml` + `map/tools/` — datum source of truth, crop/auto-draft/
  edit/render/check/calibrate scripts (each has a usage header)
- `ros2_ws/src/my_bringup/my_bringup/gps_to_map.py` + `config/gps_datum.yaml`
  (generated) — NavSatFix → map-frame node, wired into `master_launch.py`
- Mask content was traced by a two-round multi-agent pass over the aerial
  (trace + stitch/verify) and still expects human review of stairs and
  street-crossing policy (see `map/README.md`).
