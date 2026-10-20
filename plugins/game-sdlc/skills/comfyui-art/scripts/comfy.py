#!/usr/bin/env python3
"""Drive a local ComfyUI + Z-Image Turbo install from the command line.

Standard library only, so any Python can run it. Talks to ComfyUI's HTTP API
(/prompt, /history, /view, /upload/image) instead of clicking the web UI, which
proved unreliable (the Run button opens a menu, typing lands in node search).

    python comfy.py status
    python comfy.py start                      # starts the portable install if it is down
    python comfy.py txt2img --prompt-file p.txt --seeds 1 2 3 4 --out DIR --prefix concept
    python comfy.py img2img --image src.png --denoise 0.55 --crop 205 40 500 667 \
                            --scale 768 1024 --prompt-file p.txt --seeds 1 2 --out DIR
    python comfy.py free                       # unload models, give VRAM back

Environment: COMFYUI_ROOT (portable folder), COMFYUI_URL (default http://127.0.0.1:8188).
"""
import argparse
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = os.environ.get("COMFYUI_ROOT", "")
URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")

# Known-good Z-Image Turbo settings (tested 2026-09). The int8 model plus the fp8
# text encoder fit a 12 GB card together; the bf16 model (12.3 GB) does not.
DEFAULTS = {
    "unet": "z_image_turbo_int8_convrot.safetensors",
    "clip": "qwen_3_4b_fp8_mixed.safetensors",
    "clip_type": "lumina2",
    "vae": "ae.safetensors",
    "steps": 8,
    "cfg": 1.0,  # Turbo is distilled: cfg 1, so the negative prompt has no effect
    "sampler": "res_multistep",
    "scheduler": "simple",
    "shift": 3.0,
}


def _get(path, timeout=10):
    with urllib.request.urlopen(URL + path, timeout=timeout) as r:
        return r.read()


def _get_json(path, timeout=10):
    return json.loads(_get(path, timeout))


def _post_json(path, payload, timeout=30):
    req = urllib.request.Request(URL + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return json.loads(body) if body else {}


def is_up():
    try:
        _get_json("/system_stats", timeout=3)
        return True
    except Exception:
        return False


def status():
    if not is_up():
        print(f"DOWN: nothing answering at {URL}")
        return 1
    s = _get_json("/system_stats")
    q = _get_json("/queue")
    dev = s["devices"][0] if s.get("devices") else {}
    mb = lambda b: round(b / 1048576)
    print(f"UP: ComfyUI {s['system'].get('comfyui_version')} at {URL}")
    if dev:
        # vram_free alone is misleading: ComfyUI keeps its own models resident after a job,
        # so a low number right after generating is usually ComfyUI, not other apps.
        held = dev.get("torch_vram_total", 0)
        print(f"  device: {dev.get('name')}  VRAM free {mb(dev.get('vram_free', 0))} MB "
              f"of {mb(dev.get('vram_total', 0))} MB; held by ComfyUI itself {mb(held)} MB; "
              f"used by other apps ~{mb(max(0, dev.get('vram_total', 0) - dev.get('vram_free', 0) - held))} MB")
    print(f"  queue: {len(q['queue_running'])} running, {len(q['queue_pending'])} pending")
    return 0


def start(wait_s=240):
    if is_up():
        print(f"already up at {URL}")
        return 0
    py = os.path.join(ROOT, "python_embeded", "python.exe")
    main = os.path.join(ROOT, "ComfyUI", "main.py")
    if not (os.path.exists(py) and os.path.exists(main)):
        print(f"ComfyUI portable not found under {ROOT} (set COMFYUI_ROOT)")
        return 2
    port = urllib.parse.urlparse(URL).port or 8188
    log = open(os.path.join(ROOT, "comfy_server.log"), "ab")
    flags = 0
    if os.name == "nt":  # survive the calling shell exiting
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen([py, "-s", main, "--windows-standalone-build", "--listen", "127.0.0.1",
                      "--port", str(port)], cwd=ROOT, stdout=log, stderr=log,
                     stdin=subprocess.DEVNULL, creationflags=flags)
    print(f"starting ComfyUI (log: {os.path.join(ROOT, 'comfy_server.log')}) ...")
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if is_up():
            print(f"up after {int(time.time() - t0)} s")
            return status()
        time.sleep(3)
    print(f"not up after {wait_s} s; read the log")
    return 3


def upload(path):
    """Upload a local image into ComfyUI's input folder; returns the stored name."""
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n").encode() + data + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue" \
           f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(URL + "/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["name"]


def _graph(a, prompt, seed, latent_nodes):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": a.unet, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": a.clip, "type": DEFAULTS["clip_type"],
                                                      "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": a.vae}},
        "4": {"class_type": "ModelSamplingAuraFlow",
              "inputs": {"model": ["20", 0] if a.lora else ["1", 0], "shift": a.shift}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "low quality"}},
        "11": {"class_type": "KSampler", "inputs": {
            "model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["10", 0],
            "seed": seed, "steps": a.steps, "cfg": a.cfg, "sampler_name": DEFAULTS["sampler"],
            "scheduler": DEFAULTS["scheduler"], "denoise": getattr(a, "denoise", 1.0)}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": ""}},
    }
    if a.lora:
        g["20"] = {"class_type": "LoraLoaderModelOnly",
                   "inputs": {"model": ["1", 0], "lora_name": a.lora, "strength_model": a.lora_strength}}
    g.update(latent_nodes)
    return g


def _run(a, latent_nodes_for):
    if not is_up():
        print("ComfyUI is down; run: python comfy.py start")
        return 1
    prompt = open(a.prompt_file, encoding="utf-8").read().strip() if a.prompt_file else a.prompt
    if not prompt:
        print("give --prompt or --prompt-file")
        return 2
    os.makedirs(a.out, exist_ok=True)
    jobs = []
    for seed in a.seeds:
        g = _graph(a, prompt, seed, latent_nodes_for())
        g["13"]["inputs"]["filename_prefix"] = f"agent/{a.prefix}_seed{seed}"
        r = _post_json("/prompt", {"prompt": g, "client_id": "comfy-cli"})
        if "prompt_id" not in r:
            print("rejected:", json.dumps(r)[:600])
            return 3
        jobs.append((seed, r["prompt_id"]))
    t0, done, results = time.time(), set(), []
    while len(done) < len(jobs) and time.time() - t0 < a.timeout:
        for seed, pid in jobs:
            if pid in done:
                continue
            h = _get_json(f"/history/{pid}").get(pid)
            if not h:
                continue
            done.add(pid)
            st = h.get("status", {})
            if st.get("status_str") != "success":
                msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
                print(f"seed {seed}: FAILED {json.dumps(msgs)[:600]}")
                continue
            for node in h["outputs"].values():
                for im in node.get("images", []):
                    q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im["subfolder"],
                                                "type": im["type"]})
                    dst = os.path.join(a.out, f"{a.prefix}_seed{seed}.png")
                    with open(dst, "wb") as f:
                        f.write(_get(f"/view?{q}", timeout=60))
                    results.append(dst)
                    print(dst)
        time.sleep(1.5)
    if len(done) < len(jobs):
        print(f"timed out after {a.timeout} s with {len(jobs) - len(done)} job(s) unfinished")
        return 4
    print(f"{len(results)} image(s) in {int(time.time() - t0)} s")
    return 0


def txt2img(a):
    return _run(a, lambda: {"10": {"class_type": "EmptySD3LatentImage",
                                   "inputs": {"width": a.w, "height": a.h, "batch_size": 1}}})


def img2img(a):
    name = upload(a.image)
    def nodes():
        n = {"7": {"class_type": "LoadImage", "inputs": {"image": name}}}
        src = ["7", 0]
        if a.crop:
            x, y, w, h = a.crop
            n["8"] = {"class_type": "ImageCrop", "inputs": {"image": src, "width": w, "height": h, "x": x, "y": y}}
            src = ["8", 0]
        if a.scale:
            n["9"] = {"class_type": "ImageScale", "inputs": {"image": src, "upscale_method": "lanczos",
                                                             "width": a.scale[0], "height": a.scale[1],
                                                             "crop": "disabled"}}
            src = ["9", 0]
        n["10"] = {"class_type": "VAEEncode", "inputs": {"pixels": src, "vae": ["3", 0]}}
        return n
    return _run(a, nodes)


def free():
    if not is_up():
        print("down")
        return 1
    _post_json("/free", {"unload_models": True, "free_memory": True})
    print("models unloaded")
    return status()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("start")
    s.add_argument("--wait", type=int, default=240)
    sub.add_parser("free")
    for name in ("txt2img", "img2img"):
        g = sub.add_parser(name)
        g.add_argument("--prompt")
        g.add_argument("--prompt-file")
        g.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4])
        g.add_argument("--out", required=True, help="local folder the finished PNGs are copied into")
        g.add_argument("--prefix", default="img")
        g.add_argument("--timeout", type=int, default=600)
        g.add_argument("--steps", type=int, default=DEFAULTS["steps"])
        g.add_argument("--cfg", type=float, default=DEFAULTS["cfg"])
        g.add_argument("--shift", type=float, default=DEFAULTS["shift"])
        g.add_argument("--unet", default=DEFAULTS["unet"])
        g.add_argument("--clip", default=DEFAULTS["clip"])
        g.add_argument("--vae", default=DEFAULTS["vae"])
        g.add_argument("--lora", help="file in models/loras (off by default: it did not help pixel art)")
        g.add_argument("--lora-strength", type=float, default=0.8)
        if name == "txt2img":
            g.add_argument("--w", type=int, default=1024)
            g.add_argument("--h", type=int, default=1024)
        else:
            g.add_argument("--image", required=True)
            g.add_argument("--denoise", type=float, default=0.55)
            g.add_argument("--crop", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
            g.add_argument("--scale", type=int, nargs=2, metavar=("W", "H"))
    a = p.parse_args()
    try:
        if a.cmd == "status":
            return status()
        if a.cmd == "start":
            return start(a.wait)
        if a.cmd == "free":
            return free()
        return txt2img(a) if a.cmd == "txt2img" else img2img(a)
    except urllib.error.URLError as e:
        print(f"cannot reach ComfyUI at {URL}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
