#!/usr/bin/env python3
"""Compute the aerial-vs-RTK offset from surveyed reference points.

Stand the RTK receiver on 4-8 identifiable features (sidewalk corners,
manholes), note the fixed lat/lon of each, and find the same feature's pixel
in map/washu_aerial.png (e.g. with GIMP's pointer readout, or
render_overlay.py --grid). Put them in a CSV with header:

    lat,lon,px_x,px_y
    38.648712,-90.311302,1042,613
    ...

Then run (from repo root):  python3 map/tools/rtk_calibrate.py points.csv

Prints the mean offset and the origin_offset_m to paste into map/georef.yaml
(then run update_georef.py). Offsets > ~3 m or wildly inconsistent residuals
mean something else is wrong (bad datum, wrong pixel, float-only fix).
"""
import csv
import math
import sys

import yaml

WGS84_A = 6378137.0
WGS84_E2 = 0.00669437999014


def local_radii(lat_rad):
    """WGS84 meridional (north) and prime-vertical (east) radii at lat."""
    s2 = math.sin(lat_rad) ** 2
    w = math.sqrt(1.0 - WGS84_E2 * s2)
    return WGS84_A * (1.0 - WGS84_E2) / w ** 3, WGS84_A / w


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    with open('map/georef.yaml') as f:
        g = yaml.safe_load(f)
    lat0 = math.radians(g['datum']['lat'])
    lon0 = math.radians(g['datum']['lon'])
    res = g['resolution']
    h = g['height_px']

    rows = list(csv.DictReader(open(sys.argv[1])))
    if len(rows) < 2:
        raise SystemExit("need at least 2 reference points (4-8 recommended)")

    r_north, r_prime = local_radii(lat0)
    r_east = r_prime * math.cos(lat0)

    dxs, dys = [], []
    print(f"{'point':>5} {'d_east(m)':>10} {'d_north(m)':>10}")
    for i, r in enumerate(rows):
        east = (math.radians(float(r['lon'])) - lon0) * r_east
        north = (math.radians(float(r['lat'])) - lat0) * r_north
        # where the image says that feature is, in map meters
        img_east = float(r['px_x']) * res
        img_north = (h - float(r['px_y'])) * res
        # offset to ADD to image coords so they match RTK reality
        dx, dy = east - img_east, north - img_north
        dxs.append(dx)
        dys.append(dy)
        print(f"{i:>5} {dx:>10.2f} {dy:>10.2f}")

    mx = sum(dxs) / len(dxs)
    my = sum(dys) / len(dys)
    sx = max(abs(d - mx) for d in dxs)
    sy = max(abs(d - my) for d in dys)
    print(f"\nmean offset: east {mx:+.2f} m, north {my:+.2f} m "
          f"(worst residual {max(sx, sy):.2f} m)")
    if max(sx, sy) > 1.5:
        print("WARNING: residuals are inconsistent — re-check the outlier "
              "points before applying this.")
    print(f"\npaste into map/georef.yaml:\n"
          f"    origin_offset_m: [{mx:.2f}, {my:.2f}]\n"
          f"then run: python3 map/tools/update_georef.py")


if __name__ == '__main__':
    main()
