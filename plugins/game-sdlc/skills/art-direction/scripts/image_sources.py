#!/usr/bin/env python3
"""List the image generators this machine already has, without installing or starting anything.

Standard library only. The agent's own tools (a built-in image tool, an MCP server's image tool)
can't be seen from a script: the agent reads its own tool list for those (art-direction §2). This
covers the rest:

- ComfyUI: running, installed but stopped, or absent, and which default model files are missing;
- agent CLIs on PATH that can generate images;
- image-service API keys that are set (names only, never values).

    python image_sources.py          # one line per source
    python image_sources.py --json   # the same, as JSON

Always exits 0: an empty machine is an answer, not an error.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import urllib.request

# The files comfyui-art's comfy.py uses by default, by ComfyUI model folder.
COMFY_MODELS = {
    "diffusion_models": "z_image_turbo_int8_convrot.safetensors",
    "text_encoders": "qwen_3_4b_fp8_mixed.safetensors",
    "vae": "ae.safetensors",
}

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


def comfyui(env: dict[str, str], ping=None) -> dict:
    """ComfyUI's state: running, installed (stopped) or absent, and any missing default models."""
    url = env.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
    root = env.get("COMFYUI_ROOT", "")
    running = (ping or _ping)(url + "/system_stats")
    info: dict = {"url": url, "root": root or None, "missing_models": []}
    root_ok = bool(root) and (Path(root) / "ComfyUI").is_dir()
    if root_ok:
        models = Path(root) / "ComfyUI" / "models"
        info["missing_models"] = [
            f"{folder}/{name}" for folder, name in COMFY_MODELS.items() if not (models / folder / name).is_file()
        ]
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


def inventory(env: dict[str, str] | None = None, which=shutil.which, ping=None) -> dict:
    env = dict(os.environ) if env is None else env
    return {"comfyui": comfyui(env, ping), "clis": clis(which), "keys": keys(env)}


def render(inv: dict) -> str:
    c = inv["comfyui"]
    lines = []
    if c["state"] == "running":
        lines.append(f"ComfyUI: running at {c['url']}")
    elif c["state"] == "installed":
        lines.append(f"ComfyUI: installed at {c['root']}, not running (comfyui-art starts it)")
    else:
        lines.append("ComfyUI: not installed (COMFYUI_ROOT unset or wrong, nothing answering at " + c["url"] + ")")
    if c["missing_models"]:
        lines.append("  missing default model files: " + ", ".join(c["missing_models"]))
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
    inv = inventory()
    print(json.dumps(inv, indent=2) if args.json else render(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
