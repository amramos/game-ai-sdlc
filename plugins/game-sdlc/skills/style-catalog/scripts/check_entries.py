"""Check a style catalog: the index, every entry's files, budgets, frames and the demo page's safety.

    python check_entries.py [styles folder] [--plugin]

A catalog has two layouts. The **site** (the hosted catalog, or an owner's personal catalog) holds
whole entries: frames, demo pages and their assets. The **plugin** ships only what agents read: the
index and each entry's text, plus one small `preview.jpg` (made by export_plugin.py), under a size
budget, so installing the SDLC stays light. With no folder given, this checks the plugin's own
catalog (../styles next to this script) in plugin mode.

Exits 1 with a list of problems, 0 when clean. Standard library only, so the package check, the
style-catalog skill and a reviewer can all run it.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import re
import struct
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_STYLES = HERE.parent / "styles"

REQUIRED_FIELDS = ["id", "framings", "medium", "mood", "suits", "avoid-for", "cost", "requires",
                   "engines", "version"]
LIST_FIELDS = {"framings", "medium", "mood", "suits", "avoid-for", "requires", "engines"}
MEDIA = {"pixel art", "vector", "painted 2D", "bold 2D illustration", "paper cut-out", "low-poly 3D", "cel-shaded 3D",
         "realistic 3D", "text"}
FRAMINGS = {"top-down", "side", "isometric", "third-person", "first-person", "fixed-stage",
            "fixed-panels", "card-table", "tabletop", "tactics-grid", "on-rails"}
COSTS = {"low", "medium", "high"}
ENGINES = {"web", "godot"}
STYLE_WORDS = 1200
FRAMES = ["key-scene", "character", "prop", "text-heavy"]
FRAME_EXTS = [".png", ".jpg", ".jpeg", ".webp"]
FRAME_LONG_SIDE = 1280
FRAME_BYTES = 300 * 1024
STYLE_SECTIONS = ["## Pitfalls", "## Make it your own", "## Evidence"]
PREVIEW_WIDTH = 640
PREVIEW_BYTES = 80 * 1024
PLUGIN_BYTES = 1536 * 1024      # the whole shipped catalog; demos, art and frames live on the site
SITE_ONLY = ["frames", "assets", "cast", "demo.html"]
GODOT_STAMP = re.compile(r"<!--\s*matched-web-frame:\s*([0-9a-f]{12})\s*-->")

# A demo page runs in the user's browser: scripts only from pinned CDN versions, nothing that talks
# to the network or keeps data, and no code built from strings.
ALLOWED_SCRIPT = re.compile(
    r"^https://(?:cdn\.jsdelivr\.net/npm|unpkg\.com|cdnjs\.cloudflare\.com/ajax/libs)/"
    r"[^/\s]+?[@/]\d+\.\d+\.\d+(?:/|$)"
)
URL = re.compile(r"https?://[^\s\"'`)<>]+")
DEMO_FORBIDDEN = re.compile(
    r"\bfetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|localStorage|sessionStorage|"
    r"indexedDB|document\.cookie|\beval\s*\(|new\s+Function\s*\(|import\s*\(\s*['\"`]https?:"
)
# Every agent that chooses a look reads these files, so text aimed at the agent is a way into other
# people's sessions. A hit is for a person to judge, not proof of bad intent.
INJECTION = re.compile(
    r"ignore (?:all |any |the )?(?:previous|prior|above|earlier) instructions|disregard (?:the |your )?"
    r"(?:previous|prior|above|instructions|rules)|system prompt|you are (?:now )?an? (?:ai|assistant|"
    r"language model)|run (?:this|the following) command|\bcurl\s+-|Invoke-WebRequest|"
    r"<\s*(?:system|instructions?)\s*>",
    re.IGNORECASE,
)
ABSOLUTE_PATH = re.compile(r"\b[A-Za-z]:[\\/][^\s]|(?<![\w.])/(?:home|Users|mnt|c)/[A-Za-z0-9._-]+")


def split_list(value: str) -> list[str]:
    """`[a, b (c, d), e]` -> ['a', 'b (c, d)', 'e']: commas inside parentheses stay."""
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return [value] if value else []
    items, depth, current = [], 0, ""
    for char in value[1:-1]:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            items.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        items.append(current.strip())
    return items


def parse_index(text: str) -> list[dict]:
    """Read the entries from the index's ```yaml block (a small subset of YAML, by design)."""
    block = re.search(r"```yaml\n(.*?)```", text.replace("\r\n", "\n"), re.DOTALL)
    if not block:
        return []
    entries: list[dict] = []
    for line in block.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line)
        if not line.strip():
            continue
        match = re.match(r"^(- |  )([a-z-]+):\s*(.*)$", line)
        if not match:
            continue
        start, key, value = match.groups()
        if start == "- ":
            entries.append({})
        if not entries:
            continue
        entries[-1][key] = split_list(value) if key in LIST_FIELDS else value.strip()
    return entries


def image_size(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        return None
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8X":
            return (int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1)
        if chunk == b"VP8 ":
            width, height = struct.unpack("<HH", data[26:30])
            return width & 0x3FFF, height & 0x3FFF
        if chunk == b"VP8L":
            bits = int.from_bytes(data[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def check_frames(folder: Path, rel: str) -> list[str]:
    problems = []
    frames = folder / "frames"
    for name in FRAMES + ["dont"]:
        found = [frames / f"{name}{ext}" for ext in FRAME_EXTS if (frames / f"{name}{ext}").is_file()]
        if not found:
            if name != "dont":
                problems.append(f"{rel}: missing frames/{name}.png|jpg|webp")
            continue
        for image in found:
            size = image_size(image)
            if size is None:
                problems.append(f"{rel}: frames/{image.name} is not a readable PNG, JPEG or WebP")
            elif max(size) > FRAME_LONG_SIDE:
                problems.append(f"{rel}: frames/{image.name} is {size[0]}×{size[1]}; long side over {FRAME_LONG_SIDE}")
            if image.stat().st_size > FRAME_BYTES:
                problems.append(f"{rel}: frames/{image.name} is {image.stat().st_size // 1024} KB; over {FRAME_BYTES // 1024} KB")
    return problems


def check_palette(path: Path, rel: str) -> list[str]:
    if not path.is_file():
        return [f"{rel}: missing example-palette.gpl"]
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "GIMP Palette":
        return [f"{rel}: example-palette.gpl doesn't start with 'GIMP Palette'"]
    named = [line for line in lines if re.match(r"^\s*\d{1,3}\s+\d{1,3}\s+\d{1,3}\s+\S", line)]
    if len(named) < 4:
        return [f"{rel}: example-palette.gpl has {len(named)} named colours; colour roles need at least 4"]
    return []


def check_demo(path: Path, rel: str) -> list[str]:
    if not path.is_file():
        return []
    problems = []
    text = path.read_text(encoding="utf-8")
    for match in DEMO_FORBIDDEN.finditer(text):
        problems.append(f"{rel}: demo.html uses {match.group(0).strip()!r}; demos make no network calls and keep no data")
    for url in URL.findall(text):
        if not ALLOWED_SCRIPT.match(url):
            problems.append(f"{rel}: demo.html loads {url}; only exact versions from jsdelivr, unpkg or cdnjs")
    return problems


def check_text(folder: Path, rel: str) -> list[str]:
    problems = []
    for path in sorted(folder.rglob("*")):
        if path.suffix not in {".md", ".html", ".gpl"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        name = path.relative_to(folder).as_posix()
        for match in INJECTION.finditer(text):
            problems.append(f"{rel}: {name} has text aimed at an agent: {match.group(0)!r}")
        for match in ABSOLUTE_PATH.finditer(text):
            problems.append(f"{rel}: {name} has an absolute path: {match.group(0)!r}")
        if path.suffix == ".md":
            for url in URL.findall(text):
                if not ALLOWED_SCRIPT.match(url):
                    problems.append(f"{rel}: {name} links {url}; entries carry no links but pinned CDN scripts")
    return problems


def frame_file(folder: Path, name: str) -> Path | None:
    return next((folder / "frames" / f"{name}{ext}" for ext in FRAME_EXTS
                 if (folder / "frames" / f"{name}{ext}").is_file()), None)


def check_godot(folder: Path, text: str, rel: str, plugin: bool = False) -> list[str]:
    """An entry that lists godot proves it with a Godot render of the key scene, matched against the
    web frame as it is now. godot.md records which web frame it matched (a hash of the file), so
    remaking the web demo without re-porting fails here instead of shipping a stale promise."""
    problems: list[str] = []
    if "not yet test-rendered" in text.lower():
        problems.append(f"{rel}: lists godot but godot.md still says it's not yet test-rendered")
    if plugin:   # the render and the web frame are on the site, whose check compares them
        if not GODOT_STAMP.search(text):
            problems.append(f"{rel}: godot.md doesn't say which web frame its render matched")
        return problems
    render, web = frame_file(folder, "godot-key-scene"), frame_file(folder, "key-scene")
    if render is None:
        problems.append(f"{rel}: lists godot but has no frames/godot-key-scene.png|jpg|webp")
    else:
        size = image_size(render)
        if size and max(size) > FRAME_LONG_SIDE or render.stat().st_size > FRAME_BYTES:
            problems.append(f"{rel}: frames/{render.name} is over the frame budget")
    if web is not None:
        current = hashlib.sha256(web.read_bytes()).hexdigest()[:12]
        stamp = GODOT_STAMP.search(text)
        if not stamp:
            problems.append(f"{rel}: godot.md doesn't say which web frame its render matched; after "
                            f"comparing, add <!-- matched-web-frame: {current} -->")
        elif stamp.group(1) != current:
            problems.append(f"{rel}: frames/{web.name} changed since the Godot render was matched; "
                            f"port the change, re-render, compare, then update the stamp to {current}")
    return problems


def check_preview(folder: Path, rel: str) -> list[str]:
    preview = folder / "preview.jpg"
    if not preview.is_file():
        return [f"{rel}: missing preview.jpg; run export_plugin.py"]
    size = image_size(preview)
    if size is None or size[0] > PREVIEW_WIDTH:
        return [f"{rel}: preview.jpg must be a JPEG at most {PREVIEW_WIDTH} px wide"]
    if preview.stat().st_size > PREVIEW_BYTES:
        return [f"{rel}: preview.jpg is {preview.stat().st_size // 1024} KB; over {PREVIEW_BYTES // 1024} KB"]
    return []


def check_entry(folder: Path, entry: dict, plugin: bool = False) -> list[str]:
    rel = folder.name
    problems: list[str] = []
    for field in REQUIRED_FIELDS:
        if not entry.get(field):
            problems.append(f"{rel}: index entry has no {field}")
    for medium in entry.get("medium", []):
        if medium not in MEDIA:
            problems.append(f"{rel}: medium {medium!r} is not in the vocabulary")
    framings = [f.rstrip("*") for f in entry.get("framings", [])]
    for framing, raw in zip(framings, entry.get("framings", [])):
        if framing not in FRAMINGS:
            problems.append(f"{rel}: framing {framing!r} is not in the vocabulary")
        file = folder / "framings" / f"{framing}.md"
        if not file.is_file():
            problems.append(f"{rel}: missing framings/{framing}.md")
        elif not raw.endswith("*") and "not yet built" not in file.read_text(encoding="utf-8").lower():
            problems.append(f"{rel}: framings/{framing}.md must say '(not yet built)' until a game is built in it")
    if entry.get("cost") and entry["cost"] not in COSTS:
        problems.append(f"{rel}: cost {entry['cost']!r} is not low, medium or high")
    for engine in entry.get("engines", []):
        if engine not in ENGINES:
            problems.append(f"{rel}: engine {engine!r} is not web or godot")
        elif not (folder / f"{engine}.md").is_file():
            problems.append(f"{rel}: lists engine {engine} but has no {engine}.md")
    godot = folder / "godot.md"
    if "godot" in entry.get("engines", []) and godot.is_file():
        problems += check_godot(folder, godot.read_text(encoding="utf-8"), rel, plugin)

    style = folder / "style.md"
    if not style.is_file():
        problems.append(f"{rel}: missing style.md")
    else:
        text = style.read_text(encoding="utf-8")
        words = len(text.split())
        if words > STYLE_WORDS:
            problems.append(f"{rel}: style.md has {words} words; the budget is {STYLE_WORDS}")
        front = re.match(r"---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.DOTALL)
        fields = dict(re.findall(r"^([a-z-]+):\s*(.*)$", front.group(1), re.MULTILINE)) if front else {}
        if fields.get("id") != rel:
            problems.append(f"{rel}: style.md frontmatter id {fields.get('id')!r} doesn't match the folder")
        if fields.get("version") != str(entry.get("version")):
            problems.append(f"{rel}: style.md version {fields.get('version')!r} differs from the index's")
        for section in STYLE_SECTIONS:
            if not re.search(rf"^{re.escape(section)}\b", text, re.MULTILINE):
                problems.append(f"{rel}: style.md has no '{section}' section")
        if "colour-rules:" not in text:
            problems.append(f"{rel}: style.md has no colour-rules")
    for name in ["recipe.md"]:
        if not (folder / name).is_file():
            problems.append(f"{rel}: missing {name}")
    problems += check_palette(folder / "example-palette.gpl", rel)
    if plugin:
        problems += check_preview(folder, rel)
        for name in SITE_ONLY:
            if (folder / name).exists():
                problems.append(f"{rel}: {name} belongs on the catalog site; the plugin ships text and preview.jpg")
    else:
        problems += check_frames(folder, rel)
        problems += check_demo(folder / "demo.html", rel)
    problems += check_text(folder, rel)
    return problems


def check_catalog(styles: Path, plugin: bool = False) -> list[str]:
    index = styles / "index.md"
    if not index.is_file():
        return [f"{styles.name}: no index.md"]
    entries = parse_index(index.read_text(encoding="utf-8"))
    if not entries:
        return ["index.md: no entries in its ```yaml block"]
    problems: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        entry_id = entry.get("id", "")
        if entry_id in seen:
            problems.append(f"index.md: duplicate id {entry_id!r}")
        seen.add(entry_id)
        folder = styles / entry_id
        if not entry_id or not folder.is_dir():
            problems.append(f"index.md: entry {entry_id!r} has no folder")
            continue
        problems += check_entry(folder, entry, plugin)
    for folder in sorted(p for p in styles.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if folder.name not in seen:
            problems.append(f"{folder.name}: folder has no entry in index.md")
    if plugin:
        if (styles / "catalog.html").exists():
            problems.append("catalog.html belongs on the catalog site, not in the plugin")
        total = sum(p.stat().st_size for p in styles.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
        if total > PLUGIN_BYTES:
            problems.append(f"the shipped catalog is {total // 1024} KB; the budget is {PLUGIN_BYTES // 1024} KB")
    else:
        problems += check_gallery(styles)
    return problems


def check_gallery(styles: Path) -> list[str]:
    """catalog.html is generated from the index; a missing or stale page is a problem."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_gallery", HERE / "build_gallery.py")
    build_gallery = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build_gallery)
    page = styles / "catalog.html"
    if not page.is_file():
        return ["catalog.html is missing; run scripts/build_gallery.py"]
    if page.read_text(encoding="utf-8").replace("\r\n", "\n") != build_gallery.render(styles):
        return ["catalog.html is out of date; run scripts/build_gallery.py"]
    return []


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    styles = Path(args[0]) if args else DEFAULT_STYLES
    problems = check_catalog(styles, plugin="--plugin" in argv or not args)
    for line in problems:
        print(line)
    print(f"{styles}: {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
