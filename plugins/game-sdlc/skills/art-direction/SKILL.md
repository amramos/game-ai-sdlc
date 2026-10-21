---
name: art-direction
description: Set a game's visual style once — generate two or three style directions as style frames from the GDD's art references, let the user pick one (or, in a hands-off project, have a critic agent pick and record the choice as assumed, with the runners-up kept for a one-word swap), and save the chosen frames, palette, size rules and prompt core in the repository so every later asset is generated against the same reference. Use after setup when a game has no style guide yet, or when the user asks for concept art, a style guide, art direction or a look for the game.
argument-hint: "Optional: a style direction to start from"
---

# Art direction: one reference for every asset

Without a fixed reference, each generated asset drifts a little, and fifty assets later the game has
no look. This skill makes the reference first: a small set of **style frames**, saved in the
repository, that every later generation starts from.

## 0. Mode

Follow the project's **working style** (the `Working style` line in `AGENTS.md`), unless the user
says otherwise when calling the skill ("let me pick", "pick for me"):

- **interactive** — the user picks the direction;
- **hands-off** — a **critic agent** picks it, the choice is recorded as **assumed**, and the
  runners-up are kept so the user can swap with one word (§7).

The art style is a taste call, so in hands-off mode it is never decided silently: the user always
sees what was picked and what it was picked over.

## 1. Read what's decided

From the GDD's art section: the style, camera and resolution, reference games and images (with what
each contributes), palette mood and tone. If the references are thin, run one round of questions
(rounds over the frontier, with a recommendation each, as in `gdd-core`) before generating anything.
In hands-off mode the critic answers that round from the GDD instead, and each answer is recorded as
assumed.

## 2. Pick the generator

Use the first one available, and say which:

1. **Local ComfyUI** through the `comfyui-art` skill — free, private, best for pixel art.
2. **Codex image generation**, when the Codex CLI is installed — good for painted concepts. Run it in
   a scratch folder; it writes images on request.
3. **Meshy** (paid) for 3D games or when nothing else is available. Show the cost of every call
   and get a credit budget before the first one; keep a ledger of credits spent.

If none is available, stop and tell the user what each needs.

## 3. Generate two or three directions

Each direction is one interpretation of the GDD's references — e.g. "muted ink and parchment" versus
"saturated arcade". For each, generate the same four **style frames**:

- **a key scene** — the game's main screen as a player would see it;
- **a character** — the protagonist or a typical character, at game scale;
- **a prop** — one interactive object;
- **a UI panel** — one menu or HUD element over the scene.

Keep a direction's frames consistent with each other (same prompt core, same seed family). Show the
directions side by side, each with two lines of *for* and *against*, and with a reference game it
resembles.

- **Interactive:** **the user picks one** — or asks for another round that changes one thing.
- **Hands-off:** **the critic picks.** It's a separate agent — a model from another vendor when
  available (e.g. Codex), otherwise a different model from the one that generated the frames — and
  it gets only the GDD's art section, its references and governing rule, and a review sheet of the
  frames. It scores each direction on: fit with the references; readability at game scale;
  consistency across the four frames; distinctness from the comparables; and how reliably the
  generator can repeat it. It returns the pick and, for every direction, one line of why. Within a
  direction, `comfyui-art`'s unattended critic (its `references/critic.md`) can pick between seeds.

## 4. Approve one before multiplying

Before saving the guide, take the chosen direction one step further: one more asset of the kind the
game needs most (a second character, a tile set row), placed into the key scene at game scale. If it
doesn't sit right, adjust now. Fixing a guide costs one round; fixing fifty assets costs fifty.
In hands-off mode the critic judges the fit, with at most one adjustment round.

## 5. Save the style guide

Into `docs/art/` (outside the build: add a `.gdignore` there for Godot, or the engine's equivalent):

- `frames/` — the chosen style frames and the extra asset, at full resolution;
- `palette.gpl` — the palette derived from the frames (for pixel art, the exact colours, quantized
  to a fixed count; for painted styles, the key colours by role);
- `art-direction.md`, from [art-direction-template.md](art-direction-template.md): the style in a
  paragraph, do and don't, reference games, sizes and canvases, the **prompt core** — the exact
  prompt text, model and settings that produced the frames — and **who chose it** (the user, or the
  critic, assumed);
- hands-off only: `runners-up/<direction>/` — each other direction's frames and prompt core, kept
  until the user confirms the pick (§7), then deleted.

For pixel art, configure the project's palette linter (e.g. `pixelforge`, installed with
`pip install git+https://github.com/amramos/pixelforge`) to the saved palette and canvases, so a
wrong colour or size fails a check instead of a review.

## 6. Every later asset uses it

Any skill or agent generating art for this game starts from `docs/art/art-direction.md`:

- the prompt starts with the prompt core;
- the frames go in as image references wherever the generator accepts them (img2img, reference
  images for Codex, image-to-3D for Meshy);
- the result is cleaned onto `palette.gpl` and judged next to the frames at game scale.

Generated art can ship unless the project's own rules say otherwise; that's the project's call, not
this skill's.

## 7. Hands-off: show the pick, swap with one word

End a hands-off run by showing, in the conversation (and as images where the client can show them):

- **the chosen direction**: its key scene and character, and the critic's two-line reason;
- **each runner-up**: its key scene and one line of why it lost;
- one line: *"This is assumed. Reply with another direction's name to swap; otherwise nothing to do."*

If the user names another direction, **swap**: promote its folder from `runners-up/`, redo §4 (one
extra asset at game scale) and §5 with it, and record it as the user's choice. If they confirm, or
the next skill starts without a swap, mark the choice confirmed and delete `runners-up/`.

## 8. Next

Offer the first feature — usually the GDD's core loop as a playable slice — with `feature-planning-handsoff` or `feature-planning`. Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.
