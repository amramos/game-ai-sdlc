#!/usr/bin/env python3
"""Drive a local ComfyUI install from the command line, with one of the model profiles in profiles.py.

Standard library only, so any Python can run it. Talks to ComfyUI's HTTP API
(/prompt, /history, /view, /upload/image) instead of clicking the web UI, which
proved unreliable (the Run button opens a menu, typing lands in node search).

    python comfy.py hardware                   # the profiles this machine can run, and their files
    python comfy.py status
    python comfy.py start                      # starts the portable install if it is down
    python comfy.py start --cuda-device 1 --fp32-vae   # unknown flags go to ComfyUI itself
    python comfy.py txt2img --prompt-file p.txt --seeds 1 2 3 4 --out DIR --prefix concept
    python comfy.py img2img --image src.png --denoise 0.55 --crop 205 40 500 667 \
                            --scale 768 1024 --prompt-file p.txt --seeds 1 2 --out DIR
    python comfy.py free                       # unload models, give VRAM back

txt2img and img2img take --profile (default zimage-int8; the style guide names the project's).

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import profiles  # noqa: E402  (same folder)

# Input name each loader node takes its file through.
FILE_INPUT = {"UNETLoader": "unet_name", "UnetLoaderGGUF": "unet_name", "CLIPLoader": "clip_name",
              "CLIPLoaderGGUF": "clip_name", "VAELoader": "vae_name",
              "CheckpointLoaderSimple": "ckpt_name", "LoraLoaderModelOnly": "lora_name"}


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


def start(wait_s=240, cuda_device=None, extra=()):
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
    cmd = [py, "-s", main, "--windows-standalone-build", "--listen", "127.0.0.1", "--port", str(port)]
    if cuda_device is not None:
        cmd += ["--cuda-device", str(cuda_device)]
    cmd += list(extra)
    subprocess.Popen(cmd, cwd=ROOT, stdout=log, stderr=log, stdin=subprocess.DEVNULL, creationflags=flags)
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


def _options(info, node):
    """The file names a loader node offers, from /object_info; None if the node isn't installed."""
    if node not in info:
        return None
    spec = info[node]["input"]["required"][FILE_INPUT[node]]
    first = spec[0]
    if isinstance(first, list):  # older format: [[names...], {...}]
        return first
    if len(spec) > 1 and isinstance(spec[1], dict):  # newer format: ["COMBO", {"options": [...]}]
        return spec[1].get("options", [])
    return []


def resolve_files(profile, overrides, info):
    """Map each of the profile's file roles to a real file name: (files, None) or (None, problem)."""
    files = {}
    for role, spec in profiles.file_specs(profile).items():
        opts = _options(info, spec["node"])
        if opts is None:
            need = profile.get("custom_nodes", "a newer ComfyUI")
            return None, f"ComfyUI has no {spec['node']} node: install {need}, then restart it"
        if overrides.get(role):
            files[role] = overrides[role]
            continue
        found = profiles.match(spec, opts)
        if not found:
            want = spec.get("name") or spec["pattern"]
            return None, (f"no {role} file matching {want} in models/{spec['folder'][0]} "
                          f"(profile {profile['name']}; pass --{role} to name one)")
        files[role] = found[0]
    if overrides.get("vae") and "vae" not in files:  # an extra VAE for a checkpoint profile
        files["vae"] = overrides["vae"]
    return files, None


def build_graph(profile, files, opts, prompt, seed, latent_nodes):
    """The ComfyUI API graph for one image. Node "13" saves it; "10" is the latent."""
    fam = profile["family"]
    if fam == "zimage":
        unet_in = {"unet_name": files["unet"]}
        if profile["unet"]["node"] == "UNETLoader":
            unet_in["weight_dtype"] = "default"
        clip_in = {"clip_name": files["clip"], "type": opts["clip_type"]}
        if profile["clip"]["node"] == "CLIPLoader":
            clip_in["device"] = "default"
        g = {"1": {"class_type": profile["unet"]["node"], "inputs": unet_in},
             "2": {"class_type": profile["clip"]["node"], "inputs": clip_in},
             "3": {"class_type": "VAELoader", "inputs": {"vae_name": files["vae"]}}}
        clip, vae, model = ["2", 0], ["3", 0], ["1", 0]
    elif fam == "sdxl":
        g = {"1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": files["ckpt"]}},
             "20": {"class_type": "LoraLoaderModelOnly",
                    "inputs": {"model": ["1", 0], "lora_name": files["lora"],
                               "strength_model": opts["lora_strength"]}}}
        clip, vae, model = ["1", 1], ["1", 2], ["20", 0]
        if files.get("vae"):  # e.g. an fp16-fixed SDXL VAE
            g["3"] = {"class_type": "VAELoader", "inputs": {"vae_name": files["vae"]}}
            vae = ["3", 0]
    else:
        raise ValueError(f"unknown profile family {fam}")
    if opts.get("user_lora"):
        g["21"] = {"class_type": "LoraLoaderModelOnly",
                   "inputs": {"model": model, "lora_name": opts["user_lora"],
                              "strength_model": opts["user_lora_strength"]}}
        model = ["21", 0]
    if fam == "zimage":
        g["4"] = {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": model, "shift": opts["shift"]}}
        model = ["4", 0]
    g.update({
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": clip, "text": prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": clip, "text": "low quality"}},
        "11": {"class_type": "KSampler", "inputs": {
            "model": model, "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["10", 0],
            "seed": seed, "steps": opts["steps"], "cfg": opts["cfg"], "sampler_name": opts["sampler"],
            "scheduler": opts["scheduler"], "denoise": opts.get("denoise", 1.0)}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": vae}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": ""}},
    })
    g.update(latent_nodes(vae))
    return g


def options(a, profile):
    """Sampler settings: the profile's, with any flag the caller gave on top."""
    opts = dict(profile["settings"])
    for key in ("steps", "cfg", "shift", "w", "h"):
        if getattr(a, key, None) is not None:
            opts[key] = getattr(a, key)
    opts["denoise"] = getattr(a, "denoise", 1.0)
    opts["user_lora"], opts["user_lora_strength"] = a.lora, a.lora_strength
    return opts


def _run(a, latent_nodes):
    if not is_up():
        print("ComfyUI is down; run: python comfy.py start")
        return 1
    prompt = open(a.prompt_file, encoding="utf-8").read().strip() if a.prompt_file else a.prompt
    if not prompt:
        print("give --prompt or --prompt-file")
        return 2
    profile = profiles.get(a.profile)
    overrides = {r: getattr(a, r, None) for r in ("unet", "clip", "vae", "ckpt")}
    files, problem = resolve_files(profile, overrides, _get_json("/object_info", timeout=60))
    if problem:
        print(problem)
        return 2
    opts = options(a, profile)
    os.makedirs(a.out, exist_ok=True)
    jobs = []
    for seed in a.seeds:
        g = build_graph(profile, files, opts, prompt, seed, lambda vae: latent_nodes(opts, vae))
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
    print(f"{len(results)} image(s) in {int(time.time() - t0)} s with profile {profile['name']}")
    return 0


LATENT = {"zimage": "EmptySD3LatentImage", "sdxl": "EmptyLatentImage"}


def empty_latent(family):
    def nodes(opts, vae):
        return {"10": {"class_type": LATENT[family],
                       "inputs": {"width": opts["w"], "height": opts["h"], "batch_size": 1}}}
    return nodes


def txt2img(a):
    return _run(a, empty_latent(profiles.get(a.profile)["family"]))


def img2img(a):
    name = upload(a.image)

    def nodes(opts, vae):
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
        n["10"] = {"class_type": "VAEEncode", "inputs": {"pixels": src, "vae": vae}}
        return n
    return _run(a, nodes)


def hardware():
    """The machine's hardware, the profiles that fit, and which of their files are in place."""
    hw = profiles.detect()
    rec = profiles.recommend(hw)
    print(profiles.render(hw, rec))
    info = _get_json("/object_info", timeout=60) if is_up() else None
    for name in rec["fits"] or [profiles.DEFAULT]:
        p = profiles.get(name)
        if info is not None:
            _, problem = resolve_files(p, {}, info)
            print(f"  {name}: {'ready' if not problem else problem}")
        elif ROOT and os.path.isdir(os.path.join(ROOT, "ComfyUI")):
            gone = profiles.missing(p, ROOT)
            print(f"  {name}: " + ("files in place" if not gone else "missing " + ", ".join(gone)))
        else:
            print(f"  {name}: ComfyUI not found (set COMFYUI_ROOT), so its files weren't checked")
    return 0


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
    sub.add_parser("hardware")
    s = sub.add_parser("start", help="unknown flags are passed on to ComfyUI (e.g. --fp32-vae)")
    s.add_argument("--wait", type=int, default=240)
    s.add_argument("--cuda-device", type=int, help="which GPU ComfyUI runs on (see `hardware`)")
    sub.add_parser("free")
    for name in ("txt2img", "img2img"):
        g = sub.add_parser(name)
        g.add_argument("--profile", default=profiles.DEFAULT, choices=list(profiles.PROFILES),
                       help="model profile from profiles.py; use the one the style guide names")
        g.add_argument("--prompt")
        g.add_argument("--prompt-file")
        g.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4])
        g.add_argument("--out", required=True, help="local folder the finished PNGs are copied into")
        g.add_argument("--prefix", default="img")
        g.add_argument("--timeout", type=int, default=600)
        g.add_argument("--steps", type=int, help="default: the profile's")
        g.add_argument("--cfg", type=float, help="default: the profile's")
        g.add_argument("--shift", type=float, help="default: the profile's (Z-Image profiles)")
        g.add_argument("--unet", help="diffusion model file instead of the profile's")
        g.add_argument("--clip", help="text encoder file instead of the profile's")
        g.add_argument("--vae", help="VAE file instead of the profile's (SDXL: e.g. an fp16-fixed VAE)")
        g.add_argument("--ckpt", help="checkpoint file (SDXL profiles)")
        g.add_argument("--lora", help="an extra LoRA in models/loras (off by default: it did not help pixel art)")
        g.add_argument("--lora-strength", type=float, default=0.8)
        if name == "txt2img":
            g.add_argument("--w", type=int, help="default: the profile's")
            g.add_argument("--h", type=int, help="default: the profile's")
        else:
            g.add_argument("--image", required=True)
            g.add_argument("--denoise", type=float, default=0.55)
            g.add_argument("--crop", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
            g.add_argument("--scale", type=int, nargs=2, metavar=("W", "H"))
    a, extra = p.parse_known_args()
    if extra and a.cmd != "start":
        p.error("unrecognized arguments: " + " ".join(extra))
    try:
        if a.cmd == "status":
            return status()
        if a.cmd == "hardware":
            return hardware()
        if a.cmd == "start":
            return start(a.wait, a.cuda_device, extra)
        if a.cmd == "free":
            return free()
        return txt2img(a) if a.cmd == "txt2img" else img2img(a)
    except urllib.error.URLError as e:
        print(f"cannot reach ComfyUI at {URL}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
