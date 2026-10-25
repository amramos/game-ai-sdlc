---
name: art-direction
description: Set a game's visual style once — generate two or three style directions as style frames from the GDD's art references (differing in medium, such as pixel art, vector or low-poly 3D, when the GDD's style was only assumed), let the user pick one (or, in a hands-off project, have a critic agent pick and record the choice as assumed, with the runners-up kept for a one-word swap), and save the chosen frames, palette, size rules and prompt core in the repository so every later asset is generated against the same reference. Use after setup when a game has no style guide yet, or when the user asks for concept art, a style guide, art direction or a look for the game.
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

Note **whose decision the style is**. It is **assumed** when the GDD lists it in its "Assumed by the
panel" appendix (as `gdd-handsoff` does) or leaves it `[OPEN]`; it is **the owner's** when the owner
chose it, as in the interactive `gdd`. That decides how far apart the directions go (§3).

## 2. Pick the generator

A style frame is a still image whatever the medium — a low-poly 3D direction needs a rendered-looking
image, not real models, at this stage. Choose per direction, using the first one available that
renders that medium well, and say which:

1. **Local ComfyUI** through the `comfyui-art` skill — free, private, best for pixel art.
2. **Codex image generation**, when the Codex CLI is installed — good for painted concepts. Run it in
   a scratch folder; it writes images on request.
3. **Meshy** (paid) for 3D games or when nothing else is available. Show the cost of every call
   and get a credit budget before the first one; keep a ledger of credits spent.

If none is available, stop and tell the user what each needs.

## 3. Generate two or three directions

Each direction is one interpretation of the GDD's references, and **directions must differ in medium
or rendering, never only in colour.** A palette swap is a variant of a direction, not a new one.

- **The style was assumed (or is `[OPEN]`):** one direction keeps the GDD's style; the others use
  different **media** that suit the game, its camera and its platforms — for example pixel art, 2D
  vector or flat, low-poly 3D, painterly or hand-drawn, ink or woodcut. For each, add one line on
  why it suits this game and one on what it costs to produce (3D needs a model for every asset;
  hand-drawn needs a consistent hand).
- **The owner chose the style:** every direction stays in that medium but differs in **rendering**
  — outlines or none, flat or shaded, perspective, line weight, texture, level of detail.

For each direction, generate the same four **style frames**:

- **a key scene** — the game's main screen as a player would see it;
- **a character** — the protagonist or a typical character, at game scale;
- **a prop** — one interactive object;
- **the most text-heavy screen** — generated from its worst-case content (the longest text, the most
  items), as the player will read it, following the GDD's interface section. Sample content flatters
  a frame that the real build then can't match.

Keep a direction's frames consistent with each other (same prompt core, same seed family). Show the
directions side by side, each with two lines of *for* and *against*, and with a reference game it
resembles.

- **Interactive:** **the user picks one** — or asks for another round that changes one thing.
- **Hands-off:** **the critic picks.** It's a separate agent — a model from another vendor when
  available (e.g. Codex), otherwise a different model from the one that generated the frames and
  no more expensive than the session's — and
  it gets only the GDD's art and interface sections, its references and pillars, and a review sheet
  of the frames. It scores each direction on: fit with the references and the pillars; readability
  at game scale, judged at 1:1 (the text-heavy screen included); consistency across the four frames;
  distinctness from the comparables; and how reliably the generator can repeat it. It returns the pick and, for every direction, one line of why. Within a
  direction, `comfyui-art`'s unattended critic (its `references/critic.md`) can pick between seeds.

## 4. Approve one before multiplying

Before saving the guide, take the chosen direction one step further:

- **one more asset of the kind the game needs most** (a second character, a tile set row), placed
  into the key scene at game scale;
- **the hardest-to-read gameplay asset** (the mark, wound, symbol or unit the player must read to
  decide), composited on its real background. Measure its contrast against its own surroundings,
  per object and in every lighting state, not average colour against average colour;
- **the loudest moment**: a frame of the game's signature action, with the space the layout keeps for
  it.

If anything doesn't sit right, adjust now. Fixing a guide costs one round; fixing fifty assets costs
fifty. In hands-off mode the critic judges the fit, with at most one adjustment round.

### If the winning medium isn't the GDD's

State the cost once, in one paragraph — which GDD lines, project settings and tools change — then make
the switch part of this run, so the project never disagrees with its own style guide:

- **The GDD:** rewrite its art section (style, camera and resolution) to the chosen direction, add a
  dated line to its amendments header ("<date> — art style changed from <old> to <new> by
  art-direction"), and update the matching row of "Assumed by the panel" if it has one.
- **Project settings** (for Godot, `project.godot`):
  - *away from pixel art:* stretch mode `canvas_items`, no integer scaling, linear filtering (remove
    `textures/canvas_textures/default_texture_filter=0`), and a base resolution the art is drawn
    for (e.g. 1920×1080);
  - *to pixel art:* a small base (e.g. 640×360), stretch mode `viewport`, integer scaling, nearest
    filtering;
  - *to 3D:* check the renderer — Compatibility for web builds, Forward+ for desktop only — and say
    whether it changes.
- **Tooling:** the pixel palette linter (`pixelforge`) applies to pixel art only; add or remove its
  configuration, and say which.
- **Validate** as setup does: import, the test suite, and a headless boot with no errors.

Commit the GDD amendment and the settings change together, on a branch, following the project's
rules. In hands-off mode the switch is made and recorded as assumed; a swap back (§7) reverts it the
same way.

## 5. Save the style guide

Into `docs/art/` (outside the build: add a `.gdignore` there for Godot, or the engine's equivalent):

- `frames/` — the chosen style frames and the extra asset, at full resolution;
- `palette.gpl` — the palette derived from the frames (for pixel art, the exact colours, quantized
  to a fixed count; for painted styles, the key colours by role);
- `art-direction.md`, from [art-direction-template.md](art-direction-template.md): the style in a
  paragraph, do and don't, reference games, sizes and canvases, the **prompt core** — the exact
  prompt text, model and settings that produced the frames — **who chose it** (the user, or the
  critic, assumed), and the **interface** section: the material kit every screen is made of; type
  roles (a display face and a body face, at most two or three treatments, each font's source and
  licence); colour jobs (the accent's one job, the signal colours and what they mean); the smallest
  readable size; motion (how things enter, leave and answer a press, with durations and the
  reduced-motion end state); the loudest moment. The GDD's interface section decided what reaches
  the player and why; this decides how it looks. The `game-ui` skill holds the defaults, including
  where to find a licence-safe font when the project has too few;
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
- the result is cleaned onto `palette.gpl` and judged next to the frames at game scale;
- **every asset can be rebuilt from the repository**: its prompt, seed, model and the model's
  licence, and the scripts that clean and composite it, with a `--check` mode that confirms the
  committed file still matches;
- **anything derived from another asset is scripted** (recolours, extra animation frames, effects),
  so a change to the source costs a rerun, not a redraw.

Generated art can ship unless the project's own rules say otherwise; that's the project's call, not
this skill's.

## 7. Hands-off: show the pick, swap with one word

End a hands-off run by showing, in the conversation (and as images where the client can show them):

- **the chosen direction**: its key scene and character, and the critic's two-line reason;
- **each runner-up**: its key scene and one line of why it lost;
- one line: *"This is assumed. Reply with another direction's name to swap; otherwise nothing to do."*

If the user names another direction, **swap**: promote its folder from `runners-up/`, redo §4 (one
extra asset at game scale, and the medium switch if the medium changes) and §5 with it, and record it
as the user's choice. If they confirm, or
the next skill starts without a swap, mark the choice confirmed and delete `runners-up/`.

## 8. Next

Offer the first feature — usually the GDD's core loop as a playable slice — with `feature-planning-handsoff` or `feature-planning`. Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.
