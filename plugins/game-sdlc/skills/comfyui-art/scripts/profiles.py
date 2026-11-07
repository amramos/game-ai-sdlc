#!/usr/bin/env python3
"""Model profiles for comfyui-art, and the hardware check that suggests one.

A profile is one complete way of generating: the model files, the ComfyUI nodes that load them,
the latent type, the sampler settings and the prompting notes that go with them. comfy.py builds
its graph from a profile, and art-direction's image_sources.py reports which profile fits the
machine. Standard library only.

    python profiles.py            # this machine's hardware and the profiles that fit it
    python profiles.py --json

Keep the list short. Every profile here should be one someone has generated real assets with;
`tested` says whether that has happened yet, and the skill tells the user when it hasn't.

Projects lock to a profile by name in their style guide, so a name always means the same files and
settings: never change or delete a profile. Add a new one and mark the old one `superseded_by`.
The repository's `research-image-models` skill keeps this list current.
"""
from __future__ import annotations

import argparse
import ctypes
import fnmatch
import json
import os
import shutil
import subprocess
import sys

DEFAULT = "zimage-int8"

# Each file is {"folder": ComfyUI models subfolder(s), "name": exact name} or a "pattern" (glob,
# case-insensitive) when builds of the same model ship under different names.
PROFILES: dict[str, dict] = {
    "zimage-bf16": {
        "label": "Z-Image Turbo, full bf16 model + fp8 text encoder",
        "family": "zimage",
        "tested": False,
        "min_vram_mb": 15000,
        "download_gb": 17,
        "source": "https://huggingface.co/Comfy-Org/z_image_turbo (split_files/)",
        "unet": {"node": "UNETLoader", "folder": ["diffusion_models"],
                 "name": "z_image_turbo_bf16.safetensors"},
        "clip": {"node": "CLIPLoader", "folder": ["text_encoders"],
                 "name": "qwen_3_4b_fp8_mixed.safetensors"},
        "vae": {"node": "VAELoader", "folder": ["vae"], "name": "ae.safetensors"},
        "settings": {"steps": 8, "cfg": 1.0, "sampler": "res_multistep", "scheduler": "simple",
                     "shift": 3.0, "clip_type": "lumina2", "w": 1024, "h": 1024},
        "prompting": "references/prompting.md",
        "note": "The same model as zimage-int8 at full precision (12.3 GB): the same prompts and "
                "look, with a little more fine detail. Doesn't fit a 12 GB card.",
    },
    "zimage-int8": {
        "label": "Z-Image Turbo, int8 model + fp8 text encoder",
        "family": "zimage",
        "tested": True,
        "min_vram_mb": 11500,
        "download_gb": 12,
        "source": "https://huggingface.co/Comfy-Org/z_image_turbo (text encoder and VAE)",
        "unet": {"node": "UNETLoader", "folder": ["diffusion_models"],
                 "name": "z_image_turbo_int8_convrot.safetensors"},
        "clip": {"node": "CLIPLoader", "folder": ["text_encoders"],
                 "name": "qwen_3_4b_fp8_mixed.safetensors"},
        "vae": {"node": "VAELoader", "folder": ["vae"], "name": "ae.safetensors"},
        "settings": {"steps": 8, "cfg": 1.0, "sampler": "res_multistep", "scheduler": "simple",
                     "shift": 3.0, "clip_type": "lumina2", "w": 1024, "h": 1024},
        "prompting": "references/prompting.md",
        "note": "Turbo is distilled to cfg 1, so negative prompts have no effect.",
    },
    "zimage-gguf": {
        "label": "Z-Image Turbo, GGUF Q4_K_M or Q5_K_M model + GGUF text encoder",
        "family": "zimage",
        "tested": False,
        "min_vram_mb": 5800,
        "download_gb": 8,
        "custom_nodes": "ComfyUI-GGUF (city96), for UnetLoaderGGUF and CLIPLoaderGGUF",
        "source": "https://huggingface.co/jayn7/Z-Image-Turbo-GGUF (model); a Qwen3-4B GGUF for the text encoder",
        "unet": {"node": "UnetLoaderGGUF", "folder": ["diffusion_models", "unet"],
                 "pattern": "*z*image*turbo*.gguf"},
        "clip": {"node": "CLIPLoaderGGUF", "folder": ["text_encoders", "clip"],
                 "pattern": "*qwen*3*4b*.gguf"},
        "vae": {"node": "VAELoader", "folder": ["vae"], "name": "ae.safetensors"},
        "settings": {"steps": 8, "cfg": 1.0, "sampler": "res_multistep", "scheduler": "simple",
                     "shift": 3.0, "clip_type": "lumina2", "w": 768, "h": 768},
        "prompting": "references/prompting.md",
        "note": "Same model as zimage-int8, compressed: same prompts, a little less fine detail. "
                "768 px keeps it fast; sprites are downscaled anyway.",
    },
    "sdxl-fast": {
        "label": "SDXL checkpoint + DMD2 4-step LoRA",
        "family": "sdxl",
        "tested": False,
        "min_vram_mb": 3800,
        "download_gb": 7,
        "source": "an SDXL checkpoint of your choice; https://huggingface.co/tianweiy/DMD2 (LoRA)",
        "ckpt": {"node": "CheckpointLoaderSimple", "folder": ["checkpoints"], "pattern": "*.safetensors"},
        "lora": {"node": "LoraLoaderModelOnly", "folder": ["loras"], "pattern": "*dmd2*sdxl*4step*"},
        "settings": {"steps": 6, "cfg": 1.0, "sampler": "lcm", "scheduler": "sgm_uniform",
                     "w": 1024, "h": 1024, "lora_strength": 1.0},
        "prompting": "references/prompting-sdxl.md",
        "note": "Pick an SDXL checkpoint that suits the art direction (base SDXL or a style "
                "fine-tune) and pass it with --ckpt. Different prompting from Z-Image.",
    },
}

# Preference when several profiles fit: the first in this order that fits wins. A superseded
# profile ("superseded_by": "<name>") stays in PROFILES so projects locked to it keep working,
# but is never suggested.
ORDER = ["zimage-bf16", "zimage-int8", "zimage-gguf", "sdxl-fast"]


def get(name: str | None) -> dict:
    name = name or DEFAULT
    if name not in PROFILES:
        raise SystemExit(f"unknown profile {name!r}; known: {', '.join(PROFILES)}")
    return {"name": name, **PROFILES[name]}


def file_specs(profile: dict) -> dict[str, dict]:
    """The model files a profile needs, keyed by role (unet, clip, vae, ckpt, lora)."""
    return {role: profile[role] for role in ("unet", "clip", "vae", "ckpt", "lora") if role in profile}


def match(spec: dict, names: list[str]) -> list[str]:
    """The names (paths inside a model folder, as ComfyUI lists them) that satisfy a file spec."""
    if "name" in spec:
        return [n for n in names if n.replace("\\", "/").split("/")[-1] == spec["name"]]
    pat = spec["pattern"].lower()
    return sorted(n for n in names if fnmatch.fnmatch(n.replace("\\", "/").split("/")[-1].lower(), pat))


def list_folder(root: str, folder: str) -> list[str]:
    """Model files under COMFYUI_ROOT/ComfyUI/models/<folder>, as paths relative to that folder."""
    base = os.path.join(root, "ComfyUI", "models", folder)
    out = []
    for dirpath, _, files in os.walk(base):
        for f in files:
            out.append(os.path.relpath(os.path.join(dirpath, f), base).replace("\\", "/"))
    return out


def missing(profile: dict, root: str) -> list[str]:
    """Files of a profile not found under COMFYUI_ROOT, as 'folder/name-or-pattern'."""
    gone = []
    for spec in file_specs(profile).values():
        names = [n for folder in spec["folder"] for n in list_folder(root, folder)]
        if not match(spec, names):
            gone.append(f"{spec['folder'][0]}/{spec.get('name') or spec['pattern']}")
    return gone


# ---------------------------------------------------------------- hardware

def _ram_mb() -> int | None:
    try:
        if os.name == "nt":
            class MemStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MemStatus()
            m.dwLength = ctypes.sizeof(MemStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.ullTotalPhys // 1048576
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") // 1048576
    except Exception:
        return None


def _nvidia_gpus(run=subprocess.run, which=shutil.which) -> list[dict]:
    if not which("nvidia-smi"):
        return []
    try:
        r = run(["nvidia-smi", "--query-gpu=index,name,memory.total,compute_cap",
                 "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    gpus = []
    for line in r.stdout.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            cap = float(parts[3]) if len(parts) > 3 else None
        except ValueError:
            cap = None
        try:
            gpus.append({"index": int(parts[0]), "name": parts[1], "vram_mb": int(float(parts[2])),
                         "compute_cap": cap})
        except ValueError:
            continue
    return gpus


def detect(run=subprocess.run, which=shutil.which, ram_mb=_ram_mb) -> dict:
    """GPUs (NVIDIA, through nvidia-smi) and system RAM. Never raises."""
    return {"gpus": _nvidia_gpus(run, which), "ram_mb": ram_mb()}


def recommend(hw: dict) -> dict:
    """The profiles that fit, best first, the GPU to run them on, and notes for the user."""
    notes: list[str] = []
    gpus = hw.get("gpus") or []
    ram = hw.get("ram_mb")
    if not gpus:
        notes.append("No NVIDIA card found. ComfyUI also runs on AMD cards and Apple chips, but no "
                     "profile here has been tried there: prefer another image source, or try "
                     "zimage-gguf and expect it to be slow.")
        return {"gpu": None, "fits": [], "notes": notes}
    gpu = max(gpus, key=lambda g: g["vram_mb"])
    fits = [n for n in ORDER
            if gpu["vram_mb"] >= PROFILES[n]["min_vram_mb"] and not PROFILES[n].get("superseded_by")]
    if len(gpus) > 1 and gpu["index"] != 0:
        notes.append(f"Several cards: the largest is #{gpu['index']} ({gpu['name']}). Start ComfyUI on it "
                     f"with `comfy.py start --cuda-device {gpu['index']}`.")
    if "GTX 16" in gpu["name"]:
        notes.append("GTX 16-series cards can produce black images in half precision. If they do, "
                     "start ComfyUI with `comfy.py start --fp32-vae` (or `--force-fp32` if that "
                     "isn't enough).")
    if gpu["vram_mb"] < 11500 and ram is not None and ram < 16000:
        notes.append(f"Only {round(ram / 1024)} GB of system RAM: with a small card, models spill into "
                     "RAM, so 16 GB is a practical minimum and 32 GB is comfortable.")
    if not fits:
        notes.append(f"{gpu['name']} has {round(gpu['vram_mb'] / 1024)} GB of video memory, below every "
                     "profile here. Use another image source.")
    return {"gpu": gpu, "fits": fits, "notes": notes}


def render(hw: dict, rec: dict) -> str:
    lines = []
    if hw.get("gpus"):
        for g in hw["gpus"]:
            lines.append(f"GPU #{g['index']}: {g['name']}, {round(g['vram_mb'] / 1024)} GB video memory")
    else:
        lines.append("GPU: no NVIDIA card found")
    if hw.get("ram_mb"):
        lines.append(f"System RAM: {round(hw['ram_mb'] / 1024)} GB")
    for i, name in enumerate(rec["fits"]):
        p = PROFILES[name]
        tag = "" if p["tested"] else " (untested here)"
        lines.append(f"{'Suggested' if i == 0 else 'Also fits'}: {name} - {p['label']}{tag}")
    for n in rec["notes"]:
        lines.append(f"Note: {n}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    hw = detect()
    rec = recommend(hw)
    print(json.dumps({"hardware": hw, **rec}, indent=2) if a.json else render(hw, rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
