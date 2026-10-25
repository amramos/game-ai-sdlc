# Notes: game UI guidelines from the videos

The detailed notes behind [the ten commandments](README.md): the first draft of 28 guidelines, three
disagreements and a pattern library, each with the sources and timestamps it came from. The owner's
review on 2026-10-24 merged them into the ten commandments; this file keeps the detail.

| Item | Became |
|---|---|
| G1, G5 | 1. Intentional |
| G2, G4 | 2. Built from the moment |
| G3 | 3. Designed with the mechanic |
| G6–G11 | 4. One hierarchy, readable at a glance |
| G12–G14 | 5. Grouped and composed |
| G15 | 6. Fits the hands and the full content |
| G16–G18 | 7. Its own identity, minimal by default |
| G19, G21 | 8. Show before telling (G21 changed: text-heavy play only when a pillar calls for it) |
| G20 | 9. Alive, and fast the hundredth time |
| G22–G24 | 10. Type with roles (G23's pairing of a sharp frame with a soft font dropped as taste) |
| G25 | a step in `playtest` and the critic |
| G26 | a step in `feature-planning-core`, for layout decisions |
| G27 | a step in `art-direction`: the interface style sheet |
| G28 | stays here, as a pattern library |
| X1, X2, X3 | ruled by the owner; see the commandments' rulings |

Everything is paraphrased; the timestamps let you check any point against the video.

## Sources

The codes are listed in [the commandments' sources](README.md#sources).

References in the descriptions: the Kotaku piece on The Last of Us's interface and the Zelda demo
page were read. Riot's article added nothing. Six others couldn't be read (expired certificate,
blocked fetch, a 404, GDC Vault under maintenance).

## What the sources change about the problem

The working theory was "agent-built UI looks like a web page". The sources sharpen it, and correct
two parts of it:

- **The failure is a default look with no composition, not flatness or borders.** VIB describes it
  exactly: flat bordered panels, gradient shading, plain text spread out, no hierarchy, every element
  placed where it fits, state carried by text and icons instead of the board. GD2 calls the same thing
  a "programmer menu". The fix isn't decoration: GD2 faults a remaster for clean, toneless type as
  much as Battleborn for flashing everything.
- **Borders and panels are legitimate.** LEC treats a container as one of the strongest grouping
  cues. What fails is boxes that all weigh the same, and frames brighter than what they frame.
- **Plain can be right when it's chosen.** FONT (Nintendo's neutral UI face) and GVB (Skyrim's iconic
  plainness) agree that plain works when it's owned and unmistakably the game's.
- **A web pattern isn't wrong in itself.** ZEL rates a grid with tabs well, because it fits the
  content size and the input device.
- **Sources barely cover text amount.** Only GVB (menus as walls of text), HUD (cut repeated
  information) and GD2 (Danganronpa narrows what to read) touch it. The word-budget guidelines lean on
  the Valhalla evidence more than on the videos.

---

## A. What the interface is for

### G1. Every element serves a player decision

Classify each element as a **gauge** (it surfaces hidden state: health, enemy intent, what's off
screen) or a **preview** (it shows what an action will do before the player commits). Cut what is
neither: repeated information, window dressing. Keep an element when it saves the player memory work.

- **Why:** the HUD exists so the player can plan on purpose instead of acting on faith; showing every
  tracked variable buries what matters.
- **Check:** review. Each element in a screen spec names the decision it supports.
- **Sources:** HUD 00:54, 02:57, 04:40, 05:21; GD1 02:08 (Mark of the Ninja makes hidden state
  visible).

### G2. Build each screen from what the player is doing right now

Start from "what does the player need to understand at this moment", not from the previous screen or
a template. When the mode changes, remove the previous mode's UI. Hide what's irrelevant now, and
bring it back when it matters.

- **Why:** inherited layouts are developer convenience; leftover panels make players wonder why
  they're there and add load. Darkest Dungeon keeps the style across screens but almost no positions,
  and hides money inside a dungeon.
- **Check:** review. Each screen spec states the player's activity and lists what is deliberately
  absent.
- **Sources:** DKD 00:43–03:11; LEC 1:04:43, 1:13:55; HUD 08:06; MECH 00:51 (Cairn hides its UI until
  a menu input is touched).

### G3. Design the UI with the mechanic, not after it

A mechanic's plan includes how it is shown. If the interface can't show a mechanic clearly, simplify
the mechanic; don't patch it with UI. Interface polish starts mid-development, not at the end.

- **Why:** Into the Breach dropped units it couldn't display; Hearthstone caps the board at what fits.
  The Last of Us's HUD was designed in its last eight months.
- **Check:** feature planning. Every new mechanic has a "how the player sees it" line and a sketch.
- **Sources:** HUD 00:00, 14:09–15:36; LEC 28:48; RIOT 07:10 (polish can't save a bad design).

### G4. Show numbers at the precision the decision needs

Exact numbers where the player compares or calculates; meters or vague warnings where they should feel
or read. Precise numbers beside prose pull attention away from the prose.

- **Why:** Reigns' testers optimised exact stats and ignored the story; with vague bars they read it.
- **Check:** review. Each number on screen names the comparison it serves.
- **Sources:** HUD 11:53–13:18.

### G5. Withhold on purpose, and find the intent before "fixing" friction

Hiding information can be design (a faction made unreadable to scare; a helper cue that's an option).
Before changing a friction-heavy design, look up why it's that way and list the routes that already
exist.

- **Why:** Echoes of Wisdom's slow menu was meant to make players stumble on creatures they'd never
  pick; a favourites ring would defeat it.
- **Check:** feature planning and `design-change`: the intent is recorded before the fix.
- **Sources:** HUD 11:13; LEC 1:30:03; ZEL 10:37, 16:14.

---

## B. Hierarchy and attention

### G6. Rank everything into three reads, and make the low ranks look low

First read: the objects in play. Second: the rules that matter now. Third: minor context. Information
moves between reads as the state changes. Push the low ranks back on purpose (darken, wash out, blur,
lower internal contrast).

- **Why:** if everything looks important, nothing is.
- **Check:** review. Each screen names its push-back device and its pull-forward device.
- **Sources:** HUD 06:04, 06:44 (Zach Gage's three reads); DKD 04:05–05:20; LEC 1:09:03–1:11:55.

### G7. Ration emphasis

The hottest, brightest colour goes only to what needs attention or can be acted on. Frames, borders
and screen titles sit mid-tone and drop back once read. No single emphasis technique on every element
(outlining everything is like typing in capitals).

- **Why:** a decorative frame that outshines the currency it holds inverts the hierarchy.
- **Check:** review on captures; a border or frame is never the highest-contrast thing on screen.
- **Sources:** LEC 1:32:10, 1:41:39–1:47:51; DKD 03:23.

### G8. Pass the squint test

Blur and desaturate a capture: the key objects and their roles still read. Perception runs shape, then
colour, then detail, so different roles get different shapes. Colours that sit next to each other
differ in brightness as well as hue.

- **Why:** colour alone fails colourblind players and fails at a glance; Splatoon's inks stay distinct
  with the colour drained.
- **Check:** automated: a greyscale and blurred capture per screen in the critic's sheet; a value
  difference between state colours.
- **Sources:** LEC 31:30, 1:08:20; DKD 03:23; GD2 01:10–02:37; VAL (pair every colour cue with a
  shape).

### G9. Critical state uses more than one channel

A meter in a corner never carries critical state alone: add motion, sound, an in-world reaction or a
central cue. An alert that mustn't be missed is more than a small static label.

- **Why:** the periphery reads as unimportant; Hitman's trespass warning went from a label to a
  flashing alert to the alert plus a sound.
- **Check:** review. Every critical state lists its channels; at least two.
- **Sources:** LEC 26:26, 30:46; HUD 06:04.

### G10. About seven kinds of things on a screen, three menu levels

At most about seven distinct kinds of thing on one screen, three to five being safer. A list counts as
one thing; identical items count once. At most three levels of menu.

- **Why:** short-term memory. Both numbers are heuristics, not research: one studio's rule of thumb
  for menus, a loose cap for screens.
- **Check:** review (grouping is a judgement).
- **Sources:** LEC 32:30, 33:12, 34:35; DKD 01:45.

### G11. Centre for what matters, edges for what's glanced at

Passive state at the edges; controls used constantly together, near where attention already is, and
close to what they act on. Reading runs left to right, top to bottom, and the bottom-left gets ignored.

- **Why:** a glance at a corner is cheap; moving the cursor there isn't.
- **Check:** review.
- **Sources:** LEC 17:47–25:44, 30:04, 36:46.

---

## C. Grouping and layout

### G12. Group with stacked cues

Put related things together and make them look alike; a container (panel, border) groups them
further. A label sits next to its value, and a meter next to what it describes. Equal-weight boxes and
frames brighter than their content are the failure, not borders themselves.

- **Why:** players assume anything placed together is related, and that the developer meant it. When
  players misread a group, often only one cue was used.
- **Check:** review; label-to-value gaps on captures.
- **Sources:** LEC 47:35–51:42, 1:36:53, 1:42:21; RIOT 05:55.

### G13. Look-alike means act-alike

The same shape or colour means the same behaviour; the same kind of element moves the same way; one
interaction pattern throughout (Darkest Dungeon: click the ability, then the target). One icon never
carries two meanings, and empty or zero states look empty.

- **Why:** look-alikes that behave differently break expectations.
- **Check:** review.
- **Sources:** LEC 45:23, 1:01:27, 1:35:25–1:39:45; RIOT 08:37.

### G14. Compose, don't just place

Elements sit on a grid with consistent edges, and one frame style is applied the same way everywhere.
Every element is placed for a reason. Centred text alone is not a menu. Align with layout, never with
spaces. Grammar-check every string.

- **Why:** VIB's "doesn't look like a video game" and GD2's "programmer menu" are both composition
  failures.
- **Check:** review on captures; a spellcheck pass over strings.
- **Sources:** GD1 13:00; GD2 03:29–04:56; VIB 00:42.

### G15. Fit the input device and the real content size

Test a layout with the full item count (a radial menu worked with 16 items and failed with 116). A
stick wants direction-based selection, a d-pad wants a grid, a mouse wants nearness. Long lists get
structure (columns, tabs, a stacking rule) and a position indicator.

- **Why:** most of ZEL's fixes were structure chosen for the controller, not restyling.
- **Check:** automated where possible: worst-case and average presses to reach any item at full
  content.
- **Sources:** ZEL 00:43–15:29; MECH 08:19 (rule-based card stacking); VIB 13:34.

---

## D. Identity: the anti-"web page" section

### G16. A default look is not a style

The interface has three jobs: information, feel and theme. Own all three. Every screen (title,
options, loading, save, inventory) uses the same material kit as the title. Borrow a visual language
from the game's world or from real graphic design outside games (album covers, transit maps,
notebooks, posters), never from app or web UI.

- **Why:** VIB's critique of an AI-assisted game is exactly this; Brutal Legend's notebook encyclopedia
  and album-cover missions are the counter-model; Mini Metro borrows transit manuals.
- **Check:** review against a reference game from the same genre: does this read as a game or an app?
- **Sources:** LEC 05:25, 1:21:38; VIB 00:00–01:24, 10:04; GD1 06:37–08:04; GVB 02:48–04:57.

### G17. Neither more nor less decoration is the fix

Toneless "clean" type fails and so does flashing everything at once. Plain works when it's chosen and
unmistakably the game's. Style may break a rule only knowingly and for the theme (Persona 5), and
never at usability's expense (Brutal Legend's album menu keeps live, localisable text and sped-up
footage).

- **Why:** clarity and style often pull apart, and there's no universal right answer: match the
  balance to the game's purpose and world, then make it kinder where you can (SAK).
- **Check:** the game's interface direction (P5) states where it sits between clarity and style.
- **Sources:** SAK; GD1 08:04, 13:43; GD2 09:27, 12:51–14:20; FONT 10:01; GVB 06:46.

### G18. Colour: separate the UI from the world, one accent per job

The UI's colours stand apart from the world's palette. Keep the world neutral and reserve colour for
what matters. One accent colour has one signalling job, with variants for its states (available,
locked, done). Never colour alone: pair it with a shape.

- **Why:** neon blue against Dead Space's rust; Diablo II's grey stone makes potions pop; WoW's yellow
  marker means one thing.
- **Check:** a palette audit: every accent's job is listed.
- **Sources:** GD1 07:20, 11:34; GD2 02:37; GVB 10:44, 13:56; VAL.

### G19. Show state in the world before in text

The board should be readable without opening text. Character state shows on screen (blood, a blur, a
colour shift), not only as a number. Put information in the world when it lives there and stays
readable. Tag each element diegetic, non-diegetic, spatial or meta, with a reason tied to the game's
tone (horror wants it in the world; competitive play wants overlays).

- **Why:** VIB's reviewer could read the better game's board at a glance, while the weaker one was all
  text and icons.
- **Check:** review; each element's tag and reason in the screen spec.
- **Sources:** VIB 07:18; HUD 08:37–10:44; TYP 00:34–02:55; GVB 11:19, 16:37; LEC 1:29:22.

### G20. The interface feels alive, and stays fast the hundredth time

Every press answers (a pressed state, a sound). Motion explains a change (a short slide instead of a
one-frame jump). Each kind of interaction has its own sound. Actions feel like what they represent.
Repeated feedback stays short and out of the way.

- **Why:** a silent interface reads as frozen, and an attack with no weight plays like a spreadsheet.
  The Last of Us aimed for a UI that still feels good the hundredth time.
- **Check:** harness timings (every response within 0.3 s; nothing blocks input longer except the one
  signature moment, as Valhalla did).
- **Sources:** LEC 28:06; ZEL 04:29, 13:25; RIOT 07:54–09:19 (responsiveness, intention, awareness,
  consistency, physical intuition); VIB 04:16; GD2 14:20; Kotaku on The Last of Us; VAL.

---

## E. Text and type

### G21. Words are a cost

Every screen has a word budget. Never restate what the screen shows. A label names; it doesn't
explain. Highlight the words that matter so the player knows what to read. Prefer a mark or an icon
where space is small, and show instead of telling (a route line, a synergy path). Low-stakes readables
appear without a button press. Text-heavy play is fine when the design narrows what to read.

- **Why:** this is the habit you still see in Valhalla. The videos support it only partly (GVB's
  menus as walls of text, HUD's cut on repeats, Danganronpa's highlighted key words), so it rests
  mostly on our own evidence.
- **Check:** automated fit test at native resolution with no exceptions list; a cut pass on every
  player-facing string.
- **Sources:** VAL; HUD 05:21; GD2 07:14–07:56, 09:27 (a wordier remaster script, no better); GVB
  17:23; MECH 09:35–11:18.

### G22. Type roles, two or three of them

A display face for titles and the logo (expressive, read once) and a body face for UI and dialogue
(readable, fast). At most two or three type treatments in the whole game; one text effect at a time
(an outline, a shadow or a gradient, not all three); the same element gets the same treatment in every
mode. The test: does this font belong in this game's world?

- **Why:** Mario Party 8's menu mixes five treatments; Yatagarasu has about seven fonts.
- **Check:** automated: a Theme with type roles and a guard test that no scene sets a font directly
  (P8); a count of treatments.
- **Sources:** FONT 03:31–04:57; GD1 10:11–10:54; GD2 04:13.

### G23. A font is integrated, not just matching

A dialogue face seen only in dialogue jumps out; one seen everywhere (Terraria) belongs. A neutral UI
face leaves the voice to the writing; a characterful one voices every line. Pair a sharp frame with a
soft face, or the reverse. Text margins are measured from the text's own box and are the same for
every speaker.

- **Why:** Celeste's dialogue font and drifting margins are FONT's main counter-example.
- **Check:** review; margin consistency on captures.
- **Sources:** FONT 02:08–03:31, 05:41–06:25, 10:01–11:27.

### G24. Legible at the smallest size it ships at

Test confusable glyphs (1, l, I; 0, O; the numerals) at the smallest shipped size, keep letter
spacing tight enough to read fast, and give pixel text over art an edge or shadow. Prefer a column
to a very wide line. Text stays live, never baked into images, so it can be localised.

- **Why:** Ultima VII's numerals and Link's Awakening's spaced italics read slowly; old CRPG
  full-width dialogue strips tire the eye.
- **Check:** automated: a minimum-size and fit test; a glyph sample capture in the critic's sheet.
- **Sources:** FONT 12:08–14:18; LEC 57:22; GD1 08:52; VAL (a minimum size for anything the player
  must read).

---

## F. Process

### G25. The final look by the blind playtest, and never judged by its author

By the time blind testers play, the UI carries its final look, not grey boxes. Developers are poor
judges of their own UI: blind playtesters and a reviewer that didn't build it judge it.

- **Why:** the author knows too much to see what players miss, and resists changes that cost work.
- **Check:** the playtest skill's blind panel and the capped critic (P18).
- **Sources:** LEC 11:18–12:45, 52:24; Kotaku on The Last of Us (wireframe, implement, test,
  iterate, then skin).

### G26. A method for fixing a screen

When a screen is wrong:
1. state the pain with a number (presses, seconds, items);
2. capture the current screen faithfully;
3. try the cheapest fix first and see what it breaks;
4. borrow structures from games that solved the same problem;
5. judge each option at full content size and on the real input device;
6. look up the original intent;
7. show the options side by side for a decision.

- **Why:** ZEL's method, and it matches feature planning's "show it, don't describe it" step.
- **Check:** used by `feature-planning-core` for layout forks and by the lead for UI findings.
- **Sources:** ZEL (whole video).

### G27. Write the interface rules down before the first screen

A short interface style sheet: what each colour means, type roles and sizes, iconography, shape
language, motion rules, screen positions, the material of each text surface, and the space kept for
the loudest moment.

- **Why:** League's client set a theme, then rules for each of these, before screens.
- **Check:** `art-direction` writes it (P5); the build card cites it.
- **Sources:** RIOT 04:29–05:13; VAL.

---

## Optional: a pattern library

Not rules; ideas that solve specific player problems, offered when a game has that problem.

### G28. Patterns worth offering

- **A failure screen shows how close the player got** (Cuphead's boss timeline) — retry loops.
- **An end-of-run summary credits results to choices** (route taken, damage by source, best and worst
  unit) — run-based games.
- **A route recap coloured by cost** (Cairn's flyby) — games with path choices.
- **Rule-based stacking for a collection that grows** (Shroom and Gloom).
- **A live synergy view** (Pathogenic) — build-crafting games.
- **UI that hides until its inputs are touched** (Cairn) — controller games with a clean core loop.

- **Sources:** MECH 02:05–12:42.

---

## Where the sources disagree

### X1. Consistent layout, or a layout per screen?

Common advice says keep layouts consistent. DKD and LEC praise Darkest Dungeon for keeping one style
but rebuilding each screen's layout from its activity. **Proposal:** consistent style and patterns
(G13), layout from the activity (G2).

### X2. Minimal or rich?

"Disappearing UI" is an immersive-AAA goal; card games, management games and Mini Metro are all
interface; GVB argues rich, themed UI for RPGs. **Proposal:** density follows the genre and is set in
the GDD's interface section (P3), never a plugin-wide default.

### X3. Verbs in the fiction?

GVB likes stock verbs written in-world ("sign the pact" for Start); clarity argues against it.
**Proposal:** in-world wording for flavour actions, plain verbs where a mistake costs the player.

---

## Visual-only moments

The points below were made on screen, so the captions lose them. No commandment depends on any single
one; they're the moments to capture if a commandment needs a picture.

- **LEC:** [17:47] StarCraft, information on top and actions at the bottom; [41:52] a letterform slide
  for closure and proximity; [49:33] Darkest Dungeon with its common regions highlighted; [53:52]
  overlapping lines for continuity; [1:06:13] Darkest Dungeon's seven groups counted; [1:08:20] the
  same screen in colour and blurred greyscale; [1:34:43] a critiqued game's menus (zero counts, score
  against target); [1:43:03], [1:46:25] a star-chart screen before and after critique.
- **DKD:** [00:15] the town and dungeon screens side by side; [01:45] a screen annotated with seven
  regions; [03:23] blurred and greyscale versions; [04:37] background trees against a high-contrast
  key object; [05:20] the map's skull and grid icons in green and red.
- **VIB:** [00:00] a tooltip attached to the wrong thing, with panels stacked; [00:42–01:24] the flat,
  gradient-bordered layout and its modal sidebar; [04:16] attacks and builds with no feedback; [07:18]
  an unclear unit icon, and another game's board read at a glance; [13:34] Folk Emerging's condensed,
  pad-friendly look.
- **TYP:** [01:21] fighting-game health bars, a minimap and overlays; [01:21–02:09] Uncharted's
  notebook and Fallout's Pip-Boy; [02:09] Splinter Cell Conviction's prompts projected in the world;
  [02:55] an imagined Dead Space overlay and an Uncharted racing line.
- **HUD:** [02:15] Slay the Spire's intent icons; [06:04] Hitman's three warning treatments; [07:26]
  SpellTower's three reads as layers; [09:19] Dead Space's gauges on the suit and gun; [14:09] Into
  the Breach's web of arrows and icons.
- **ZEL:** [05:14] the recreated HUD around the menu; [08:44] Cross Media Bar columns splitting off the
  row; [10:08] shading that calms the cross layout; [15:29] the radial menu crowded with 116 items;
  [19:31] spiral items stacked on one plane.
- **RIOT:** [03:04] Fortnite on PC and on mobile; [05:13] League's themed client; [05:55] a health bar
  beside an enemy's name; [08:37] the Ammonomicon opening; [09:19] themed login screens.
- **GVB:** [02:48–04:14] Painkiller's worn menus; [05:20–06:46] Skyrim's and Oblivion's menus and item
  icons; [09:16] Diablo II's orbs and stone panels; [11:19] Dead Space's suit; [13:56–14:39] WoW's quest
  markers by colour.
- **FONT:** [00:00] Stray's dialogue box; [02:08] Hollow Knight's line work beside its font; [05:41]
  Terraria's text beside Celeste's; [06:25] Celeste's drifting margins; [12:53] Minecraft's menu with
  and without edge pixels, and Ultima VII's numerals.
- **MECH:** [01:35] Cairn's UI appearing and disappearing; [04:34] Rogue Point's drawn routes and pins;
  [09:01] stacked and unstacked cards; [09:35] Pathogenic's energy paths; [12:42] Cairn's route recap.
- **GD1:** [02:49] Mark of the Ninja's outlines and sound rings; [08:04] Brutal Legend's album menu;
  [10:11] Mario Party 8's five type treatments; [10:54] text with two outlines, a gradient and a
  shadow; [13:00] misaligned submenu frames.
- **GD2:** [02:37] Splatoon drained of colour; [03:29] Yatagarasu's menu problems; [07:14] Danganronpa's
  kinetic type; [09:27] Final Fantasy VI's original menus beside the remaster's; [13:35] Battleborn's
  flooded HUD.
- **SAK:** read from captions while playing; no moments flagged.

Sakurai's channel has more short UI videos, including one on text size, if a later pass wants more on
legibility.
