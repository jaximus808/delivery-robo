# WashU Danforth Campus — Nav2 Map Package

Source imagery: USDA/USGS NAIP (public domain), exported 2026-08-12 from
`imagery.nationalmap.gov` (USGSNAIPPlus ImageServer), WGS84.

## Files

- `washu_aerial.png` — 4004x2664 RGB aerial. Reference for tracing; not loaded by Nav2.
- `base_map.pgm` + `base_map.yaml` — all-free static map (localization is RTK, not map matching).
- `keepout_draft.pgm` + `keepout_draft.yaml` — AUTO-DRAFTED keepout mask
  (green-vegetation threshold). Black (0) = keepout, white (254) = free.
  **Must be hand-edited before use** — see below.
- `keepout_overlay_preview.png` — draft mask shown red over the aerial.

## Georeferencing

- Bounding box (WGS84): lon `-90.3235 … -90.3005`, lat `38.6435 … 38.6555`
- Resolution: **0.5 m/pixel** (ground extent ≈ 2002 m x 1332 m)
- Map frame origin (0,0) = **southwest corner** = lat `38.6435`, lon `-90.3235`
- X = east, Y = north (standard ROS ENU)

Set `navsat_transform_node` datum to the SW corner so GPS and map agree:

```yaml
navsat_transform:
  ros__parameters:
    datum: [38.6435, -90.3235, 0.0]   # lat, lon, yaw
```

## IMPORTANT: calibrate before trusting

NAIP is orthorectified but can still be offset ~1–2 m locally. Before relying
on the keepout mask: log RTK fixes at 4–8 identifiable features (sidewalk
corners, manholes) spread across campus, convert to map frame (meters E/N of
the SW-corner datum), and compare with pixel positions
(`px_x = east_m / 0.5`, `px_y = image_height - north_m / 0.5`). If there is a
consistent shift, adjust `origin` in the YAMLs (or re-warp in QGIS with those
points as ground control).

## Editing the draft mask (GIMP)

The auto-draft flags all vegetation, including **tree canopy hanging over
sidewalks** (paths under trees look blocked) and misses shadowed grass. Also,
off-campus areas are not yet painted as keepout. To edit:

1. Open `keepout_draft.pgm`; load `washu_aerial.png` as a layer underneath
   (set mask layer ~50% opacity while editing).
2. Use the hard-edged Pencil tool only (no anti-aliasing — intermediate gray
   values confuse the trinary map): pure black = keepout, pure white = free.
3. Erase canopy-over-sidewalk blobs, fill shadowed grass, paint roads and all
   off-campus area black, leave a margin around keepout edges.
4. Flatten to just the mask layer and export as PGM (or PNG, grayscale).

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
