"""Tests for art-direction's image_sources.py, with a fake environment (no real ComfyUI, CLIs or keys)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE / "plugins" / "game-sdlc" / "skills" / "art-direction" / "scripts" / "image_sources.py"

spec = importlib.util.spec_from_file_location("image_sources", SCRIPT)
image_sources = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(image_sources)


def nothing(_name):
    return None


def down(_url):
    return False


def up(_url):
    return True


class ImageSourcesTests(unittest.TestCase):
    def test_an_empty_machine_reports_nothing_and_points_at_the_agents_own_tools(self) -> None:
        inv = image_sources.inventory(env={}, which=nothing, ping=down)
        self.assertEqual(inv["comfyui"]["state"], "absent")
        self.assertEqual(inv["clis"], [])
        self.assertEqual(inv["keys"], [])
        self.assertIn("your own tools", image_sources.render(inv))

    def test_a_running_server_counts_even_without_comfyui_root(self) -> None:
        inv = image_sources.inventory(env={"COMFYUI_URL": "http://host:9000/"}, which=nothing, ping=up)
        self.assertEqual(inv["comfyui"]["state"], "running")
        self.assertEqual(inv["comfyui"]["url"], "http://host:9000")

    def test_an_installed_but_stopped_comfyui_lists_its_missing_models(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vae = Path(tmp) / "ComfyUI" / "models" / "vae"
            vae.mkdir(parents=True)
            (vae / "ae.safetensors").write_bytes(b"")
            inv = image_sources.inventory(env={"COMFYUI_ROOT": tmp}, which=nothing, ping=down)
        self.assertEqual(inv["comfyui"]["state"], "installed")
        self.assertEqual(len(inv["comfyui"]["missing_models"]), 2)
        self.assertNotIn("vae/ae.safetensors", inv["comfyui"]["missing_models"])

    def test_a_comfyui_root_without_the_comfyui_folder_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            inv = image_sources.inventory(env={"COMFYUI_ROOT": tmp}, which=nothing, ping=down)
        self.assertEqual(inv["comfyui"]["state"], "absent")

    def test_clis_on_path_are_listed(self) -> None:
        inv = image_sources.inventory(env={}, which=lambda name: "/bin/" + name, ping=down)
        self.assertEqual([c["name"] for c in inv["clis"]], ["codex"])

    def test_keys_are_reported_by_name_and_never_by_value(self) -> None:
        secret = "sk-not-a-real-key-123"
        inv = image_sources.inventory(env={"OPENAI_API_KEY": secret, "FAL_KEY": "  "}, which=nothing, ping=down)
        self.assertEqual([k["name"] for k in inv["keys"]], ["OPENAI_API_KEY"])
        self.assertNotIn(secret, image_sources.render(inv))
        self.assertNotIn(secret, repr(inv))


if __name__ == "__main__":
    unittest.main()
