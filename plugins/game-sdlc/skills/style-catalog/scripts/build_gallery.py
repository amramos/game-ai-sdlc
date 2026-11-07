"""Write catalog.html: one page showing every entry in a styles folder, with its key-scene frame,
its index fields and links to its other frames and demo page.

    python build_gallery.py [styles folder]     (default: ../styles next to this script)

The page is generated from index.md, so it never drifts from the catalog; check_entries.py fails
when the committed page is out of date. Standard library only.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_entries import DEFAULT_STYLES, FRAME_EXTS, parse_index  # noqa: E402

FRAMES = ["key-scene", "character", "prop", "text-heavy", "dont", "godot-key-scene"]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Style catalog</title>
<style>
:root {{ --bg: #f6f5f2; --card: #ffffff; --ink: #1d1d22; --dim: #5d5d68; --line: #dddbd5; --link: #2357c9; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg: #16161a; --card: #212127; --ink: #ececf0; --dim: #a3a3ad; --line: #34343c; --link: #8fb0ff; }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 24px 16px 48px; background: var(--bg); color: var(--ink);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 26px; margin: 0 0 4px; }}
.lede {{ color: var(--dim); margin: 0 0 24px; }}
.grid {{ display: grid; gap: 20px; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); }}
article {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }}
article > a img {{ display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }}
.body {{ padding: 14px 16px 16px; }}
h2 {{ font-size: 18px; margin: 0 0 2px; }}
code {{ font-size: 13px; color: var(--dim); }}
dl {{ display: grid; grid-template-columns: auto 1fr; gap: 2px 12px; margin: 10px 0; font-size: 14px; }}
dt {{ color: var(--dim); }}
dd {{ margin: 0; }}
.links {{ display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 14px; }}
a {{ color: var(--link); }}
</style>
</head>
<body>
<main>
<h1>Style catalog</h1>
<p class="lede">{count} looks. Each is a starting point: a game keeps its rules and recipe and makes
the palette, fonts, setting and cast its own. Open a demo to see the look running.</p>
<div class="grid">
{cards}
</div>
</main>
</body>
</html>
"""

CARD = """<article>
<a href="{key_scene}"><img src="{key_scene}" alt="{name}: key scene" loading="lazy"></a>
<div class="body">
<h2>{name}</h2>
<code>{id}</code>
<dl>
<dt>Medium</dt><dd>{medium}</dd>
<dt>Framings</dt><dd>{framings}</dd>
<dt>Mood</dt><dd>{mood}</dd>
<dt>Suits</dt><dd>{suits}</dd>
<dt>Avoid for</dt><dd>{avoid}</dd>
<dt>Cost</dt><dd>{cost}</dd>
<dt>Engines</dt><dd>{engines}</dd>
</dl>
<div class="links">{links}</div>
</div>
</article>"""


def frame(folder: Path, name: str) -> str | None:
    for ext in FRAME_EXTS:
        if (folder / "frames" / f"{name}{ext}").is_file():
            return f"{folder.name}/frames/{name}{ext}"
    return None


def entry_name(folder: Path) -> str:
    style = folder / "style.md"
    if style.is_file():
        for line in style.read_text(encoding="utf-8").splitlines():
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip()
    return folder.name


def render(styles: Path) -> str:
    entries = parse_index((styles / "index.md").read_text(encoding="utf-8"))
    cards = []
    for entry in entries:
        folder = styles / entry.get("id", "")
        links = []
        if (folder / "demo.html").is_file():
            links.append(f'<a href="{escape(folder.name)}/demo.html">Open the demo</a>')
        for name in FRAMES[1:]:
            path = frame(folder, name)
            if path:
                links.append(f'<a href="{escape(path)}">{escape(name)}</a>')
        links.append(f'<a href="{escape(folder.name)}/style.md">style.md</a>')
        joined = lambda key: escape(", ".join(entry.get(key, [])))  # noqa: E731
        cards.append(CARD.format(
            key_scene=escape(frame(folder, "key-scene") or ""),
            name=escape(entry_name(folder)), id=escape(entry.get("id", "")),
            medium=joined("medium"), framings=joined("framings"), mood=joined("mood"),
            suits=joined("suits"), avoid=joined("avoid-for"), cost=escape(entry.get("cost", "")),
            engines=joined("engines"), links=" ".join(links)))
    return PAGE.format(count=len(cards), cards="\n".join(cards))


def main(argv: list[str]) -> int:
    styles = Path(argv[1]) if len(argv) > 1 else DEFAULT_STYLES
    out = styles / "catalog.html"
    out.write_text(render(styles), encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
