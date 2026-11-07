"""Write the plugin's catalog from the site's: the index, each entry's text and a small preview.

The hosted catalog site holds whole entries (frames, demo pages, art, models). The plugin ships only
what agents read while choosing and building, so installing the SDLC stays light:

    python export_plugin.py <site catalog folder> [plugin styles folder]

(default plugin folder: ../styles next to this script). It replaces the plugin folder's entries with
the site's, writes each `preview.jpg` (640 px wide) from the entry's key-scene frame, and then runs
check_entries.py in plugin mode. Needs Pillow for the preview; the checks themselves don't.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_entries import DEFAULT_STYLES, PREVIEW_BYTES, PREVIEW_WIDTH, check_catalog, frame_file, parse_index  # noqa: E402

TEXT = ["style.md", "recipe.md", "web.md", "godot.md", "example-palette.gpl"]


def preview(source: Path, target: Path) -> None:
    from PIL import Image
    image = Image.open(source).convert("RGB")
    height = round(image.height * PREVIEW_WIDTH / image.width)
    # Pixel art keeps its hard edges when it shrinks by a whole factor; everything else is smoothed.
    pixel = image.width % PREVIEW_WIDTH == 0 and len(image.getcolors(1 << 16) or []) <= 64
    image = image.resize((PREVIEW_WIDTH, height), Image.NEAREST if pixel else Image.LANCZOS)
    for quality in (82, 75, 68, 60):
        image.save(target, "JPEG", quality=quality, optimize=True)
        if target.stat().st_size <= PREVIEW_BYTES:
            return


def export(site: Path, plugin: Path) -> list[str]:
    entries = parse_index((site / "index.md").read_text(encoding="utf-8"))
    plugin.mkdir(parents=True, exist_ok=True)
    for old in plugin.iterdir():
        if old.is_dir():
            shutil.rmtree(old)
        else:
            old.unlink()
    shutil.copy2(site / "index.md", plugin / "index.md")
    for entry in entries:
        source, target = site / entry["id"], plugin / entry["id"]
        target.mkdir()
        for name in TEXT:
            if (source / name).is_file():
                shutil.copy2(source / name, target / name)
        if (source / "framings").is_dir():
            shutil.copytree(source / "framings", target / "framings")
        key = frame_file(source, "key-scene")
        if key is not None:
            preview(key, target / "preview.jpg")
    return check_catalog(plugin, plugin=True)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    site = Path(argv[1])
    plugin = Path(argv[2]) if len(argv) > 2 else DEFAULT_STYLES
    if not (site / "index.md").is_file():
        print(f"not a catalog: {site}")
        return 2
    if plugin.resolve() == site.resolve():
        print("the plugin folder must differ from the site folder")
        return 2
    problems = export(site, plugin)
    for line in problems:
        print(line)
    size = sum(p.stat().st_size for p in plugin.rglob("*") if p.is_file())
    print(f"{plugin}: {size // 1024} KB, {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
