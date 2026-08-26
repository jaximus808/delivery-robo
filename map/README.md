# WashU Danforth Campus — Nav2 Map Package

Source imagery: USDA/USGS NAIP (public domain), exported 2026-08-12 from
`imagery.nationalmap.gov` (USGSNAIPPlus ImageServer), WGS84.

## Files

- `washu_aerial.png` — 2720x1860 RGB aerial, cropped to campus. Reference for
  tracing; not loaded by Nav2.
- `base_map.pgm` + `base_map.yaml` — all-free static map (localization is RTK, not map matching).
- `keepout_draft.pgm` + `keepout_draft.yaml` — keepout mask: black (0) =
  keepout, white (254) = free. Drafted as "everything keepout except the
  paved walkway network" (`tools/auto_draft.py` + traced vector edits).
  **Review before trusting** — see below.
- `keepout_overlay_preview.png` — draft mask shown red over the aerial.
- `georef.yaml` — **single source of truth** for datum lat/lon, resolution,
  and calibration offset. Edit it, then run `python3 map/tools/update_georef.py`
  to regenerate the map yamls and the GPS datum config.
- `tools/` — crop/auto-draft/edit/render scripts (each has a usage header).

## Georeferencing

- Bounding box (WGS84): lon `-90.3161244 … -90.3005`, lat `38.6435 … 38.6518784`
- Resolution: **0.5 m/pixel** (ground extent 1360 m x 930 m)
- Map frame origin (0,0) = **southwest corner** = lat `38.6435`, lon `-90.3161244`
- X = east, Y = north (standard ROS ENU)
- Cropped from the original 4004x2664 NAIP export with
  `tools/crop_to_campus.py` (window x 1284..4004, y 804..2664); the south
  edge is unchanged, so only the west/north edges moved.

**To update the datum lat/lon: edit `georef.yaml` and run
`python3 map/tools/update_georef.py`.** That rewrites `base_map.yaml`,
`keepout_draft.yaml`, and `ros2_ws/src/my_bringup/config/gps_datum.yaml`
so everything stays in sync. If you later add robot_localization, its
`navsat_transform` datum is the same `[lat, lon, 0.0]` (the script prints it).

## IMPORTANT: calibrate before trusting

NAIP is orthorectified but can still be offset ~1–2 m locally. Before relying
on the keepout mask: log RTK fixes at 4–8 identifiable features (sidewalk
corners, manholes) spread across campus, convert to map frame (meters E/N of
the SW-corner datum), and compare with pixel positions
(`px_x = east_m / 0.5`, `px_y = 1860 - north_m / 0.5`). If there is a
consistent shift, put it in `origin_offset_m` in `georef.yaml` and re-run
`tools/update_georef.py` (or re-warp in QGIS with those points as ground
control). `map/tools/rtk_calibrate.py` automates the math: feed it a CSV of
`lat,lon,px_x,px_y` reference points and it prints the offset to paste into
`georef.yaml`.

While driving, the `gps_to_map` node (in `my_bringup`) converts live RTK
fixes to map-frame coordinates — echo `/gps/map_pose` to read the robot's
position in meters E/N of the datum (and `/gps/map_pixel` for the pixel it
is on in this imagery).

## Editing the draft mask

The mask defaults to keepout everywhere and frees only the traced walkway
network (safe direction: a missed path is blocked, not a hazard). Two ways
to edit:

- **Vector edits (preferred, reproducible):** add polygons/strokes to a JSON
  file and run `python3 map/tools/apply_edits.py my_edits.json`; check the
  result with `python3 map/tools/render_overlay.py out.png --scale 0.5`
  (`--tile X0 Y0 X1 Y1 --grid 50` to zoom). Format is documented in the
  script header. White strokes are applied after black fills, so corridors
  punch through.
- **GIMP (freehand):** full step-by-step workflow (layer setup, editing
  passes, export, RViz verification): see [`GIMP_WORKFLOW.md`](GIMP_WORKFLOW.md).
  Pencil tool only, pure black/white, export must stay **2720x1860**.

Things the aerial can't show and still need local knowledge: outdoor
**staircases** on walkways (paint black — they read as sidewalk from above),
construction fencing, and which street crossings are actually allowed.

## Nav2 wiring (both global AND local costmaps)

```yaml
costmap_filters:
  filters: ["keepout_filter"]
  keepout_filter:
    plugin: "nav2_costmap_2d::KeepoutFilter"
    filter_info_topic: "/costmap_filter_info"
```

Run `nav2_map_server::CostmapFilterInfoServer` with `type: 0` (keepout),
`mask_topic: /keepout_filter_mask`, and a second `map_server` instance
serving `keepout_draft.yaml` on that topic.
