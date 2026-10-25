---
name: comfyui-art
description: Generate game art locally with ComfyUI and Z-Image Turbo — concept paintings, character portraits, pixel-art sprites and sprite sheets, props, placeholder art — then clean it onto a project's palette and canvas. Use this whenever the user asks to create, draw, generate, iterate on or explore images or art for a game or project ("make a portrait for the old sailor", "we need a sprite for the cook", "try some style variations", "generate placeholder art for the event"), even if they don't mention ComfyUI. Handles starting ComfyUI, the concept → pixel-art → palette pipeline, and both guided iteration (the user picks each round) and unattended iteration (a critic agent picks).
---

# ComfyUI art

Local image generation with ComfyUI and Z-Image Turbo. Everything is driven by two scripts in this
skill's `scripts/` folder — call them with the absolute path of this skill:

- `comfy.py` — `status`, `start`, `free`, `txt2img`, `img2img` (crop, scale, denoise). Talks to
  ComfyUI's HTTP API. Do not drive the ComfyUI web page by clicking: its Run button opens a menu,
  and typed text lands in the node search, which cost several retries in the session this skill
  came from.
- `pixel_post.py` — `key` (background removal), `report` (palette usage and a letter grid),
  `remap` (colour fixes by meaning), `holes`, `sheet` (review sheets), `frames`, `anim`.

The project's own palette tool (e.g. `pixelforge`) does the palette snap; this skill does not
replace it.

## 0. One-time setup (the user's machine)

- ComfyUI **portable** installed; `COMFYUI_ROOT` set to its folder (the one holding
  `python_embeded/` and `ComfyUI/`). `COMFYUI_URL` defaults to `http://127.0.0.1:8188`.
- Z-Image Turbo model files in ComfyUI's model folders: `z_image_turbo_int8_convrot.safetensors`
  (`diffusion_models`), `qwen_3_4b_fp8_mixed.safetensors` (`text_encoders`), `ae.safetensors`
  (`vae`). Other files work through `comfy.py`'s `--unet/--clip/--vae` flags.
- A GPU with about 12 GB of video memory for those files; less works with smaller models, slower.

If any of this is missing, list what's missing with its source and ask the user before
downloading anything. If the user doesn't want a local install, fall back to the next generator
the `art-direction` skill names (Codex image generation, then Meshy).

## 1. Decide the mode first

**Guided** (default): show every round to the user and let them choose and steer. Use it unless
the request clearly says otherwise.

**Unattended**: the user said so — "on your own", "don't wait for me", "unattended", "just come
back with the result", "let another agent review", or they are clearly away (a scheduled task,
a remote trigger). A critic picks each round instead of the user; read `references/critic.md`.

If it's genuinely ambiguous (e.g. "make art for the three new crew" with no word on
involvement), ask once, in one line, and default to guided. State the mode you're using in your
first reply so the user can correct it.

## 2. Start-up

```bash
python <skill>/scripts/comfy.py status   # UP with free VRAM, or DOWN
python <skill>/scripts/comfy.py start    # only if DOWN; ~25 s, detached, log in COMFYUI_ROOT
```

- The int8 model plus the fp8 text encoder need ~11 GB of video memory. `status` splits usage
  into what ComfyUI itself holds (its models stay loaded between jobs — that is fine) and what
  other apps use. Only if **other apps** hold several GB (browsers, Electron apps, games) is there
  a problem: generation spills into system RAM and slows down. Tell the user which kinds of apps
  to close rather than killing anything.
- `comfy.py free` unloads the models when you're done, if the user needs the card back.
- If `start` fails, read the last lines of `comfy_server.log` in the ComfyUI folder.

## 3. Load the project's art rules before prompting

Art has to fit a project, so find its rules first — most of the quality comes from here:
- the style guide the `art-direction` skill saved (`docs/art/`): its chosen frames are image
  references for every new asset, and its prompt core starts every prompt;
- a project skill about art, which takes precedence over this file for anything
  project-specific (palette, canvases, reserved colours, naming, where assets live);
- art direction and contract docs, the palette file (`.gpl`), the palette tool's config (e.g.
  `pixelforge.toml` canvases);
- existing assets of the same kind — the new one must sit next to them.

Pull the few lines that matter (palette intent, reserved colours, canvas, tone) into your prompts
as concrete colours, light and materials. Take **hard rules** (reserved colours, budgets,
canvases, naming) from the tool config rather than the prose — prose can lag the config, and when
they disagree, follow the config and tell the user. If the project has no art rules, ask for
target size and palette, or produce unconstrained concepts and say so.

## 4. Where files go

Work outside the project, in `$COMFYUI_WORK/<project>/<asset>/` (default `~/comfyui-work`; call it
`$W`), one subfolder per round, with the prompt text saved beside its images so any result can
be reproduced.

**Never write generated art into the project** unless the user approves a specific result for
it. Then the project's own rules apply (branch, naming, lint), including any rule the project
sets about generated art.

## 5. Pick the route for the asset

| Asset | Route (details in `references/process.md`) |
|---|---|
| Character portrait / bust | concept painting rounds (last one on a flat backdrop) → img2img close-up if needed → pixel repaint → clean → meaning fixes |
| A set of states of one character | finish one state, derive the rest from it by low-denoise img2img (`process.md` §8) |
| Character sprite / sprite sheet | txt2img pixel sprite at 1024 → clean → meaning fixes → hand edits for extra poses → `frames`/`anim` |
| Prop, event marker, token | txt2img at an integer multiple of the canvas, subject size stated → clean |
| Style exploration | several style directions × 4 seeds → clean each → one board + an in-context composite |
| Icons / UI marks under ~32×32 | don't generate — have a code-writing agent place the pixels |
| Opaque backdrops | generate at an exact multiple, downscale by nearest, snap without keying |

Before writing prompts, read `references/prompting.md` — its table of "wrote X, got Y" is the
difference between one round and four.

## 6. Guided rounds

Each round: generate (usually 4 seeds), build a review sheet with `pixel_post.py sheet` (add
`--actual` once it's pixel art), send it with `SendUserFile` when available, and ask the user to
pick one and say what to change — `AskUserQuestion` with the candidates as options works well.
Give your own read in a few lines (what worked, what missed, what you'd change next) so the user
is choosing, not auditing. Change one or two things per round and say which.

## 7. Done means

- never raw generator output: every asset is cleaned onto the palette and canvas, and each batch is
  checked for the generator's habits (lifelike skin where it doesn't belong, glossy highlights, a
  variant that changed colour but not shape);
- palette tool clean (lint passes), with the dry-run remap read before writing;
- colours checked by **meaning**, not just membership (`references/process.md` §5). For pixel art,
  reserve each signal colour to the asset paths that may use it, and lint that too;
- for pixel art, transformed only by whole numbers (scale ×2, ×3; mirror; shear or redraw instead of
  rotating), since anything else smears the pixels;
- judged at true size **and** composited on real game art at game scale;
- the user has seen it (guided) or received the unattended report (`references/critic.md`);
- honest limits stated — what a human artist would still touch up.

## Troubleshooting

- `rejected:` from `comfy.py` — a model filename is wrong; check `models/diffusion_models`,
  `text_encoders`, `vae` under the ComfyUI folder.
- All-black or mush output — width/height below 512, or VRAM exhausted (`free`, close apps).
- The model ignores the background colour — regenerate; see `prompting.md`, "Backgrounds".
- A pixel-art LoRA exists in `models/loras`; it was tested and rejected (finer, not chunkier
  pixels; anime drift). Only use it if the user asks.
