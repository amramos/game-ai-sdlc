# Design: a style catalog for art direction

**Status:** draft for the owner to rule on. Nothing here changes a skill yet; each part becomes its
own pull request once approved.

## 1. The problem

Hands-off runs use up Pro and Plus quotas too fast. Part of that cost is spent inventing a look from
scratch, three times over:

- **gdd-handsoff §2:** each of three concepts invents a camera and medium.
- **prototype:** when a round compares looks, each look is a full HTML build, plus its playtests.
- **art-direction §3–4:** two or three directions × four style frames × several seeds. Every image
  the agent views costs tokens, then a cross-direction critic, seed critics and an adjustment round.

The build phases then rediscover the same lessons each time: a post chain that is too slow without a
GPU, a camera that eases in and doesn't come home, text-only click targets. Those cost whole playtest
rounds.

**What this won't fix.** Most of a hands-off run's tokens probably go to team-lead, adversarial
reviews and screenshot-heavy blind playtests, not to art. §9 measures this before anything is
promised to subscribers.

## 2. The idea

The plugin ships a **catalog of proven looks**. Each entry has a description, reference frames, an
optional page to try the look, and a build recipe agents can follow. The look can come from one of
four paths:

| | Owner present | Hands-off |
|---|---|---|
| **Build a look** (today) | the owner and agents build it together | agents build it, a critic picks, the pick is assumed |
| **From the catalog** (new) | the owner picks an entry | the panel picks an entry, the pick is assumed |

Picking from the catalog replaces only the search. The game still makes the look its own (§5), and
the swap-with-one-word rule of art-direction §7 still applies.

## 3. What an entry is

```
the catalog site (its own repository, published with GitHub Pages)   ← the source
  index.md                 ← one line per entry; the only file read while choosing
  catalog.html             ← the gallery, generated from the index
  <id>/
    style.md               ← the look, signature, readability, colour structure, pitfalls, variations
    recipe.md              ← the core, engine-neutral: rendering, materials, lights as ratios, post chain, sizes, prompt core
    framings/<camera>.md   ← one per camera the look works in: camera values, what the core changes there, its pitfalls
    web.md                 ← three.js snippets, for prototype
    godot.md               ← Godot code, tested against the web frame, for the real build
    frames/                ← key scene, character, prop, text-heavy screen, "don't", and the Godot render
    example-palette.gpl    ← the colours the frames were rendered in; an example, never the default
    demo.html, assets/     ← the look running in a browser with its example art and models

plugins/game-sdlc/skills/style-catalog/styles/   ← exported from the site (export_plugin.py)
  index.md, <id>/ with the text files above and preview.jpg (the key scene, 640 px wide)
```

**Why two places.** An entry's frames, demo, art and models weigh about 1.8 MB; ten entries came to
18 MB, against 433 KB for the whole SDLC before the catalog. Agents read none of it: they read the
index, then one entry's text. Everything an installation downloads must earn its place, so the
plugin ships the text and a 640 px preview for the look question (about 1 MB for ten entries, held
to a budget by the checker), and the rest is a website people browse. Art-direction downloads only
the picked entry's four reference frames, once per game.

**Why stage the loading.** The five drafts total about 72 KB (~18k tokens). An agent that reads the
whole catalog to choose spends most of the savings. So:

| File | Read by | When | Budget |
|---|---|---|---|
| `index.md` | gdd, gdd-handsoff, art-direction | while choosing | ~60 tokens per entry |
| `style.md` | the chooser, then the critic | after a shortlist of ≤3 | ≤1,200 words |
| `preview.jpg` | the owner; the critic | when showing the shortlist | 640 px, ≤80 KB |
| `frames/` (site) | art-direction §3a | after the pick, as image references | 4 images, ≤300 KB each |
| `recipe.md` + one `framings/` file | art-direction §3a | after the pick | — |
| `web.md` / `godot.md` | prototype / developers | while building | only the project's engine |

**Index line**, with the same vocabulary gdd-handsoff §2 already counts, so matching is mechanical:

```yaml
- id: lit-diorama-pixel-sprites
  framings: [isometric*, tactics-grid, side-scroll]   # * = the one it was built and played in
  medium: [pixel art, low-poly 3D]
  mood: [hushed, miniature, nocturnal]
  suits: [tactics, management on one set, small-cast narrative]
  avoid-for: [fast hit-reading, big crowds, many targets at range]
  cost: medium
  requires: [image model for sprites, ComfyUI or equivalent for backdrops]   # checked against art-direction §2's stock-take
  engines: [web, godot]
  version: 1              # a released entry never changes; a real change is a new version
```

`framings` uses gdd-handsoff §2's cameras (top-down, side, isometric, third-person, first-person)
plus a few fixed setups the drafts already use (fixed panels, fixed stage, tabletop, tactics grid).
Unstarred framings are the author's reasoned extension of the core; their files say "not yet
built" so the chooser knows how much is untested.

**Three layers, and only two ship.** The drafts mix them, so each entry is split:

| Layer | Example | Goes in |
|---|---|---|
| **Core**: what makes the look, in any camera | render at 240 lines and scale up; vertex snap; affine textures; 4×4 dither to 31 levels; 64 px textures | `recipe.md` |
| **Framing**: what depends on the camera | a seated first-person head that eases between staged looks; a fixed stage with tilt-shift | `framings/<camera>.md` |
| **Game moments**: what one game did with it | a scripted event that turns the player's head, the sequence for one game's losing state | nowhere: a general pattern goes in the framing file ("staged moments: narrow the FOV and hold"), the rest is dropped |

A framing file says what the core needs to change in that camera (a tilt-shift look needs a camera
looking down; a cut-out theatre needs a front view and fails in first person). When the core can't
work in a camera, that camera isn't listed.

**How generic before it loses value.** The value is in numbers, named techniques, working code and
pitfalls. "Use bloom and fog" is worthless; "bloom threshold above the warm light's value, so only it
blooms" carries over. The test for every line in `recipe.md`: does it state a value, a technique or a
ratio an agent can apply? If it's only an adjective, cut it. The test for the whole entry is a blind
build (§6, `review-style-entry`): an agent with only the entry builds the demo scene, and it's
compared with the frames.

**Engine-specific share.** In the five drafts about 7–13% of the lines are engine API (three.js
classes and passes); the rest are values, techniques and shader math. Ports carry well: colours,
ratios, FOV, render resolution, dither, shader logic (GLSL to Godot's shading language is close).
These need re-tuning per engine: tone-mapping exposure, bloom strength, fog density (each engine
defines it differently), and post chains that one engine has built in and another needs written.
So the core keeps relations ("bloom only the warm light"), and the engine files hold the tuned
numbers.

**Same four frames as art-direction.** When an entry's frames match art-direction §3's set (key
scene, character, prop, text-heavy screen), they can be shown in place of generated directions.
Shipped frames use generic content from no particular game. **Formats:** PNG for pixel art (JPEG
smears pixel edges and adds off-palette colours, and pixel-art PNGs are small anyway); JPEG or WebP
at quality ~85 for everything else. The long side is at most 1280 px. Dimensions, not file size,
decide what an image costs an agent to view, so the pixel cap is what saves tokens.

**`demo.html`** follows prototype's page rules: self-contained, three.js from a CDN at an exact
version, and a render loop that pauses when idle. It includes a palette switcher, so the page shows
what §4 claims: the roles, not the hexes, make the look.

It must work opened straight from the file. Chrome treats each local file as its own origin and
won't let WebGL or a canvas read an image loaded from a neighbouring file, so the scene comes up
blank for the user while a capture run with file-access flags looks fine. Images the page draws
with WebGL go in `assets/images.js` (`scripts/embed_images.py pack`), and models in base64 script
files. Frames are captured without file-access flags, so a capture shows what a user sees.

## 4. Colour: roles and rules, not palettes

The hexes don't define a style; the relationships between colours do ("one warm light in a cold
world", "the accent has one job"). Fixed palettes would give every game in a style the same tone, and
the palette is the cheapest place for a game to differ. So each entry states a **colour structure**:

```yaml
colour-roles:          # names every game in this style fills
  field:   the world's dominant ambient colour
  key:     main light or sky
  rim:     edge and separation light
  accent:  one job, named by the game (game-ui's "colour jobs")
  signal:  [danger, ...]          # each with its meaning
  ink:     [ink, ink-dim, ink-faint]
colour-rules:          # checkable, not prose
  - temp(accent) opposite temp(field)
  - no role but accent shares the accent's temperature
  - value(field) <= 0.35
  - chroma(*) <= 0.5 except [accent, signal]
  - contrast(ink, field) >= 7
  - contrast(accent, field) >= 4.5
```

- **Role names follow game-ui and the style-guide template.** Accent and signal colours are already
  "colour jobs" there; the catalog reuses those words instead of starting a second vocabulary.
- **Where the game's palette comes from,** in order: the owner names one → derived from the GDD's
  tone and references under the entry's rules (the default) → for pixel art with a fixed colour
  count, optionally a Lospec palette of that size, whose colours the agent assigns to roles and
  checks. Lospec is optional because it needs the network, suits pixel art best and still leaves a
  taste call.
- **No palette catalog.** It would be a second thing to maintain, and it would present a second
  choice as already made.
- **A checker.** `style-catalog/scripts/check_palette.py <palette.gpl> <style.md>` reads role names
  from the `.gpl`'s colour names and evaluates `colour-rules`. A script holds steadier than a critic
  judging colour by eye. (Phase 2; until then, the rules are a checklist in §4 of art-direction.)

**Mood and lighting belong to the game, too** (owner's ruling, 2026-11-07). An entry's `mood`
lists the moods the look can carry, not its example's: most looks have no inherent mood once
colour is split out. Colour rules keep only structural needs (neon needs a dark ground, toybox a
saturation ceiling, ink its black masses, a loud-cast look a stage dimmer than the cast).
Lighting schemes (one warm light, daylight, overcast) are variations. The five original drafts
were written from one game's prototypes, so their moods and their lighting ("lantern-lit",
"one warm light") are that game's, not the looks': conversion re-tags them.

Colour pitfalls stay in `style.md`, because they hold for any palette ("reserving warmth costs
signal", "dark low-key scenes swallow distant props").

## 5. How the skills change

**Catalog-biased, in every mode.** Every path looks at the catalog first and builds a look only when
no entry fits (§5a). Interactive runs offer the matching entries first, with "build our own" beside
them; hands-off runs take a fitting entry by default.

**gdd-core, design-tree item 10 (camera and medium).** Run §5a's match on the pitch and
references, then ask one question, recommendation first (owner's format, UX trial 2026-11-07):
*"Based on your pitch and references, I suggest <entry>. You can also pick from the whole
style catalog."* Options: the recommended entry, up to two more entries,
"Create a new look", and Other ("I'll pick from the catalog myself"). The catalog link opens the site's
gallery, generated from the index (`catalog.html`). The question is in `style-catalog` §1
"Asking the owner", so gdd and art-direction ask it the same way. A pick records `Style: catalog <id> v<version>` in the GDD's art section,
with the framing used (§3) and what this game changes (palette, one variation, the accent's job).

**gdd-handsoff §1, intake.** A fifth item with a default:

> 5. **Look:** pick from the catalog, let the panel pick, or have the panel build one. Default:
> *the panel picks, from the catalog when an entry fits*.

With "the panel picks", each of the three concepts runs §5a on its own camera and medium and names
the entry that passes, or "built" when none does. The pick is `panel — assumed` with a runner-up,
as today.

**prototype §1.** With a catalog style, variations never differ in look (already the rule). When the
entry has a demo on the site, prototypes may start from its starter scene, still greybox.

**art-direction: new §3a, "From the catalog".** Replaces §3 when the GDD names an entry:

1. Read `style.md` and `recipe.md`; check `requires` against §2's stock-take. When a requirement is
   missing, offer its setup as §2 does, or fall back to building a look.
2. Make the palette (§4 above).
3. Generate the four frames *for this game*: the entry's prompt core + the game's subject, with the
   entry's frames as image references, one seed round.
4. Go to §4 as usual (extra asset, hardest-to-read asset, loudest moment).
5. Hands-off: the critic doesn't compare directions; it checks fit against the GDD and the entry's
   `avoid-for`, with at most one adjustment round. Runners-up are the next two entries by index
   match, by **name only**. No frames are generated for them, so swapping to one costs a §3a run
   then, not now.

**art-direction §5, the style guide.** It copies the entry into `docs/art/style/` as a **snapshot**
(`style.md`, `recipe.md`, the project engine's file) and records the entry id and plugin version.
Projects don't follow catalog updates silently: a plugin update must never change a game's look.

**team-lead, game-ui.** Developers already read `docs/art/`, which now holds the snapshot's engine
file and pitfalls. The playtest budget changes (§5b).

## 5a. Choosing: catalog first, build when nothing fits

The bias must come from fit, never from cost: an entry that only roughly fits makes a worse game
than a built look, and a look the references don't support is exactly the "average game" hands-off
runs already fight. So the match is mechanical and runs on index lines only (~60 tokens each):

1. **Hard filters**, from what the GDD or the references settle. An entry fails on any one:
   - **medium:** the references' counted medium (gdd-handsoff §2's count) isn't in the entry's
     `medium`. Cel-shaded anime or realistic 3D references fail every entry with no such medium;
   - **framing:** the game's camera isn't in the entry's `framings` (§3);
   - **avoid-for:** the game's core loop or genre is on the entry's `avoid-for`;
   - **requires:** a requirement that §2's stock-take can't meet and the owner hasn't offered to
     set up.
2. **Soft score** for the survivors: one point for each `mood` word the GDD's tone or the
   references share, one for each `suits` the genre or loop matches. An entry needs **at least two
   points** to be offered.
3. **Shortlist:** at most three, highest score first. Only now are their `style.md` files read, and
   the chooser (or the critic, hands-off) confirms the fit in one line each against the references.
   A reference that names what the entry can't do (a realistic open world, say) ends it.
4. **Nothing passes → build the look,** as today. Record one line: which entry came closest and the
   filter it failed. That line is the catalog's to-do list.

**A near miss** (passes the hard filters, scores one) is offered only as a base with a named
variation ("this look, but warm-keyed"), and only interactively. Hands-off runs never stretch an
entry.

**Tuning.** The knobs are the soft threshold (two points), which fields are hard filters, and the
shortlist size. They live in one place, `style-catalog/references/matching.md`, so a change is one
pull request. They are tuned from evidence, not by feel:

- every run writes its §5a record to the style guide: the entries considered, their scores, the
  filter that ended each, and the outcome;
- an **owner swap** after a catalog pick (art-direction §7) means the match was too loose;
- a **near miss the owner accepts**, or a built look the owner later `add`s that closely matches an
  existing entry, means it was too strict;
- the maintainer reviews those records when changing the knobs, and `review-style-entry` (§6)
  reports how often each entry was offered, picked and swapped, when records are shared.

## 5b. Playtests with a catalog style

Blind playtests mostly test the game, not the style. A catalog entry vouches for the look in general,
not for this game's screens (its content, text density, live targets), its onboarding, or its code:
an entry's pitfalls were found by real-window play and can come back in a new game's code. So
screenshot play is trimmed, not dropped, for every catalog entry:

| | Building a look | Catalog entry |
|---|---|---|
| team-lead step 6 visual critic | the look's readability and the layout | the layout only, with the entry's readability rules and pitfalls added to its checklist |
| blind playtesters | 2–4, real window where the question is readability | one cold real-window playtester (onboarding); the rest headless |
| comparing variations | real window for the leading one | headless only: the look isn't a variable |

There is no `proven` status gating this (owner's ruling): an entry is a guide for agents, and an
owner who dislikes the result iterates on it. The one cold real-window playtester still catches
what a weak entry gets wrong in this game. Each entry keeps a short **Evidence** section in
`style.md` (what it was built and played in, in general terms) for the reviewer and the chooser.

## 6. Growing the catalog: the `style-catalog` skill

One shipped skill owns the catalog. It holds the entries and three actions. Two layers, like the
taste profile:

- **Shipped:** `style-catalog/styles/`, curated by the maintainer through pull requests.
- **Personal:** `styles/` in the taste profile's folder (`$GAME_SDLC_TASTE`, default
  `~/.game-sdlc/`, next to `taste.md`). Read after the shipped index and marked as personal in any
  list. Private: it never leaves the machine unless `propose` sends an entry.

### `browse`

Shows the index (both layers) with each entry's key-scene frame, filtered by camera, medium or mood
when asked. Opens `demo.html` where one exists. gdd-core (design-tree item 10), gdd-handsoff and art-direction call
the same filter; the owner can also call it directly ("show me the art styles").

### `add`: from the game you're working in

For any user, in a project whose style guide is confirmed (art-direction §7). art-direction §8
offers it once: *"Add this look to your catalog?"*

1. **Read what exists.** art-direction already wrote most of an entry: `docs/art/art-direction.md`,
   the frames, the prompt core, the palette. Add the code that makes the look (camera, lights,
   shaders, post chain), and the pitfalls from playtest findings and the visual critic's reports.
   No research: it copies decisions that are already written down.
2. **Make it generic.** Build the leak list from the project itself: the game's title, the GDD
   glossary, its characters and places, and every project path. Search the draft for each term and
   rewrite or remove every hit. Recipe parts built for this game's subject become general ones.
   The palette becomes colour roles plus rules (§4), and the actual colours become
   `example-palette.gpl`.
   **Protect the source game from clones.** A look harvested from a game the owner may release
   carries its techniques, never its identity:
   - a new example palette, re-chosen rather than shifted, that still passes the entry's rules;
   - no fonts, title treatment, interface documents or reference list copied as a set: the game's
     own combination is its fingerprint, so the entry lists options and the game's pick is not
     singled out;
   - examples, frames and framing notes use settings and genres far from the source game;
   - the entry's `suits` stays honest but doesn't spell out the source game's exact genre mix;
   - a **Make it your own** section lists what every game in the look must change (palette,
     fonts and title treatment, interface material, setting and cast), and art-direction's critic
     checks it before approving a style guide built on the entry.
3. **Record the evidence** in `style.md` in general terms ("a 2D game in development, played at
   1080p and on a handheld"), never the game's name. `engines` lists only the engines the recipe
   was run in; the starred framing is the one it was built and played in.
4. **Save to the personal catalog.** A personal entry may keep the game's own frames, because it
   stays private, unless the owner marks the game as one to release: then frames are made fresh, as
   for a shipped entry. It is usable in the owner's next game at once, with no release needed.

### `propose`: from a personal entry to the plugin

1. **Check that it's ready to share:** the four frames regenerated with generic content (the only
   step that spends image generation, using the entry's own prompt core); a clean leak scan; the
   entry validator passing (below); a generator licence that allows sharing the frames; no
   duplicate of a shipped entry (a near match is proposed as one of that entry's *Variations*
   instead).
2. **Show exactly what will become public and wait for a yes.** A pull request publishes the look,
   and for an unreleased game the look itself may be sensitive. Nothing from `taste.md` is ever
   included.
3. **Open the pull request** with `gh`: fork, branch `style/<id>`, the entry under
   `style-catalog/styles/<id>/`, and its index line. The description names the entry's evidence,
   not the game it came from. Without `gh` or a GitHub account, it writes a ready-to-attach folder
   and links the repository's issue template instead. It never merges.

**The maintainer** runs the same flow. Their pull request goes to their own repository; the personal
copy works immediately, and the shipped copy arrives with the next release.

### On the repository's side

- **An entry validator in CI** (an extension of `scripts/check_package.py`): every file present;
  index fields from the controlled vocabulary; `style.md` within its budget; frames within their
  size; no absolute paths; `colour-rules` parse.
- **The maintainer reviews** quality, coverage and evidence, with the help of `review-style-entry`
  (below), and decides. Nothing merges without the maintainer.

### `review-style-entry`: the maintainer's evaluator

A repository skill in `.claude/skills/`, like `research-image-models`: it runs only in this
repository, never ships, and never merges. Given a pull request or a local entry folder, it writes a
review for the maintainer with a recommendation (merge, ask for changes, decline) and evidence for
each point:

1. **Safety first, because entries reach other people's agents.** Every user's agent reads
   `index.md` and `style.md` during a run, so a catalog file is a prompt-injection path into every
   session that loads it. Flag any text addressed to an agent (instructions, "ignore", tool or
   command requests, links to fetch, hidden or encoded text) and any prose that isn't describing
   the look. `demo.html` runs in users' browsers: scripts only from the allowed CDNs at exact
   versions, no network calls, no storage beyond the page, no obfuscated code. Any finding here is a
   decline until fixed, whatever the quality.
2. **The validator** (the CI check above), run locally, with its output.
3. **Leaks and privacy.** For an outside entry there's no project glossary to search, so it scans
   for proper nouns, character-like names, file paths, usernames and game titles outside
   `inspired-by`, and flags each one for the maintainer to judge.
4. **Is it new?** It compares the index line with every shipped entry (same medium and framing,
   overlapping mood and suits) and says whether it is a new look or a variation of an existing one.
   For a variation, it proposes merging it into that entry's *Variations*.
5. **Does it carry value?** It applies §3's test to `recipe.md` (values, techniques, ratios; no
   adjective-only lines) and checks that each framing file says what changes in that camera.
6. **Blind build (optional, costs the most).** An agent with only the entry builds the demo scene in
   one framing. The reviewer compares its capture with the entry's frames, and reports what the
   entry failed to say. Rendering follows the machine's GPU rules: the GPU, never software WebGL;
   at most two browsers; close everything afterwards.
7. **Evidence and clone risk.** The Evidence section says what the look was built and played in,
   without naming the game. The entry has a *Make it your own* section, and nothing in it (palette,
   fonts, title treatment, references as a set, example settings) reproduces one game's
   combination. Frames must be regenerable from the entry's prompt core, and the generator's
   licence must allow sharing them.
8. **Coverage.** What the entry adds to the catalog (a new medium, mood or genre), and the §5a
   records that show demand for it, if any.
- **Released entries never change** (as with comfyui-art's model profiles). A real change is a new
  `version`; fixes to typos and links are the only edits in place. Together with the project
  snapshot (§5), no game's look changes under it.

## 7. Turning the five drafts into entries

The owner's draft library (outside this repository) has five entries. Before any of them ship:

- **Coverage.** All five came from one project's prototype round. Splitting out framings (§3)
  widens their cameras: the retro low-poly core, for example, works in first person, a fixed
  third-person horror camera, a tabletop view or a tactics grid. Their drafts share one mood
  (lamplit, melancholy, hushed) only because their palettes and lighting came from one game;
  re-tagged with the range each look can carry (owner's ruling), they cover far more. Their
  `suits` still lean to narrative management and need widening the same way.
- **Leaks.** Remove the *Tried in* sections (game name, characters, absolute paths, the owner's
  verdict on that game), and rewrite recipe parts built for that game's subject into general parts
  (for example, a shader for one particular surface becomes "an animated banded ground plane").
- **Names.** Name each look by what it is, not by a brand: avoid console or publisher trademarks in
  ids and titles. Real games stay in `inspired-by` as references.
- **Split** each file into core, framings and game moments (§3): `style.md`, `recipe.md`,
  `framings/`, `web.md`; drop the game moments; move hexes to `example-palette.gpl` and write the
  colour structure.
- **Godot files.** Each entry is ported to Godot 4 and its key scene rendered in the Compatibility
  renderer before the release that ships it, then compared with the web frame. Until then the entry
  lists `engines: [web]`, and §3a tells a Godot project that the recipe must be ported, using §3's
  list of what re-tunes. `godot.md` records the hash of the web frame it matched, so a web demo
  remade later fails the checker until the port catches up. Three ports went stale exactly that way
  when their web demos were remade after the first Godot round.
- **Frames.** While the catalog is being built, captures from the owner's prototypes may stand in
  as frames, but only from games not meant for release. This is an exception to AGENTS.md's rule
  against carrying a game's art into the SDLC, so it ends before release: every shipped entry gets
  the four standard frames regenerated with generic content, and the validator's leak scan covers
  frame file names. Nothing from a game the owner will release is ever used, even as a stand-in.

**The pilot.** The first entry in the new format, `loud-ink-cast-quiet-stage`, was harvested by hand
from a game the owner will release commercially, following §6's `add` steps. It ships only after its frames were remade from
generated art in an unrelated setting, with nothing from that game. It tested the format: the style guide supplied almost
everything; the colour rules came straight from the game's measured contrasts; and the
clone-protection step needed the most judgment (a new example palette, fonts and title treatments
listed as options, references trimmed, frames to be made in an unrelated setting).

## 8. Rollout

1. The `style-catalog` skill with `browse`, the format, the entry validator, art-direction §3a and
   the §5 snapshot, with 2–3 entries (minor bump).
2. gdd-core (design-tree item 10) and the gdd-handsoff intake read the catalog, browsing first (minor).
3. The playtest budget (§5b) in team-lead and playtest (minor).
4. `add` and the personal layer; art-direction §8's offer (minor).
5. `propose`, `check_palette.py`, the issue template, and `review-style-entry` (the last ships
   nothing, so it needs no version bump).
6. More entries, each its own pull request.

Existing projects are untouched: a GDD without a `catalog` style follows today's path.

## 9. Measuring it

Before promising savings: run gdd-handsoff + art-direction on the same one-line idea twice, once
building a look and once from the catalog. Then compare each run's token use by phase from its
transcript. Report the share art takes in a full hands-off run (through the first team-lead epic),
so the changelog claims only what was measured. Measure the playtest share the same way, before and
after the §5b budget, on one epic built from a catalog entry.

## 10. Rulings and open questions

**Ruled by the owner (2026-11-07):**

| Question | Ruling |
|---|---|
| Hands-off default | Catalog-biased: the catalog first, build only when no entry fits (§5a) |
| Interactive default | Offer the catalog first |
| When to offer `add` | In both modes, once, after the style guide is confirmed; hands-off runs offer it in their report and never add on their own |
| Frames in the plugin | Only a 640 px preview per entry; frames, demos, art and models live on the catalog site (GitHub Pages), so installing the SDLC stays light (§3) |
| Frames from the owner's prototypes | Allowed while building the catalog, only from games not meant for release; regenerated generic before release (§7) |
| A `proven` status | Dropped: entries are guides, owners iterate; an Evidence section stays (§5b) |
| Clones of a released game | Never: harvesting from such a game follows §6's clone protection |
| The pilot entry | `loud-ink-cast-quiet-stage`, from the owner's commercial game (§7) |
| First new entries | Chunky bright pixel art, cel-shaded 3D, toybox low-poly, neon vector glow: written from established technique, each with a `demo.html` that renders its frames; no framing starred until a game is built in it |
| Fixed cameras | No: entries list framings (§3) |
| Godot | Every shipped entry is ported and its render matched to the web frame before release |
| Outside pull requests | Welcome from the first release; the maintainer decides each, with `review-style-entry` |

**Still open:**

1. **The cheapest way to make reference frames in Godot.** Web is answered (2026-11-07): all four
   new entries render their five frames (the four standard ones plus a "don't") from `demo.html`
   with no image generation, including the pixel-art one, whose sprites are drawn from arrays in
   code. One headless Chrome per entry, on the GPU, takes about a minute for five frames. Two
   capture traps, to build into the capture script the skill ships: Windows display scaling
   shrinks the page (force the device scale factor to 1), and headless Chrome's window frame takes
   16×95 px, so open it at 1296×815 and crop to 1280×720. The captures paid for themselves: they
   caught truncated names and a tooltip covering the status chips in one entry, and shadow acne, a
   dark-faced character and a cluttered composition in another, before any game used them. Still
   open: the same for Godot (a headless render of a demo scene per entry), and how an illustrated
   look like the pilot gets its cast without a paid image model.
