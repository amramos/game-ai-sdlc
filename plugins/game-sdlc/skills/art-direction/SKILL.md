---
name: art-direction
description: Set a game's visual style once — start from the style catalog when an entry fits the game (one set of frames made the game's own), otherwise generate two or three style directions as style frames from the GDD's art references (differing in medium, such as pixel art, vector or low-poly 3D, when the GDD's style was only assumed), let the user pick one (or, in a hands-off project, have a critic agent pick and record the choice as assumed, with the runners-up kept for a one-word swap), and save the chosen frames, palette, size rules and prompt core in the repository so every later asset is generated against the same reference. Use after setup when a game has no style guide yet, or when the user asks for concept art, a style guide, art direction or a look for the game.
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

Look for the owner's **taste profile** too, by `taste-profile` §1 (`game-sdlc:taste-profile` in
Claude Code): **never open `taste.md` yourself; run §1's command**, which prints only the
Never lines. Offer the profile if it's missing and the owner is there (its §5). Use it by its §3.
You, choosing the directions, keep only its Never lines. Image generators get nothing from it,
and neither do saved prompts or the style guide. Only the judge reads it whole: the critic in
hands-off mode, or a recommendation check before the owner picks. The profile never picks a medium
or an art style: those come from the GDD.

Note **whose decision the style is**. It is **assumed** when the GDD lists it in its "Assumed by the
panel" appendix (as `gdd-handsoff` does) or leaves it `[OPEN]`; it is **the owner's** when the owner
chose it, as in the interactive `gdd`. That decides how far apart the directions go (§3).

### Check the style catalog first

The `style-catalog` skill (`game-sdlc:style-catalog` in Claude Code) holds looks that
were already worked out. Building a look from scratch is for games no entry fits.

- **The GDD names an entry** (`Style: catalog <id> v<version>`): go to §3a after §2.
- **Otherwise** run `style-catalog` §1's match on the GDD, unless the owner already said they want
  a look built from scratch.
  - **Interactive:** ask the one question in `style-catalog` §1 "Asking the owner": the
    recommended entry first, up to two more, "Create a new look", and the link to the whole
    catalog. The owner picks an entry (§3a), one from the catalog themselves (§3a, recorded as
    their call), or a new look (§3). Offer a near miss as the match file describes.
  - **Hands-off:** the critic (§3's critic, with the same inputs) reads the shortlist's `style.md`
    files and picks the entry that fits best, or rejects them all with one line each. A picked
    entry goes to §3a, recorded as assumed; with none picked, §3 runs as before.
  - **Nothing fits:** hands-off, §3 as before; interactive, the same question recommends "Create a
    new look" and keeps the catalog link.

Keep the match record for the style guide (§5).

## 2. Pick the generator

A style frame is a still image whatever the medium — a low-poly 3D direction needs a rendered-looking
image, not real models, at this stage.

**Use what's already set up before suggesting any install.** Take stock first:

1. **Your own tools.** Read your tool list for anything that generates or edits images: a built-in
   image tool (some agents, Codex among them, have one) or an MCP server's image tool (an image
   model's API, or an image tool inside another service). Note each one's name and whether it is
   paid per call; its description or its server's instructions usually say.
2. **The machine.** Run `python <this skill>/scripts/image_sources.py`. Without installing or
   starting anything, it reports ComfyUI (running, installed but stopped, or absent), the
   graphics card and the `comfyui-art` model profile it can run (with that profile's missing model
   files), agent CLIs on PATH that make images, and which image-service API keys are set, by name
   only.
3. **Say what you found** in one short block: each source, what it's good at, what it costs. In
   hands-off mode it goes in the run's report.

Then choose per direction, using the first available source that renders that medium well, and say
which:

- **Already set up and free, or already paid for:** your own image tool; local ComfyUI through the
  `comfyui-art` skill when it is installed (strong at pixel art and painted concepts, weaker at
  rendered-looking 3D); the Codex CLI's image tool when you are not Codex yourself (good for painted
  concepts and rendered-looking 3D frames such as low poly or toon-shaded; run it in a scratch
  folder). For a source not described here, judge it by one test frame of the direction.
- **Paid per call** (an image API through MCP, Meshy's image tools): show the cost of every call and
  get a budget before the first one; keep a ledger of what was spent. **Meshy**'s real 3D models come
  after a 3D direction is chosen (§4 and later assets).
- **An API key with no tool to use it:** mention it as an option that needs a small setup (an MCP
  server for that service). Never wire it up unasked.

**If nothing set up renders the medium well, offer setups; don't install.** Explain each one in
plain words, with what it costs, and ask which the user wants, if any:

- **ComfyUI**: a free app that runs open image models on your own computer, so images are private
  and cost nothing per picture. It needs an NVIDIA graphics card with at least 4 GB of video
  memory, and roughly 10–20 GB of downloads for the app and models. The model depends on the card:
  name the profile `image_sources.py` suggested, and say whether it is tested. An untested profile
  means the first round is also a test of it, so expect it to be slower or rougher.
  `comfyui-art` §0 has the steps.
- **An agent with built-in image generation**, such as the Codex CLI on a plan that includes it.
- **An image service connected to this agent** through an MCP server: no local hardware, paid per
  image.

In hands-off mode never install or connect anything: use what's set up.

**Record the choice.** The generator and model go into the style guide's prompt core (§5), and every
later asset uses the same one: a different generator draws a different look. For ComfyUI that is
the profile name and the exact model files it resolved to (`comfy.py` prints the profile with
every batch), so another machine knows what it needs to match. Changing generator
later is a style-guide change, so make the frames again with the new one and compare them first.

**The generator never chooses the medium.** If nothing available renders a direction well, show it
anyway, with the closest frame you can make and screenshots of the reference games it follows, and
say what it would take to produce properly. If none is available at all, stop and tell the user what
each needs.

## 3. Generate two or three directions

Each direction is one interpretation of the GDD's references, and **directions must differ in medium
or rendering, never only in colour.** A palette swap is a variant of a direction, not a new one.

- **The style was assumed (or is `[OPEN]`):** one direction keeps the GDD's style; the others use
  different **media** that suit the game, its camera and its platforms — for example pixel art, 2D
  vector or flat, low-poly 3D, painterly or hand-drawn, ink or woodcut. When most of the GDD's
  reference games share a medium the GDD didn't choose, one direction uses it. For each, add one line
  on why it suits this game and one on what it costs to produce (3D needs a model for every asset;
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

No direction's frames use any of `game-ui`'s banned looks unless the user asked for that look in
their own words. A frame that has one anyway is regenerated, never shown or picked.

Keep a direction's frames consistent with each other (same prompt core, same seed family). Show the
directions side by side, each with two lines of *for* and *against*, and with a reference game it
resembles.

- **Interactive:** **the user picks one** — or asks for another round that changes one thing.
- **Hands-off:** **the critic picks.** It's a separate agent — a model from another vendor when
  available (e.g. Codex), otherwise a different model from the one that generated the frames and
  no more expensive than the session's — and
  it gets only the GDD's art and interface sections, its references and pillars, the owner's taste
  profile when there is one (`taste-profile` §3), and a review
  sheet of the frames. It scores each direction on: fit with the references (their media included) and the
  pillars; readability at game scale, judged at 1:1 (the text-heavy screen included); consistency
  across the four frames; and distinctness from the comparables. Separately, and without scoring it,
  it writes what each direction costs to produce (tools, assets, time, paid services): production cost
  informs the owner, it doesn't pick the medium, and a frame's polish says more about the generator
  than about the direction. It returns the pick and, for every direction, one line of why. If a
  direction looks lost on a weak seed pick rather than on its medium, it can send that one direction
  back for one adjustment round before it picks.

  **Seeds within a direction.** A separate seed critic (`comfyui-art`'s
  `references/critic.md`) picks between seeds when it can run on another vendor's model or on a
  model stronger than the generating agent's. When neither is available, the generating agent picks
  by that file's brief as a strict rubric (its option 3), ranking before it states a preference, and
  the run's report says the seed picks had no independent critic. A same-model seed critic adds
  little here: the cross-direction critic sees every pick.

## 3a. From the catalog

Replaces §3 when the look comes from a catalog entry. One direction, made the game's own:

1. **Read the entry:** its `style.md`, `recipe.md` and the framing file for the GDD's camera. Check
   its `requires` against §2's stock-take; when something is missing, offer its setup as §2 does,
   or go back and build a look (§3).
2. **Make the palette** from the entry's colour roles, under its colour rules, for this game's
   tone: the owner's palette when they named one; otherwise derived from the GDD's tone and
   references; for pixel art with a fixed colour count, optionally starting from a published
   palette of that size whose colours you assign to roles. Never the entry's example palette as is.
   Check every colour rule and write the measured values beside the palette.
3. **Make it your own.** Settle each item the entry's "Make it your own" section lists (palette,
   fonts, interface material, setting and cast, whatever it names) for this game, in one short
   list.
4. **Generate the four style frames** (§3's set) for this game: the entry's prompt core with the
   game's palette and subject, the entry's frames as image references where the generator accepts
   them (downloaded from the catalog site, `style-catalog` §3), one seed round. Where the entry's look is drawn in code (its demo page needs no image
   model), build the frames in the engine or a page from the recipe instead, with this game's
   subject and palette.
5. **Check against the entry:** its pitfalls, and its `dont` frame as what not to ship.
   - **Interactive:** show the frames; the owner approves or asks for one change.
   - **Hands-off:** the critic checks fit with the GDD, readability at 1:1, and that every "Make it
     your own" item differs from the entry's examples, with at most one adjustment round.

Then §4 as usual. The runners-up are the shortlist's other entries, **by name only**: no frames are
made for them, so swapping to one (§7) costs a §3a run then, not now.

## 4. Approve one before multiplying

Before saving the guide, take the chosen direction one step further:

- **one more asset of the kind the game needs most** (a second character, a tile set row), placed
  into the key scene at game scale;
- **the hardest-to-read gameplay asset** (the mark, wound, symbol or unit the player must read to
  decide), composited on its real background. Measure its contrast against its own surroundings,
  per object and in every lighting state, not average colour against average colour. **When it
  carries words** (a sign, a label, a number), the words are live text in the game's font, never
  painted by the generator: pick the font now, under the interface section's type roles, and prove
  that element in the engine at native size;
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
    whether it changes. In Compatibility, build the look with `style-catalog`'s
    `references/godot-compatibility.md` at hand: colours are decoded and encoded in other places.
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
  until the user confirms the pick (§7), then deleted. After a catalog pick (§3a) there are no
  runner-up frames: the guide names the runner-up entries instead;
- from the catalog only: `style/`, a **copy** of the entry's `style.md`, `recipe.md`, the chosen
  framing file and the project engine's file (for Godot, with `style-catalog`'s
  `references/godot-compatibility.md` beside it), and nothing else. The style guide records the entry's id and version,
  the match record (`style-catalog` §1) and the "Make it your own" list from §3a. A copy, not a
  link: a plugin update must never change the game's look. Agents building the game read the
  pitfalls and engine notes from there.

Every style guide also keeps the catalog match record, including "built from scratch (closest: …)"
when no entry fitted: those records tune the catalog.

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
- **the catalog**, for a first-time owner: one sentence on what it is, then the pick or why no
  entry fitted, and the link to the gallery (`style-catalog` §1, the hands-off paragraph);
- one line: *"This is assumed. Reply with another direction's name to swap; otherwise nothing to do."*

If the user names another direction, **swap**: promote its folder from `runners-up/`, redo §4 (one
extra asset at game scale, and the medium switch if the medium changes) and §5 with it, and record it
as the user's choice. A catalog runner-up has no folder: swapping to it runs §3a for that entry,
then §4 and §5. If they confirm, or
the next skill starts without a swap, mark the choice confirmed and delete `runners-up/`.

## 8. Next

Offer the first feature — usually the GDD's core loop as a playable slice — with `feature-planning-handsoff` or `feature-planning`. Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.

Start it fresh: planning needs only the GDD and `docs/art/`, not this run's image sheets and rounds.
Where the client can start a new session, hand it over with a short brief, or ask the owner for a
compaction when they're present.
