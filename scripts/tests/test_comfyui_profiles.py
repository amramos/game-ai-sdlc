"""Tests for comfyui-art's model profiles, hardware check and graph building (no real GPU or ComfyUI)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import types
import unittest

PACKAGE = Path(__file__).resolve().parents[2]
SKILLS = PACKAGE / "plugins" / "game-sdlc" / "skills"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


profiles = load("comfyui_profiles_t", SKILLS / "comfyui-art" / "scripts" / "profiles.py")
comfy = load("comfy_t", SKILLS / "comfyui-art" / "scripts" / "comfy.py")
image_sources = load("image_sources_t", SKILLS / "art-direction" / "scripts" / "image_sources.py")


def gpu(name: str, gb: float, index: int = 0) -> dict:
    return {"index": index, "name": name, "vram_mb": int(gb * 1024), "compute_cap": 7.5}


def object_info(names: dict[str, list[str]], newer: bool = False) -> dict:
    """A fake /object_info: each loader node offering the given files."""
    info = {}
    for node, files in names.items():
        spec = ["COMBO", {"options": files}] if newer else [files, {}]
        info[node] = {"input": {"required": {comfy.FILE_INPUT[node]: spec}}}
    return info


class RecommendTests(unittest.TestCase):
    def test_a_12_gb_card_gets_the_tested_default_first(self) -> None:
        rec = profiles.recommend({"gpus": [gpu("RTX 4070 Ti", 12)], "ram_mb": 32000})
        self.assertEqual(rec["fits"][0], profiles.DEFAULT)

    def test_a_6_gb_card_gets_the_compressed_model_then_sdxl_and_a_half_precision_note(self) -> None:
        rec = profiles.recommend({"gpus": [gpu("NVIDIA GeForce GTX 1660 Ti", 6)], "ram_mb": 16384})
        self.assertEqual(rec["fits"], ["zimage-gguf", "sdxl-fast"])
        self.assertTrue(any("fp32-vae" in n for n in rec["notes"]))

    def test_a_tiny_card_gets_no_profile_and_says_so(self) -> None:
        rec = profiles.recommend({"gpus": [gpu("Old card", 2)], "ram_mb": 8000})
        self.assertEqual(rec["fits"], [])
        self.assertTrue(any("another image source" in n for n in rec["notes"]))
        self.assertTrue(any("RAM" in n for n in rec["notes"]))

    def test_no_nvidia_card_gets_no_profile(self) -> None:
        rec = profiles.recommend({"gpus": [], "ram_mb": None})
        self.assertEqual(rec["fits"], [])
        self.assertIsNone(rec["gpu"])

    def test_with_two_cards_the_larger_one_is_used_and_named(self) -> None:
        rec = profiles.recommend({"gpus": [gpu("Small", 12, 0), gpu("Big", 16, 1)], "ram_mb": 64000})
        self.assertEqual(rec["gpu"]["name"], "Big")
        self.assertTrue(any("--cuda-device 1" in n for n in rec["notes"]))

    def test_a_16_gb_card_gets_the_full_precision_model_then_the_12_gb_one(self) -> None:
        rec = profiles.recommend({"gpus": [gpu("RTX 5060 Ti", 16)], "ram_mb": 32000})
        self.assertEqual(rec["fits"][:2], ["zimage-bf16", "zimage-int8"])

    def test_a_superseded_profile_is_never_suggested_but_still_loads(self) -> None:
        old = profiles.PROFILES["zimage-gguf"]
        try:
            profiles.PROFILES["zimage-gguf"] = {**old, "superseded_by": "zimage-int8"}
            rec = profiles.recommend({"gpus": [gpu("Card", 8)], "ram_mb": 32000})
            self.assertNotIn("zimage-gguf", rec["fits"])
            self.assertEqual(profiles.get("zimage-gguf")["name"], "zimage-gguf")
        finally:
            profiles.PROFILES["zimage-gguf"] = old

    def test_every_profile_has_the_fields_the_scripts_and_skills_read(self) -> None:
        for name, p in profiles.PROFILES.items():
            for key in ("label", "family", "tested", "min_vram_mb", "download_gb", "source", "settings",
                        "prompting", "note"):
                self.assertIn(key, p, f"{name} lacks {key}")
            self.assertIn(p["family"], comfy.LATENT, name)
            if p.get("superseded_by"):
                self.assertIn(p["superseded_by"], profiles.PROFILES, name)

    def test_every_profile_names_its_prompting_notes_and_they_exist(self) -> None:
        for name, p in profiles.PROFILES.items():
            self.assertTrue((SKILLS / "comfyui-art" / p["prompting"]).is_file(), name)
        self.assertIn(profiles.DEFAULT, profiles.ORDER)
        self.assertEqual(set(profiles.ORDER), set(profiles.PROFILES))


# What each released profile means. Projects lock to these names in their style guides, so a
# released profile must never change: add a new profile (and a line here) instead, and mark the
# old one superseded_by. Changing a line here is a breaking change for every project using it.
RELEASED = {
    "zimage-bf16": ("zimage", "z_image_turbo_bf16.safetensors", "qwen_3_4b_fp8_mixed.safetensors", 8, 1.0),
    "zimage-int8": ("zimage", "z_image_turbo_int8_convrot.safetensors", "qwen_3_4b_fp8_mixed.safetensors", 8, 1.0),
    "zimage-gguf": ("zimage", "*z*image*turbo*.gguf", "*qwen*3*4b*.gguf", 8, 1.0),
    "sdxl-fast": ("sdxl", "*.safetensors", "*dmd2*sdxl*4step*", 6, 1.0),
}


class FrozenProfileTests(unittest.TestCase):
    def test_released_profiles_never_change(self) -> None:
        for name, (family, model, second, steps, cfg) in RELEASED.items():
            p = profiles.PROFILES.get(name)
            self.assertIsNotNone(p, f"{name} was removed; mark it superseded_by instead")
            first_spec = p.get("unet") or p["ckpt"]
            second_spec = p.get("clip") or p["lora"]
            got = (p["family"], first_spec.get("name") or first_spec["pattern"],
                   second_spec.get("name") or second_spec["pattern"], p["settings"]["steps"], p["settings"]["cfg"])
            self.assertEqual(got, (family, model, second, steps, cfg), f"{name} changed; add a new profile instead")

    def test_every_profile_is_recorded_as_released(self) -> None:
        self.assertEqual(set(profiles.PROFILES), set(RELEASED), "add new profiles to RELEASED")


class DetectTests(unittest.TestCase):
    def test_nvidia_smi_output_is_parsed(self) -> None:
        def run(*_a, **_k):
            return types.SimpleNamespace(stdout="0, NVIDIA GeForce GTX 1660 Ti, 6144, 7.5\n1, Card, 16311, [N/A]\n")
        hw = profiles.detect(run=run, which=lambda _n: "nvidia-smi", ram_mb=lambda: 16384)
        self.assertEqual([g["vram_mb"] for g in hw["gpus"]], [6144, 16311])
        self.assertIsNone(hw["gpus"][1]["compute_cap"])

    def test_a_missing_or_failing_nvidia_smi_means_no_gpus(self) -> None:
        self.assertEqual(profiles.detect(which=lambda _n: None, ram_mb=lambda: None)["gpus"], [])

        def boom(*_a, **_k):
            raise subprocess.TimeoutExpired("nvidia-smi", 10)
        self.assertEqual(profiles.detect(run=boom, which=lambda _n: "x", ram_mb=lambda: None)["gpus"], [])


class FileTests(unittest.TestCase):
    def test_patterns_match_case_insensitively_and_ignore_subfolders(self) -> None:
        spec = profiles.PROFILES["zimage-gguf"]["unet"]
        self.assertEqual(profiles.match(spec, ["sub/Z-Image-Turbo-Q5_K_M.gguf", "flux.gguf"]),
                         ["sub/Z-Image-Turbo-Q5_K_M.gguf"])

    def test_missing_lists_what_is_not_on_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vae = Path(tmp) / "ComfyUI" / "models" / "vae"
            vae.mkdir(parents=True)
            (vae / "ae.safetensors").write_bytes(b"")
            unet = Path(tmp) / "ComfyUI" / "models" / "unet"
            unet.mkdir(parents=True)
            (unet / "z_image_turbo-Q4_K_M.gguf").write_bytes(b"")
            gone = profiles.missing(profiles.get("zimage-gguf"), tmp)
        self.assertEqual(gone, ["text_encoders/*qwen*3*4b*.gguf"])


class GraphTests(unittest.TestCase):
    def build(self, name: str, files: dict, **extra) -> dict:
        p = profiles.get(name)
        opts = {**p["settings"], "user_lora": None, "user_lora_strength": 0.8, **extra}
        latent = comfy.empty_latent(p["family"])
        return comfy.build_graph(p, files, opts, "a lighthouse", 3, lambda vae: latent(opts, vae))

    def test_the_default_profile_builds_the_same_graph_as_before(self) -> None:
        g = self.build("zimage-int8", {"unet": "u", "clip": "c", "vae": "v"})
        self.assertEqual(g["1"]["class_type"], "UNETLoader")
        self.assertEqual(g["2"]["inputs"]["type"], "lumina2")
        self.assertEqual(g["11"]["inputs"]["model"], ["4", 0])
        self.assertEqual(g["4"]["inputs"]["model"], ["1", 0])
        self.assertEqual(g["10"]["class_type"], "EmptySD3LatentImage")
        self.assertEqual((g["11"]["inputs"]["steps"], g["11"]["inputs"]["sampler_name"]), (8, "res_multistep"))

    def test_the_gguf_profile_uses_gguf_loaders_without_core_only_inputs(self) -> None:
        g = self.build("zimage-gguf", {"unet": "u.gguf", "clip": "c.gguf", "vae": "v"})
        self.assertEqual(g["1"], {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "u.gguf"}})
        self.assertNotIn("device", g["2"]["inputs"])
        self.assertEqual(g["10"]["inputs"]["width"], 768)

    def test_the_sdxl_profile_loads_a_checkpoint_and_its_lora(self) -> None:
        g = self.build("sdxl-fast", {"ckpt": "x.safetensors", "lora": "dmd2.safetensors"})
        self.assertEqual(g["1"]["class_type"], "CheckpointLoaderSimple")
        self.assertEqual(g["11"]["inputs"]["model"], ["20", 0])
        self.assertEqual(g["5"]["inputs"]["clip"], ["1", 1])
        self.assertEqual(g["12"]["inputs"]["vae"], ["1", 2])
        self.assertEqual(g["10"]["class_type"], "EmptyLatentImage")
        self.assertNotIn("4", g)

    def test_a_separate_vae_and_an_extra_lora_are_chained_in(self) -> None:
        g = self.build("sdxl-fast", {"ckpt": "x", "lora": "d", "vae": "fix.safetensors"},
                       user_lora="style.safetensors")
        self.assertEqual(g["12"]["inputs"]["vae"], ["3", 0])
        self.assertEqual(g["21"]["inputs"]["model"], ["20", 0])
        self.assertEqual(g["11"]["inputs"]["model"], ["21", 0])


class ResolveTests(unittest.TestCase):
    def test_files_resolve_from_either_object_info_format(self) -> None:
        for newer in (False, True):
            info = object_info({"UnetLoaderGGUF": ["z_image_turbo-Q5_K_M.gguf"],
                                "CLIPLoaderGGUF": ["Qwen3-4B-Q4_K_M.gguf"], "VAELoader": ["ae.safetensors"]}, newer)
            files, problem = comfy.resolve_files(profiles.get("zimage-gguf"), {}, info)
            self.assertIsNone(problem)
            self.assertEqual(files["clip"], "Qwen3-4B-Q4_K_M.gguf")

    def test_a_missing_custom_node_is_named(self) -> None:
        _, problem = comfy.resolve_files(profiles.get("zimage-gguf"), {}, object_info({"VAELoader": ["ae.safetensors"]}))
        self.assertIn("ComfyUI-GGUF", problem)

    def test_a_missing_file_says_which_flag_names_one(self) -> None:
        info = object_info({"CheckpointLoaderSimple": [], "LoraLoaderModelOnly": ["dmd2_sdxl_4step_lora.safetensors"]})
        _, problem = comfy.resolve_files(profiles.get("sdxl-fast"), {}, info)
        self.assertIn("--ckpt", problem)
        files, problem = comfy.resolve_files(profiles.get("sdxl-fast"), {"ckpt": "mine.safetensors"}, info)
        self.assertIsNone(problem)
        self.assertEqual(files["ckpt"], "mine.safetensors")


class ImageSourcesProfileTests(unittest.TestCase):
    def test_a_small_card_is_offered_the_compressed_profile_with_its_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ComfyUI" / "models").mkdir(parents=True)
            inv = image_sources.inventory(env={"COMFYUI_ROOT": tmp}, which=lambda _n: None, ping=lambda _u: False,
                                          hw={"gpus": [gpu("NVIDIA GeForce GTX 1660 Ti", 6)], "ram_mb": 16384})
        c = inv["comfyui"]
        self.assertEqual(c["profile"], "zimage-gguf")
        self.assertIn("diffusion_models/*z*image*turbo*.gguf", c["missing_models"])
        text = image_sources.render(inv)
        self.assertIn("untested here", text)
        self.assertIn("GTX 1660 Ti", text)

    def test_hardware_with_no_profile_says_none_fits(self) -> None:
        inv = image_sources.inventory(env={}, which=lambda _n: None, ping=lambda _u: False,
                                      hw={"gpus": [], "ram_mb": None})
        self.assertIsNone(inv["comfyui"]["profile"])
        self.assertIn("none for this hardware", image_sources.render(inv))


if __name__ == "__main__":
    unittest.main()
