---
name: game-ui
description: amramos' ten commandments for game interfaces — intentional design for every screen, HUD, menu, line of text and font a player sees, with checks, a screen spec and a review procedure. Use whenever you design, build, change or review anything the player sees in a game (screens, HUD, menus, dialogue and other text, fonts, icons, transitions between scenes), when a game screen looks like a web page or an app, or has too much text, and when the user asks for a UI review of a screen, scene or capture.
argument-hint: "Optional: a screen, scene or capture to review"
---

# Game UI: the ten commandments

Agent-built game interfaces fail in a recognisable way: they look like a web page or an app (boxes of
equal weight, plain text spread out, no hierarchy), they explain what the screen already shows, and
their elements are there because a template had them. These ten commandments are the counter. The
reasons and sources behind each one are in the
[research page](https://github.com/amramos/game-ai-sdlc/blob/main/research/game-ui/README.md).

**The project wins.** The owner's rulings, the GDD (its pillars and interface section) and the
project's interface style sheet (usually in `docs/art/art-direction.md`) override any default here.
Where they're silent, these apply.

**Find the pillars first.** Commandment 1 judges elements against the game's pillars: read them from
the GDD or `AGENTS.md`. If the game has none, say so, recommend settling them (the first round of
`feature-planning` does), and meanwhile judge each element by the player decision it supports.

## The ten commandments

### 1. Intentional

Every box, button, word, sound, effect and omission is a decision with a reason you can name: the
pillar it serves, or the player decision it supports. A default is not a decision, and neither is
"other games have one".
- Where relevant, an element that can't be strongly linked to a pillar isn't shown. The exception is
  the functional floor every game needs: settings, pause, saving, accessibility, input help.
- Hiding information is a decision too: withhold on purpose, never by accident. Before removing
  friction someone designed, find out why it's there.
- Break a rule only knowingly, for a pillar, and never at the player's expense.

*Check:* every element in the screen spec has its pillar or decision, and the spec lists what is
deliberately absent.

### 2. Built from the moment

Each screen comes from what the player is doing right now, and shows what that moment needs at the
precision it needs.
- Start from the activity, not from the previous screen or a template. Keep style and interaction
  patterns consistent across screens; let layout differ.
- When the mode changes, the previous mode's UI goes. What matters only sometimes appears only then.
- Exact numbers where the player compares or calculates; meters or words where they should feel.

*Check:* the spec names the activity; each number names the comparison it serves; no panel survives
from a previous mode.

### 3. Designed with the mechanic

How the player perceives a mechanic is part of the mechanic, decided with it, not skinned on later.
- Every mechanic's plan says how the player sees it, with a sketch.
- If the interface can't show a mechanic clearly, simplify the mechanic rather than patching it with
  UI.

*Check:* a mechanic with no "how the player sees it" goes back to design.

### 4. One hierarchy, readable at a glance

- Rank everything in three reads: the objects in play, the rules that matter now, minor context.
  Push the low ranks back on purpose: darker, washed out, lower contrast.
- Ration emphasis: the brightest, hottest colour only for what matters or can be acted on; frames,
  borders and titles mid-tone. Emphasis on everything is emphasis on nothing.
- About seven kinds of thing per screen at most, three to five being safer (a list counts once); no
  more than three menu levels.
- Centre for what matters, edges for what's glanced at; controls near what they act on.
- Shape before colour: roles differ in silhouette, neighbouring colours differ in brightness, and
  colour never carries meaning alone.
- Critical state uses at least two channels: a meter plus motion, sound or an in-world reaction.

*Check:* a greyscale and a blurred capture still show the key objects and their roles; a border is
never the highest-contrast thing on screen.

### 5. Grouped and composed

- Group with several cues at once: nearness, likeness, a shared panel. Panels and borders are fine;
  boxes that all weigh the same, and frames louder than their content, are not.
- A label sits beside its value; a meter beside what it measures.
- Look-alike means act-alike: the same shape or colour means the same behaviour, one icon has one
  meaning, and empty looks empty.
- One grid, consistent edges, one frame style. Centred text alone is not a menu. Align with layout,
  never with spaces.

*Check:* on the capture: label-to-value gaps, grid alignment, one frame style; a spelling and grammar
pass over every string.

### 6. Fits the hands and the full content

- Choose the layout for the input device: a stick selects by direction, a d-pad by grid, a mouse by
  nearness.
- Test with the full item count, never a sample. Long lists get structure (columns, tabs, a stacking
  rule) and a position indicator.

*Check:* worst-case presses or pointer travel to reach any item, at full content, on every supported
device.

### 7. Its own identity, minimal by default

- One material kit from the game's world, on every screen from the title to the options. Borrow from
  the world or from graphic design outside games (album covers, maps, notebooks, posters), never from
  app or web UI.
- Minimal unless the genre or a pillar asks for more: a card or management game can be all interface;
  an action game shouldn't be.
- Neither more nor less decoration is the fix: toneless and flashy both fail; plain works when it's
  chosen and unmistakably the game's.
- UI colours stand apart from the world's; one accent colour has one job, with a variant per state.
- In-world wording for flavour actions; plain verbs where a mistake costs the player.

*Check:* beside a reference game of the same genre, does it read as a game or an app? Every accent
colour's job is listed.

### 8. Show before telling

- The board reads without opening text. Character and world state show on screen, not only as
  numbers.
- Put information in the world when it lives there and stays readable; tag each element diegetic,
  non-diegetic, spatial or meta, with the reason for this game's tone.
- Never restate what the screen shows. A label names; it doesn't explain. Highlight the words that
  matter.
- Text-heavy play is right only when a pillar asks for it: a game about drowning in bureaucracy can
  bury the player in paperwork; an action game can't. When text belongs, give it the voice the pillars
  choose (an oracle's riddles, a song, a ledger), not a form.
- Every screen has a word budget, and low-stakes reading needs no button press.

*Check:* a fit test at native resolution over every player-facing string, with no exceptions list (a
long text is a writer's trim, never a wider box); a cut pass that deletes what the screen already
shows.

### 9. Alive, and fast the hundredth time

- Every press answers with a pressed state and a sound. Motion explains a change (a short slide, not
  a one-frame jump). Actions feel like what they represent.
- Repeated feedback stays short and out of the way. Nothing blocks input except the game's one
  signature moment, and that one briefly.

*Check:* every press answered within about 0.3 s; every input block listed with its reason. Motion and
feel are judged in play or from frame sequences, never from stills.

### 10. Type with roles

- A display face for titles and the logo (expressive, read once), a body face for UI and dialogue
  (readable, fast).
- Two or three type treatments in the whole game, one text effect at a time, the same treatment for
  the same element everywhere.
- The font belongs in the game's world and is seen across the game, not in one place only.
- Legible at the smallest size it ships at: confusable glyphs tested, spacing tight enough to read
  fast, an edge or shadow on pixel text over art, columns rather than very wide lines.
- Text stays live, never baked into images, so it can be localised.

*Check:* text comes from the project's type roles (a theme), never a font or size set per scene; a
capture of confusable glyphs at the smallest size.

## Designing a screen

Before building a screen, write its spec from [screen-spec-template.md](screen-spec-template.md): the
player's activity, every element with its pillar or decision and its read, what's deliberately absent,
the word budget, the input devices and full content size, and how the screen pushes things back and
brings things forward.

- **A material layout choice gets sketches**: two or three options drawn over a real capture, side by
  side, before anyone picks (as in `feature-planning`).
- **A styled game gets a style frame first** for any new kind of screen: generated with the project's
  image tools, cleaned onto its palette, judged at 1:1. The build matches the frame.
- **Judge at the native resolution.** Zoomed captures are for reading detail, never for approval.

## Reviewing a screen

The procedure when asked to review a screen, scene or capture, and the one the lead and the critic use:

1. **Capture it at native resolution in its worst real state**: the longest text, the most items, the
   busiest moment. Make a greyscale and a blurred copy.
2. **List every element with its reason** (pillar or decision). An element without one is the first
   finding.
3. **Walk the checks** of all ten commandments.
4. **Rank the findings**: what makes the player miss or misread something first; identity and polish
   after.
5. **Separate mechanism from taste.** A taste call goes to the owner as a question, not into a fix.
6. **Report** at most ten findings, each as `[C<n>] <element>: <what's wrong> → <smallest fix>`, then
   one line on what stills can't show (motion, sound, feel), to be judged in play.

## Traps agent-built UI falls into

- A panel of system text for every piece of information, all at the same weight.
- Numbered lists, "Next" and "Skip" cards, and caption bars that restate the screen.
- Labels that explain how to use the thing they label.
- A new line of text where a visible change would do.
- A font or size chosen per scene instead of a type role.
- The previous mode's panels left on screen.
