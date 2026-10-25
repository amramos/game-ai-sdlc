"""Export every preset in export_presets.cfg into build/<channel>/, one folder per itch.io channel.

Presets are matched by their platform, not their name, so renaming a preset in the editor is safe.
Standard library only; run from the project root: python tools/ci/export_all.py --out build
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

# platform= value in export_presets.cfg -> (itch.io channel, exported file name; {slug} is filled in)
PLATFORMS: dict[str, tuple[str, str]] = {
    "Windows Desktop": ("windows", "{slug}.exe"),
    "Linux": ("linux", "{slug}.x86_64"),
    "Linux/X11": ("linux", "{slug}.x86_64"),
    "macOS": ("mac", "{slug}.zip"),
    "Web": ("web", "index.html"),
}


def presets(config: str) -> list[tuple[str, str]]:
    """Return (name, platform) for every [preset.N] section, in file order."""
    found: list[tuple[str, str]] = []
    for section in re.split(r"^\[preset\.\d+\]\s*$", config, flags=re.MULTILINE)[1:]:
        body = section.split("\n[", 1)[0]
        name = re.search(r'^name="(.*)"\s*$', body, flags=re.MULTILINE)
        platform = re.search(r'^platform="(.*)"\s*$', body, flags=re.MULTILINE)
        if name and platform:
            found.append((name.group(1), platform.group(1)))
    return found


def project_slug(project: str) -> str:
    match = re.search(r'^config/name="(.*)"\s*$', project, flags=re.MULTILINE)
    title = match.group(1) if match else "game"
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "game"


def default_godot(root: Path) -> str:
    """The Godot the hooks use: GODOT_BIN, then .agents/local/godot (written by setup), then PATH."""
    if os.environ.get("GODOT_BIN"):
        return os.environ["GODOT_BIN"]
    local = root / ".agents" / "local" / "godot"
    if local.is_file():
        configured = local.read_text(encoding="utf-8").strip()
        if configured:
            return configured
    return shutil.which("godot") or "godot"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="build")
    parser.add_argument("--godot", default=None, help="defaults to the Godot the hooks use")
    args = parser.parse_args()

    root = Path.cwd()
    args.godot = args.godot or default_godot(root)
    config_path = root / "export_presets.cfg"
    if not config_path.is_file():
        print("No export_presets.cfg: add presets in the editor (Project > Export) and commit it.")
        return 1
    slug = project_slug((root / "project.godot").read_text(encoding="utf-8"))
    exported = 0
    for name, platform in presets(config_path.read_text(encoding="utf-8")):
        if platform not in PLATFORMS:
            print(f"skip: preset '{name}' targets {platform}, which has no itch.io channel here")
            continue
        channel, file_name = PLATFORMS[platform]
        target = Path(args.out) / channel / file_name.format(slug=slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        print(f"export: '{name}' ({platform}) -> {target}", flush=True)
        result = subprocess.run([args.godot, "--headless", "--export-release", name, str(target)])
        if result.returncode != 0 or not target.exists():
            print(f"export failed for preset '{name}'")
            return 1
        exported += 1
    if exported == 0:
        print("No exportable presets found.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
