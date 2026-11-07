---
name: research-image-models
description: Keep comfyui-art's model profiles current — research which open image models run in ComfyUI at each video-memory tier, add a new profile when one is clearly better (never changing a released one), check that existing download sources still resolve, and open a pull request with sources and test steps. Use when the maintainer asks to research, refresh or update the image models or ComfyUI profiles, and on the monthly scheduled run. Also covers marking a profile tested after a real run on a GPU.
---

# Research image models

`plugins/game-sdlc/skills/comfyui-art/scripts/profiles.py` lists the model profiles `comfy.py`
can run and suggests one from the user's graphics card. This skill keeps that list current. It runs
in this repository, by the maintainer or on a monthly schedule, never inside a game project.

Read first: `profiles.py`, the `RELEASED` table in `scripts/tests/test_comfyui_profiles.py`,
`comfyui-art/SKILL.md` §0 and `build_graph` in `comfy.py`.

## The rules

1. **A released profile never changes.** Game projects lock to a profile's name in their style
   guide, so a name always means the same files and settings. To replace one, add a new profile
   and set `"superseded_by"` on the old one; it stops being suggested and keeps working. The only
   field you may edit on a released profile is `source`, when a download link moved. The
   `RELEASED` test fails if you break this; never edit its existing lines to make it pass.
2. **New profiles start untested.** `"tested": False` until someone has generated real assets with
   it on a GPU. A scheduled run never has one, so it never marks anything tested.
3. **Every claim has a source.** File names and sizes come from the model's download page
   (Hugging Face listing or the official repository), ComfyUI support from ComfyUI's own
   repository, templates or release notes, or the custom node's repository. Quality claims need
   two independent sources. Blog round-ups and model-fit calculators disagree with each other and
   with reality often: use them to find candidates, never as the only source for a number.
4. **"No change" is a good result.** Add a profile only when it is clearly better for this SDLC's
   work, not because it is new.

## 1. Research

Look at each tier: under 6 GB, 6–11 GB, 12–15 GB, 16–23 GB, 24 GB and up. For each, find the
open image models that run in ComfyUI on NVIDIA cards of that size, and for each candidate note:

- exact files (model, text encoder, VAE, LoRA), their sizes and where to download them;
- how ComfyUI loads it: core nodes, or which custom nodes (and whether those are maintained);
- the license, and whether it allows commercial games; a non-commercial license rules it out as
  a suggestion;
- how it does on what this SDLC makes: painted concept art, pixel-art sprites and props, flat
  backgrounds, following long prompts. Photorealism counts for little;
- steps, cfg, sampler and resolution its makers recommend.

Use extended web searches, several in one turn. Also check every existing profile's `source`: if
a file was removed or renamed upstream, update `source` (rule 1 allows it) and say so in the
report.

## 2. Decide

Per tier, pick one: keep the current suggestion; add a candidate as a new profile ahead of it in
`ORDER`; or list it under "worth watching" in the report (promising, but thin evidence, a license
question, or immature ComfyUI support). Prefer a profile of a family `comfy.py` already builds
(same prompts, same look across tiers) unless a new family is clearly better.

## 3. Change

For each new profile:

- add it to `PROFILES` with every field the others have (`source`, `note` and `download_gb`
  included), a name that says model and build (`<model>-<build>`), and `"tested": False`;
- place it in `ORDER`; set `superseded_by` on any profile it replaces;
- add its line to `RELEASED` in the test file;
- add its row to the table in `comfyui-art/SKILL.md` §0, and update the README's ComfyUI line if
  the tiers changed;
- a new family also needs: its graph in `comfy.py`'s `build_graph`, its latent node in `LATENT`, a
  graph test, and a prompting notes file in `comfyui-art/references/`, headed as starting notes
  like `prompting-sdxl.md`.

When you need an example in a note or test, keep it neutral and vary the genre (`AGENTS.md`).

## 4. Check and report

Run the three checks from `CONTRIBUTING.md`. Then:

- **Nothing changed:** no branch, no pull request. End with a short report: what was checked, per
  tier what you found, and anything worth watching, with sources.
- **Something changed:** branch `research/image-models-<YYYY-MM>`, commit, push, and open a pull
  request. Its description has: a table per tier (current suggestion, new suggestion, why), the
  sources for every file and claim, licenses, anything you could not verify, and for each new
  profile the exact steps to test it (below). Don't bump the version or edit `CHANGELOG.md`, and
  never merge: the maintainer tests and merges.

## Marking a profile tested

Only on a machine with a GPU that fits the profile, run by or with the maintainer:

1. `python comfy.py hardware` shows the profile and lists what it still needs; download those files.
2. Generate four seeds each of three neutral prompts in different genres (for example a painted
   character bust, a pixel-art prop on a flat background, a top-down terrain tile) with
   `--profile <name>`, and the same with the current tested profile for comparison.
3. Look at them at full size and after `pixel_post.py` cleanup. If the profile holds up, set
   `"tested": True` and say in the pull request what was run, on which card, and how long a batch
   took. If it doesn't, mark it `superseded_by` the profile it was meant to replace, and record why
   in its `note`.
