#!/usr/bin/env python3
"""List the image generators this machine already has, without installing or starting anything.

Standard library only. The agent's own tools (a built-in image tool, an MCP server's image tool)
can't be seen from a script: the agent reads its own tool list for those (art-direction §2). This
covers the rest:

- ComfyUI: running, installed but stopped, or absent; the graphics card, the comfyui-art model
  profile it can run, and which of that profile's model files are missing;
- agent CLIs on PATH that can generate images;
- image-service API keys that are set (names only, never values).

    python image_sources.py          # one line per source
    python image_sources.py --json   # the same, as JSON

Always exits 0: an empty machine is an answer, not an error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import urllib.request

# comfyui-art's model profiles and hardware check, which say which model this machine can run.
_PROFILES_PY = Path(__file__).resolve().parents[2] / "comfyui-art" / "scripts" / "profiles.py"
_spec = importlib.util.spec_from_file_location("comfyui_profiles", _PROFILES_PY)
profiles = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(profiles)

# Agent CLIs that can write images on request, with how.
CLIS = {
    "codex": "Codex CLI: its built-in image tool, run with `codex exec` in a scratch folder",
}

# Image-service keys. Set but with no tool to use them, they are an option to offer, not to use.
KEYS = {
    "OPENAI_API_KEY": "OpenAI (image models)",
    "GEMINI_API_KEY": "Google Gemini (image models)",
    "GOOGLE_API_KEY": "Google AI (image models)",
    "REPLICATE_API_TOKEN": "Replicate (hosted open models)",
    "FAL_KEY": "fal (hosted open models)",
    "STABILITY_API_KEY": "Stability AI",
}


def comfyui(env: dict[str, str], ping=None, hw: dict | None = None) -> dict:
    """ComfyUI's state: running, installed (stopped) or absent; the model profile this machine's
    hardware suggests (the default one when the hardware is unknown); and that profile's missing files."""
    url = env.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
    root = env.get("COMFYUI_ROOT", "")
    running = (ping or _ping)(url + "/system_stats")
    rec = profiles.recommend(hw) if hw is not None else {"gpu": None, "fits": [profiles.DEFAULT], "notes": []}
    info: dict = {"url": url, "root": root or None, "missing_models": [],
                  "profile": rec["fits"][0] if rec["fits"] else None,
                  "also_fits": rec["fits"][1:], "gpu": rec["gpu"], "notes": rec["notes"]}
    root_ok = bool(root) and (Path(root) / "ComfyUI").is_dir()
    if root_ok and info["profile"]:
        info["missing_models"] = profiles.missing(profiles.get(info["profile"]), root)
    if running:
        info["state"] = "running"
    elif root_ok:
        info["state"] = "installed"
    else:
        info["state"] = "absent"
    return info


def clis(which=shutil.which) -> list[dict]:
    return [{"name": name, "how": how} for name, how in CLIS.items() if which(name)]


def keys(env: dict[str, str]) -> list[dict]:
    return [{"name": name, "service": service} for name, service in KEYS.items() if env.get(name, "").strip()]


def inventory(env: dict[str, str] | None = None, which=shutil.which, ping=None, hw: dict | None = None) -> dict:
    """What's set up. `hw` is profiles.detect()'s result; None means unknown (the default profile)."""
    env = dict(os.environ) if env is None else env
    return {"comfyui": comfyui(env, ping, hw), "clis": clis(which), "keys": keys(env)}


def render(inv: dict) -> str:
    c = inv["comfyui"]
    lines = []
    if c["state"] == "running":
        lines.append(f"ComfyUI: running at {c['url']}")
    elif c["state"] == "installed":
        lines.append(f"ComfyUI: installed at {c['root']}, not running (comfyui-art starts it)")
    else:
        lines.append("ComfyUI: not installed (COMFYUI_ROOT unset or wrong, nothing answering at " + c["url"] + ")")
    if c.get("gpu"):
        g = c["gpu"]
        lines.append(f"  graphics card: {g['name']}, {round(g['vram_mb'] / 1024)} GB video memory")
    if c.get("profile"):
        p = profiles.PROFILES[c["profile"]]
        tag = "" if p["tested"] else ", untested here"
        lines.append(f"  model profile that fits: {c['profile']} ({p['label']}{tag})")
        if c.get("also_fits"):
            lines.append("  also fits: " + ", ".join(c["also_fits"]))
    else:
        lines.append("  model profile that fits: none for this hardware")
    if c["missing_models"]:
        lines.append(f"  missing model files for {c['profile']}: " + ", ".join(c["missing_models"]))
    for note in c.get("notes", []):
        lines.append(f"  note: {note}")
    if inv["clis"]:
        for cli in inv["clis"]:
            lines.append(f"CLI on PATH: {cli['name']} - {cli['how']}")
    else:
        lines.append("CLI on PATH: none that generates images")
    if inv["keys"]:
        for key in inv["keys"]:
            lines.append(f"API key set: {key['name']} ({key['service']}) - needs a tool to use it; offer, don't wire up")
    else:
        lines.append("API key set: none known")
    lines.append("Not covered here: your own tools. Read your tool list for image tools (built-in or MCP).")
    return "\n".join(lines)


def _ping(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="print JSON instead of lines")
    args = parser.parse_args(argv)
    inv = inventory(hw=profiles.detect())
    print(json.dumps(inv, indent=2) if args.json else render(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
