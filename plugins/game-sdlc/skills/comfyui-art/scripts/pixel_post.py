#!/usr/bin/env python3
"""Post-processing for palette-locked pixel art (needs Pillow).

The steps between "the model made an image" and "the palette tool is happy",
plus the review sheets a human or a critic judges from.

    key      SRC DST            flood-fill the background away from the border
    report   IMG --palette GPL  colours used, by palette name (--grid prints a letter map)
    remap    IMG OUT --palette GPL --map "Sea Foam=Ink Pale" --map "Skin Deep=Madder@rows:39-"
    holes    IMG OUT [--palette GPL --color "Ink Deep"]   fill transparent pixels enclosed by the figure
    sheet    OUT IMG [IMG ...] [--scale 6 --labels a b --bg #2d5566 --actual]
    frames   OUT CELL [CELL ...] [--shift 0 1 0 1]        assemble a horizontal sprite sheet
    anim     OUT.gif SHEET --cell 32 32 --order 0 1 0 1 2 3 [--scale 6 --ms 400]
"""
import argparse
import math
import sys

from PIL import Image, ImageDraw


def load_palette(path):
    """GIMP .gpl -> {name: (r, g, b)} in file order."""
    pal = {}
    for line in open(path, encoding="utf-8"):
        parts = line.split()
        if len(parts) >= 4 and all(p.isdigit() for p in parts[:3]):
            pal[" ".join(parts[3:])] = tuple(int(p) for p in parts[:3])
    return pal


def rgba(img_path):
    return Image.open(img_path).convert("RGBA")


def pixels(im):
    # getdata() is deprecated from Pillow 12; its replacement does not exist before it
    return im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()


def cmd_key(a):
    """Remove the background by flooding from the border over pixels whose
    chromaticity matches the border's median colour. A darker ground shadow of the
    same hue goes with it; the figure's outline stops the flood. Unlike a global
    colour key this cannot eat skin or a coat that merely resembles the backdrop,
    unless they touch the border with no outline in between."""
    im = rgba(a.src)
    px = im.load()
    w, h = im.size
    border = [px[x, y][:3] for x in range(0, w, 4) for y in (0, h - 1)] + \
             [px[x, y][:3] for y in range(0, h, 4) for x in (0, w - 1)]
    bg = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))
    nb = math.sqrt(sum(v * v for v in bg)) or 1
    bgn = [v / nb for v in bg]
    bgl = sum(bg) / 3

    def is_bg(c):
        n = math.sqrt(sum(v * v for v in c)) or 1
        d = math.sqrt(sum((c[i] / n - bgn[i]) ** 2 for i in range(3)))
        return d < a.hue_tol and a.min_light * bgl < sum(c) / 3 < a.max_light * bgl

    seen = bytearray(w * h)
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    n = 0
    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h) or seen[y * w + x]:
            continue
        seen[y * w + x] = 1
        if not is_bg(px[x, y][:3]):
            continue
        px[x, y] = (0, 0, 0, 0)
        n += 1
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    im.save(a.dst)
    # The share removed cannot tell "background" from "background plus a grey cap": a subject
    # colour close in hue to the backdrop goes with it. Always look at this check image.
    check = Image.new("RGBA", im.size, (0, 255, 64, 255))
    check.alpha_composite(im)
    check_path = a.dst.rsplit(".", 1)[0] + "_check.png"
    check.convert("RGB").resize((max(1, w // 4), max(1, h // 4)), Image.NEAREST).save(check_path)
    print(f"background {bg} removed: {n} px ({100 * n / (w * h):.0f}%), figure bbox {im.getbbox()}")
    print(f"LOOK at {check_path}: the subject on bright green - any missing part of it was keyed away")
    if n / (w * h) < 0.2:
        print("WARNING: little was removed - the background may not be flat or may touch the figure")
    return 0


def cmd_report(a):
    pal = load_palette(a.palette)
    by_rgb = {v: k for k, v in pal.items()}
    im = rgba(a.img)
    counts = {}
    for p in pixels(im):
        if p[3] == 255:
            counts[p[:3]] = counts.get(p[:3], 0) + 1
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    key = {}
    print(f"{a.img}: {im.size[0]}x{im.size[1]}, {len(counts)} colours, "
          f"alpha values {sorted(set(p[3] for p in pixels(im)))}")
    for i, (c, n) in enumerate(sorted(counts.items(), key=lambda kv: -kv[1])):
        key[c] = letters[i % len(letters)]
        name = by_rgb.get(c, "** NOT IN PALETTE **")
        print(f"  {key[c]}  #{c[0]:02x}{c[1]:02x}{c[2]:02x} {n:5d}  {name}")
    if a.grid:
        w, h = im.size
        print("    " + "".join(str(x // 10) if x % 10 == 0 else " " for x in range(w)))  # tens
        print("    " + "".join(str(x % 10) for x in range(w)))
        for y in range(h):
            print(f"{y:3d} " + "".join(key[im.getpixel((x, y))[:3]] if im.getpixel((x, y))[3] == 255 else "."
                                       for x in range(w)))
    return 0


def _span(spec, size):
    lo, _, hi = spec.partition("-")
    return range(int(lo) if lo else 0, (int(hi) + 1) if hi else size)


def cmd_remap(a):
    """Swap palette entries by meaning, optionally inside a row/column band:
    "Skin Deep=Madder@rows:39-" changes only rows 39 and below."""
    pal = load_palette(a.palette)
    im = rgba(a.img)
    px = im.load()
    w, h = im.size
    for rule in a.map:
        swap, _, where = rule.partition("@")
        src, _, dst = (s.strip() for s in swap.partition("="))
        if src not in pal or dst not in pal:
            print(f"unknown palette name in '{rule}'")
            return 2
        rows, cols = range(h), range(w)
        for part in filter(None, where.split(",")):
            axis, _, spec = part.partition(":")
            if axis.strip() == "rows":
                rows = _span(spec, h)
            elif axis.strip() == "cols":
                cols = _span(spec, w)
        n = 0
        for y in rows:
            for x in cols:
                p = px[x, y]
                if p[3] == 255 and p[:3] == pal[src]:
                    px[x, y] = pal[dst] + (255,)
                    n += 1
        print(f"{src} -> {dst} {where or 'everywhere'}: {n} px")
    im.save(a.out)
    return 0


def cmd_holes(a):
    im = rgba(a.img)
    px = im.load()
    w, h = im.size
    color = load_palette(a.palette)[a.color] if a.palette else (0x1A, 0x14, 0x20)
    seen = set()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h) or px[x, y][3] != 0:
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    holes = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] == 0 and (x, y) not in seen]
    for x, y in holes:
        px[x, y] = color + (255,)
    im.save(a.out)
    print(f"filled {len(holes)} enclosed hole(s): {holes[:20]}")
    return 0


def _hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def cmd_sheet(a):
    """Side-by-side review: each image at --scale on a flat backdrop, with an optional
    true-size copy under it (--actual), because pixel art must be judged at 1:1 too."""
    ims = [rgba(p) for p in a.imgs]
    s = a.scale
    cw = max(i.width for i in ims) * s
    ch = max(i.height for i in ims) * s
    extra = (max(i.height for i in ims) + 8) if a.actual else 0
    label_h = 16 if a.labels else 0
    sheet = Image.new("RGBA", (len(ims) * (cw + 12) + 12, ch + extra + label_h + 12), _hex(a.bg))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x0 = 12 + i * (cw + 12)
        big = im.resize((im.width * s, im.height * s), Image.NEAREST)
        sheet.alpha_composite(big, (x0 + (cw - big.width) // 2, 6 + ch - big.height))
        if a.actual:
            sheet.alpha_composite(im, (x0, 6 + ch + 6))
        if a.labels and i < len(a.labels):
            d.text((x0, 6 + ch + extra + 2), a.labels[i], fill=(235, 235, 235, 255))
    sheet.save(a.out)
    print(f"wrote {a.out} {sheet.size}")
    return 0


def cmd_frames(a):
    cells = [rgba(p) for p in a.cells]
    cw, ch = cells[0].size
    shifts = a.shift or [0] * len(cells)
    out = Image.new("RGBA", (cw * len(cells), ch), (0, 0, 0, 0))
    for i, (c, dy) in enumerate(zip(cells, shifts)):
        out.alpha_composite(c, (i * cw, -dy))  # positive shift lifts the figure (idle bob)
    out.save(a.out)
    print(f"wrote {a.out} {out.size}")
    return 0


def cmd_anim(a):
    sheet = rgba(a.sheet)
    cw, ch = a.cell
    frames = []
    for i in a.order:
        cell = sheet.crop((i * cw, 0, i * cw + cw, ch)).resize((cw * a.scale, ch * a.scale), Image.NEAREST)
        f = Image.new("RGBA", cell.size, _hex(a.bg))
        f.alpha_composite(cell)
        frames.append(f.convert("RGB"))
    frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=a.ms, loop=0)
    print(f"wrote {a.out}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("key"); k.add_argument("src"); k.add_argument("dst")
    k.add_argument("--hue-tol", type=float, default=0.09)
    k.add_argument("--min-light", type=float, default=0.35); k.add_argument("--max-light", type=float, default=1.35)
    r = sub.add_parser("report"); r.add_argument("img"); r.add_argument("--palette", required=True)
    r.add_argument("--grid", action="store_true")
    m = sub.add_parser("remap"); m.add_argument("img"); m.add_argument("out")
    m.add_argument("--palette", required=True); m.add_argument("--map", action="append", required=True)
    hh = sub.add_parser("holes"); hh.add_argument("img"); hh.add_argument("out")
    hh.add_argument("--palette"); hh.add_argument("--color", default="Ink Deep")
    s = sub.add_parser("sheet"); s.add_argument("out"); s.add_argument("imgs", nargs="+")
    s.add_argument("--scale", type=int, default=6); s.add_argument("--labels", nargs="*")
    s.add_argument("--bg", default="#2d5566"); s.add_argument("--actual", action="store_true")
    f = sub.add_parser("frames"); f.add_argument("out"); f.add_argument("cells", nargs="+")
    f.add_argument("--shift", type=int, nargs="*")
    an = sub.add_parser("anim"); an.add_argument("out"); an.add_argument("sheet")
    an.add_argument("--cell", type=int, nargs=2, required=True); an.add_argument("--order", type=int, nargs="+", required=True)
    an.add_argument("--scale", type=int, default=6); an.add_argument("--ms", type=int, default=400)
    an.add_argument("--bg", default="#2d5566")
    a = p.parse_args()
    return {"key": cmd_key, "report": cmd_report, "remap": cmd_remap, "holes": cmd_holes, "sheet": cmd_sheet,
            "frames": cmd_frames, "anim": cmd_anim}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
