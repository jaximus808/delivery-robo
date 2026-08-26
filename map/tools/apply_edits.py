#!/usr/bin/env python3
"""Apply JSON vector edits to the keepout mask.

Usage (from repo root):
  python3 map/tools/apply_edits.py EDITS.json [EDITS2.json ...] [--mask PATH]

Edit file format — coordinates are FULL-RES map pixel coords (x right, y down):
{
  "edits": [
    {"type": "poly",   "color": "black", "points": [[x,y], ...]},
    {"type": "rect",   "color": "black", "xyxy": [x0, y0, x1, y1]},
    {"type": "stroke", "color": "white", "width_px": 6, "points": [[x,y], ...]}
  ]
}

All BLACK edits (from every file) are applied first, then all WHITE edits, so
white sidewalk corridors always punch through black fills regardless of file
order. An edit may override this with an explicit "order" (black defaults to
0, white to 1; e.g. "order": 2 on a black edit re-blacks on top of white —
used for water features inside plazas). Values are pure 0 / 254 — no
anti-aliasing, trinary-safe.
"""
import argparse
import json
from PIL import Image, ImageDraw

FREE, KEEPOUT = 254, 0

def draw(d, e, val):
    t = e['type']
    if t == 'poly':
        d.polygon([tuple(p) for p in e['points']], fill=val, outline=val)
    elif t == 'rect':
        x0, y0, x1, y1 = e['xyxy']
        d.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=val)
    elif t == 'stroke':
        w = int(e.get('width_px', 6))
        pts = [tuple(p) for p in e['points']]
        d.line(pts, fill=val, width=w, joint='curve')
        r = w // 2
        for x, y in (pts[0], pts[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=val)
    else:
        raise ValueError(f"unknown edit type {t!r}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--mask', default='map/keepout_draft.pgm')
    a = ap.parse_args()

    im = Image.open(a.mask).convert('L')
    d = ImageDraw.Draw(im)
    edits = []
    for path in a.files:
        with open(path) as f:
            edits += json.load(f)['edits']

    default_order = {'black': 0, 'white': 1}
    counts = {'black': 0, 'white': 0}
    for e in sorted(edits, key=lambda e: e.get('order', default_order[e['color']])):
        draw(d, e, KEEPOUT if e['color'] == 'black' else FREE)
        counts[e['color']] += 1

    with open(a.mask, 'wb') as f:
        f.write(f"P5\n{im.width} {im.height}\n255\n".encode())
        f.write(im.tobytes())
    print(f"applied {counts['black']} black + {counts['white']} white edits -> {a.mask}")

if __name__ == '__main__':
    main()
