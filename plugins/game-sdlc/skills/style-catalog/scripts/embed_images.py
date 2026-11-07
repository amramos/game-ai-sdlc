"""Pack an entry's demo images into one script, or unpack them to edit.

A demo opened from file:// can't hand WebGL a texture loaded from a neighbouring file: Chrome
treats every local file as its own origin and refuses the upload, so the scene renders blank.
Images inside the page's own script are the same origin and load everywhere. So a demo keeps
its images in `assets/images.js` and loads them with `IMG('assets/<name>')`:

    <script src="assets/images.js"></script>
    texLoader.load(IMG('assets/floor.jpg'))

usage:
    python embed_images.py pack <entry>/assets [--keep]   # images (also in subfolders; not src/) → images.js,
                                                          # deleting them unless --keep;
                                                          # --only <subfolder> packs just that one
    python embed_images.py unpack <entry>/assets          # images.js → image files, to edit

Standard library only.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
HEADER = (
    "// Images for demo.html, embedded so the page works from file:// (see embed_images.py).\n"
    "// Edit them with: python embed_images.py unpack assets\n"
)
ENTRY = re.compile(r'^\s*"(assets/[^"]+)":\s*"data:[^;]+;base64,([^"]+)",?$', re.M)


def pack(assets: Path, keep: bool, only: str | None = None) -> int:
    root = assets / only if only else assets
    images = sorted(p for p in root.rglob("*") if p.suffix.lower() in TYPES and p.is_file()
                    and "src" not in p.relative_to(assets).parts[:-1])
    target = assets / "images.js"
    existing = dict(ENTRY.findall(target.read_text(encoding="utf-8"))) if target.exists() else {}
    data = {k: f"data:{TYPES[Path(k).suffix.lower()]};base64,{v}" for k, v in existing.items()}
    for image in images:
        key = "assets/" + image.relative_to(assets).as_posix()
        data[key] = f"data:{TYPES[image.suffix.lower()]};base64,{base64.b64encode(image.read_bytes()).decode()}"
    lines = [f"  {json.dumps(k)}: {json.dumps(v)}," for k, v in sorted(data.items())]
    target.write_text(
        HEADER
        + "window.IMAGES = {\n" + "\n".join(lines) + "\n};\n"
        + "window.IMG = (path) => {\n"
        + "  if (!(path in window.IMAGES)) throw new Error('not in images.js: ' + path);\n"
        + "  return window.IMAGES[path];\n};\n",
        encoding="utf-8",
    )
    if not keep:
        for image in images:
            image.unlink()
    print(f"{target}: {len(data)} image(s), {target.stat().st_size // 1024} KB")
    return 0


def unpack(assets: Path) -> int:
    target = assets / "images.js"
    count = 0
    for key, b64 in ENTRY.findall(target.read_text(encoding="utf-8")):
        out = assets / Path(key).relative_to("assets")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(base64.b64decode(b64))
        count += 1
    print(f"wrote {count} image(s) into {assets}; run pack again when done")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"pack", "unpack"}:
        print(__doc__)
        return 2
    assets = Path(argv[1])
    if not assets.is_dir():
        print(f"not a folder: {assets}")
        return 2
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    return pack(assets, "--keep" in argv, only) if argv[0] == "pack" else unpack(assets)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
