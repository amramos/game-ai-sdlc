# The process, stage by stage

The route that produced the best results so far (a pixel-art character portrait, September 2026):
**paint a concept → push it closer → repaint as pixel art → clean onto the palette → fix colours
by meaning → review at true size.** Going straight to a pixel prompt works for simple sprites,
but a painted concept first gives the character far more personality — the owner preferred the
painting-derived portrait over every direct pixel prompt and over the pixel-art LoRA.

All commands below use `scripts/comfy.py` and `scripts/pixel_post.py`; `S` is the skill's
`scripts` folder and `W` the working folder for this asset (see SKILL.md, "Where files go").

## Contents
1. Concept painting
2. Close-up (img2img crop)
3. Pixel-art repaint
4. Background removal and palette clean
5. Colour fixes by meaning
6. Sprites and animation frames
7. Review sheets and in-context check
8. Sets: states and variants of one character
9. Other asset types

---

## 1. Concept painting

Four seeds per round, portrait orientation for characters (`--w 896 --h 1152`), 1024×1024 for
props. Each round takes ~5 s per image once the model is loaded.

```bash
python $S/comfy.py txt2img --prompt-file $W/r1_prompt.txt --w 896 --h 1152 \
       --seeds 11 22 33 44 --out $W/r1 --prefix concept
python $S/pixel_post.py sheet $W/r1/sheet.png $W/r1/concept_seed*.png --scale 1 --labels 1 2 3 4
```

What moved the result, in order of effect (details in `prompting.md`):
1. Describe what is **visible**, never backstory (ages, eras and moods leak from story words).
2. Name the **medium** ("painted character concept art, gouache and oil, loose brushstrokes").
3. Put the project's art direction into concrete colours and light, not adjectives.
4. Fix one thing per round; the model's seed variety is low, so a new seed changes less than a
   new sentence.

Typical convergence: three rounds (fix age/tone, then costume/era, then props).

**If the concept is headed for pixel art, the final concept round needs a flat backdrop in a
colour the subject does not use** (magenta unless the subject is pink or purple). The later
img2img stages keep the source's background whatever the prompt says, so a painterly grey sky
survives into the pixel repaint and then has to be cut away from grey hair and a grey cap. Keep
the atmospheric backdrops for early rounds, where they help judge mood.

Choose the final filename now, not at the end: the project's naming lint may reject names that
seem natural (`old_finn_age3_01.png` failed a two-part pattern; `oldfinn_age3_01.png` passed).

## 2. Close-up (img2img crop)

**Optional**: skip it when the concept is already framed like the target (a half-length concept
for a bust); crop inside the pixel-repaint call instead. It is a technical step, not a judged
round — in guided mode show its result with the pixel round rather than asking separately.

To get a bust from a full-body winner, crop the source and let the model repaint it bigger.
This keeps the identity; a fresh prompt would roll a new person.

```bash
# crop box in SOURCE pixels, aspect = target aspect (3:4 for a 48x64 portrait)
python $S/comfy.py img2img --image $W/r3/concept_seed33.png --crop 300 60 340 453 \
       --scale 768 1024 --denoise 0.45 --seeds 1 2 --prompt-file $W/bust_prompt.txt \
       --out $W/bust --prefix bust
```

- Denoise **0.4–0.45** stays close to the source; **0.55–0.6** adds new detail (drips, barnacles).
- The first crop is usually too loose (half-length, not a bust). Crop head-and-shoulders tightly:
  from just above the hat to mid-chest. A second pass from the best result with a tighter crop is
  normal and cheap.
- Light described in the prompt rarely lands on the face in img2img; say "lit warmly on the left
  side of his face" if it matters.

## 3. Pixel-art repaint

Repaint the chosen painting as pixel art, on a flat background:

```bash
python $S/comfy.py img2img --image $W/bust/bust_seed2.png --denoise 0.8 \
       --seeds 1 2 3 4 --prompt-file $W/pixel_prompt.txt --out $W/pixel --prefix pix
```

- Denoise **0.65** keeps the painting's face best; **0.8** gives crisper pixel shapes and outlines
  but pushes faces toward cartoon (big round eyes). Try both in one round: two seeds at each.
- Ask for "large chunky pixels, hard edges, flat cel shading with 3 tones per material, no
  gradients, no anti-aliasing, clean dark outlines" and "plain flat solid <colour> background,
  completely empty".
- "Lantern light on his face" becomes an orange blob by the ear at this stage. Either drop the
  light from the pixel prompt or accept removing the blob afterwards.

## 4. Background removal and palette clean

```bash
python $S/pixel_post.py key $W/pixel/pix_seed1.png $W/pixel/pix1_keyed.png
cd <project root>     # so pixelforge finds the project's pixelforge.toml
python -m pixelforge clean $W/pixel/pix1_keyed.png --canvas <canvas> -o $W/clean/pix1.png --dry-run
python -m pixelforge clean $W/pixel/pix1_keyed.png --canvas <canvas> -o $W/clean/pix1.png --no-trim
```

- **Use `pixel_post.py key`, not pixelforge's own `--key`,** on generated images. The generated
  background is never flat (gradients, a ground shadow), so a global colour key either leaves a
  fringe or — with a loose tolerance — also removes grey stubble and pale skin that resemble the
  backdrop. A tolerance of 24 punched holes in a beard; the flood-fill key stops at the outline.
- `key` prints the share of pixels removed and writes `<dst>_check.png`, the subject on bright
  green. **Open the check image every time** — the share cannot tell "background" from
  "background plus a grey cap", and a subject colour close in hue to the backdrop is removed with
  it without warning. Under ~20% removed means the model ignored the background instruction
  (white, or a colour matching the costume); regenerate rather than fight it.
- Tuning `key`: `--hue-tol` (default 0.09) is how close in hue a pixel must be to count as
  background; `--min-light`/`--max-light` (0.35–1.35 × the backdrop's lightness) let darker ground
  shadows go too. For a **grey or desaturated backdrop** near grey subject colours, tighten all
  three (`--hue-tol 0.02 --min-light 0.85 --max-light 1.15` saved a sage cap on a grey sky).
- **Read the dry-run remap table first**, but know it prints only the top rows (24 of ~47,000
  source colours is typical, all background). The real check of what the figure became is
  `pixel_post.py report` on the cleaned file.
- `--no-trim` when the source is framed the way you want (exact multiple of the canvas, subject
  already placed); without it pixelforge re-fits the subject, which is right for a loose figure on
  a big background.
- **Opaque full-frame art (backdrops, title art) must not be keyed at all.** With no `--key`,
  pixelforge auto-detects a key colour and once turned a room's dark ceiling transparent while
  reporting success. For those, downscale by exact nearest sampling and snap to the palette
  yourself, then lint.
- Mode-downscaling keeps the most common colour per block, so **1-pixel features (eyes, glints)
  can vanish.** Check the face in the report grid and place them by hand if needed.

## 5. Colour fixes by meaning

Palette membership is not correctness. After cleaning, run a report and check each colour's
*meaning* against the project's art direction:

```bash
python $S/pixel_post.py report $W/clean/pix1.png --palette <project .gpl> --grid
python $S/pixel_post.py remap $W/clean/pix1.png $W/clean/pix1_m.png --palette <.gpl> \
       --map "Sea Foam=Ink Pale" --map "Skin Deep=Madder@rows:39-"
python $S/pixel_post.py holes $W/clean/pix1_m.png $W/final/pix1.png --palette <.gpl>
```

Traps seen so far (the project's own art docs have the authoritative list):
- **Cold colours on a person or a ship** — grey hair/beards snap to sea greens; black hats and
  collars to night-sky blues. Move them to the neutral (ink/rigging) ramp of similar lightness.
- **Costume reds land in the skin ramp** (a brick-red coat became "Skin Deep") — the grid shows
  whether that colour also appears in the face; if not, a global swap is safe, otherwise limit it
  with `@rows:`.
- **Saturated reds turn orange** when the palette reserves its bright red for UI state: the
  nearest *allowed* colour is an orange. Prompt costume reds as "dark wine-red, deep and muted".
- **A single-accent colour swallowing a material** (tarred rigging → the only red).
- `holes` catches transparent pixels enclosed by the figure (a sleeve outline not meeting a beard);
  the silhouette view of `pixelforge sheet` shows them as white dots.

## 6. Sprites and animation frames

- Generate sprites with **txt2img at 1024** (512 minimum). Smaller generations are cleaner in
  blocks but crude in faces; the owner judged 512 and 1024 the only acceptable ones.
- Describe the target style by its traits ("16-bit JRPG overworld sprite, three-quarter top-down
  view, head one third of the height, bold dark outline, 3 hue-shifted tones") rather than only by
  a game's name. A pixel-art LoRA made figures finer, not chunkier, and was rejected for sprites.
- **img2img will not change a pose** — the source layout wins. For a second pose, either
  regenerate with the pose in the prompt (identity drifts) or hand-edit the cleaned sprite from its
  report grid (reliable for small changes: raise an arm, add a telescope). Hand edits are normal
  sprite-artist work; describe them to the user.
- Build the sheet with `frames` (shift = pixels lifted, for idle bobs) and preview with `anim`.
  Copy the project's existing timing (e.g. idle bob of 1 px on alternate frames).
- **Under ~32×32 for icons and UI marks, do not generate at all:** have a code-writing agent place
  every pixel in a script (shapes stated as geometry — "union of circles at (10,18)r5 and …" — not
  adjectives), then verify the output. That was right first time where generation was not.

## 7. Review sheets and in-context check

- Every round ends in a sheet the human (or critic) judges: `pixel_post.py sheet` with `--actual`
  so each candidate is visible at ×N and at true size, next to an existing asset of the same kind.
- `python -m pixelforge sheet <file> -o preview.png --scale 8 --mode review` adds the silhouette.
- **Composite onto real game art at true scale** before calling it done (a crew sprite on the
  actual deck, a marker on the actual horizon). Style differences that look minor at ×8 decide
  everything at 1:1 — the tactics-style sprites looked elegant zoomed and vanished on the deck.
- Nothing is finished until it has been seen in the running game.

## 8. Sets: states and variants of one character

For a set (aging states, injured/healthy, seasonal outfits), finish and approve **one** state
first, then derive the others from it with img2img at low denoise (0.35–0.5) and a prompt that
changes only the difference ("the same man twenty years older: whiter, thinner beard, deeper
lines, stooped"). A fresh generation per state rolls a new person. Clean every state with the
same settings and compare them side by side at true size; the set must read as one person.
Check the project's scope first — a set may be planned for later even when one state is wanted
now.

## 9. Other asset types (untested with ComfyUI; notes from earlier Codex runs)

- Brief generation at an **integer multiple of the canvas** (4× worked: 1776×1440 → 444×360) and
  state composition as percentages down the frame.
- A marker or token must occupy only part of its canvas ("subject occupies the middle third"),
  or it swallows what it points at. Check the drawn bbox after cleaning; recrop the *source*.
- Filenames must pass the project's naming lint before an asset can enter the repo.
