# amramos' ten commandments for game interfaces

Distilled from thirteen talks and videos on game UI and UX, and from the Valhalla Intake UI overhaul
(an agent-built game that played well and looked like a web page). Each commandment lists its checks
and its sources, with timestamps, so any point can be traced back. The per-video notes behind them
are in [notes.md](notes.md).

**This folder doesn't ship in the plugin.** The commandments ship in the `game-ui` skill, which cites
this page for the reasons behind each one.

**The thread through all ten is intentional design.** A box, a button, a line of text, a sound, a
hidden piece of information: each is there, or not there, because someone decided it should be.

Checks are tagged **[auto]** (a test or a script can verify it), **[review]** (a reviewer or critic
judges it on captures or specs) or **[play]** (only playing shows it).

---

## 1. Intentional

Every box, button, word, sound, effect and omission is a decision with a reason you can name: the
pillar it serves, or the player decision it supports. A default is not a decision, and neither is
"other games have one".

- **Where relevant, an element that can't be strongly linked to a pillar isn't shown.** The exception
  is the functional floor every game needs: settings, pause, saving, accessibility, input help.
- **Hiding information is a decision too.** Withhold on purpose (to build dread, to make discovery
  matter), never by accident. Before removing friction someone designed, find out why it's there.
- **A rule is broken only knowingly**, for a pillar, and never at the player's expense.

Checks:
- [review] Each screen spec lists its elements, each with its pillar or the decision it supports, and
  the deliberate absences.
- [review] An element whose only reason is "the template had it" or "games usually have one" is cut.

Sources: HUD 00:54–05:21 (gauges and previews; cut repeats and window dressing), 11:13 (an enemy made
unreadable on purpose); LEC 1:30:03, 1:52:14 (helper cues as a choice); ZEL 16:14 (a slow menu meant
to encourage discovery); GD1 13:43 (rules broken knowingly); VIB 00:42 (elements placed without
purpose); owner rulings, 2026-10-24.

## 2. Built from the moment

Each screen comes from what the player is doing right now, and shows what that moment needs, at the
precision it needs.

- **Start from the activity**, not from the previous screen or a template. Style and interaction
  patterns stay consistent across screens; layout may differ.
- **When the mode changes, the previous mode's UI goes.** What matters only sometimes appears only
  then.
- **Precision follows the decision.** Exact numbers where the player compares or calculates; meters or
  words where they should feel. Exact numbers beside prose pull the eye away from the prose.

Checks:
- [review] Each screen spec names the player's activity.
- [review] Each number on screen names the comparison it serves.
- [play] No panel is left over from a previous mode.

Sources: DKD 00:43–03:11 (each screen rebuilt from the activity; no money shown inside a dungeon); LEC
1:04:43, 1:13:55; HUD 08:06 (show it only while it's relevant), 11:53–13:18 (Reigns: exact stats made
players ignore the story); MECH 00:51 (Cairn's UI appears when its inputs are touched).

## 3. Designed with the mechanic

How the player perceives a mechanic is part of the mechanic, decided when it's designed, not skinned
on at the end.

- **Every mechanic's plan says how the player sees it**, with a sketch.
- **If the interface can't show a mechanic clearly, simplify the mechanic.** UI doesn't patch a
  mechanic that doesn't work.
- **Interface polish starts mid-development**, not in the last months.

Checks:
- [review] The plan has a "how the player sees it" line for every mechanic.
- [review] A mechanic flagged as hard to show goes back to design, not to the UI.

Sources: HUD 00:00, 14:09–15:36 (Into the Breach cut what it couldn't show; Hearthstone caps the board
at what fits); LEC 28:48; RIOT 07:10 (polish can't rescue a bad design); Kotaku on The Last of Us's
interface.

## 4. One hierarchy, readable at a glance

The eye knows where to go first, second and third, and the screen reads in a blink.

- **Rank information in three reads**: the objects in play; the rules that matter now; minor context.
  Push the low ranks back on purpose: darker, washed out, lower contrast.
- **Ration emphasis.** The hottest, brightest colour goes only to what matters or can be acted on.
  Frames, borders and titles sit mid-tone. Emphasis on everything is emphasis on nothing.
- **About seven kinds of thing per screen at most**, three to five being safer (a list counts once),
  and no more than three menu levels. Both are rules of thumb, not research.
- **Centre for what matters, edges for what's glanced at**; controls near what they act on.
- **Shape first, then colour.** Different roles look different in silhouette; neighbouring colours
  differ in brightness, not only in hue; colour never carries meaning alone.
- **Critical state uses at least two channels**: a meter plus motion, sound or an in-world reaction.

Checks:
- [auto] A greyscale and a blurred capture of every screen: the key objects and their roles still read.
- [auto] Colours that mark different states differ in brightness.
- [review] Each screen names how it pushes things back and how it brings things forward.
- [review] A border or frame is never the highest-contrast thing on screen.

Sources: HUD 06:04–07:26 (Hitman's warning; three reads); DKD 01:45–06:03; LEC 17:47–37:28,
1:08:20–1:47:51; GD2 01:10–03:17 (Splatoon's inks still read without colour); VAL (pair every colour
cue with a shape).

## 5. Grouped and composed

Everything sits where it belongs, and the screen looks laid out, not filled in.

- **Group with several cues at once**: nearness, likeness and a shared panel. Panels and borders are
  fine; boxes that all weigh the same, and frames louder than their content, are not.
- **A label sits beside its value**, and a meter beside what it measures.
- **Look-alike means act-alike.** The same shape or colour means the same behaviour, the same kind of
  element moves the same way, one icon has one meaning, and empty looks empty.
- **One grid, consistent edges, one frame style.** Centred text alone is not a menu. Align with
  layout, never with spaces.

Checks:
- [review] On captures: label-to-value gaps, alignment to a grid, one frame style.
- [auto] A spelling and grammar pass over every player-facing string.

Sources: LEC 45:23–51:42, 1:01:27, 1:35:25–1:42:21; GD1 04:23–05:44, 13:00; GD2 03:29–04:56 (the
"programmer menu"); RIOT 05:55, 08:37; VIB 00:42.

## 6. Fits the hands and the full content

- **Choose the layout for the input device.** A stick selects by direction, a d-pad by grid, a mouse
  by nearness. A menu held open by a button is navigable with one other control.
- **Test with the full item count, not a sample.** Long lists get structure (columns, tabs, a stacking
  rule) and a position indicator.

Checks:
- [auto] Worst-case and average presses (or pointer travel) to reach any item, at full content.
- [play] On every supported input device.

Sources: ZEL 00:43–15:29, 19:31 (a radial menu that worked with 16 items failed with 116); MECH 08:19
(rule-based stacking); VIB 13:34.

## 7. Its own identity, minimal by default

The interface looks like this game and no other, and takes as little of the screen as the game
allows.

- **One material kit, from the game's world**, on every screen from the title to the options. Borrow
  from the world, or from graphic design outside games (album covers, transit maps, notebooks,
  posters), never from app or web UI.
- **Minimal unless the genre or a pillar asks for more.** A card or management game can be all
  interface; an action game shouldn't be.
- **Neither more nor less decoration is the fix.** Toneless and flashy both fail; plain works when
  it's chosen and unmistakably the game's.
- **The UI's colours stand apart from the world's**, and one accent colour has one job, with a variant
  per state.
- **In-world wording for flavour actions; plain verbs where a mistake costs the player.**

Checks:
- [review] Beside a reference game of the same genre: does this read as a game or as an app?
- [review] A palette audit lists each accent colour's job.
- [review] Every screen uses the material kit.

Sources: LEC 05:25, 1:15:37–1:23:04 (skeuomorphic or flat has no right answer; Mini Metro's transit
manuals); VIB 00:00–01:24, 10:04 (the web-style look of an AI-assisted game); GD1 06:37–08:52, 11:34
(Brutal Legend, Dead Space); GD2 09:27, 12:51–14:20 (a toneless remaster; an overloaded HUD); GVB
02:48–10:44, 13:56 (Painkiller, Diablo II, WoW's quest markers); SAK (clarity and style pull apart,
and each game sets the balance); FONT 10:01.

## 8. Show before telling

The world and the board carry the state. Words are a cost, spent where only words will do.

- **The board reads without opening text.** Character state shows on screen (a blur, blood, a colour
  shift), not only as numbers.
- **Put information in the world when it lives there and stays readable.** Tag each element
  diegetic, non-diegetic, spatial or meta, with the reason that fits this game's tone.
- **Never restate what the screen shows.** A label names; it doesn't explain. Highlight the words
  that matter.
- **Text-heavy play is right only when a pillar asks for it.** Papers, Please buries the player in
  paperwork because being overwhelmed by bureaucracy is the point; the same density would be wrong in
  Devil May Cry. When text belongs, give it the voice the pillars choose (an oracle's riddles, a song,
  a ledger), not a form.
- **Every screen has a word budget**, and low-stakes reading needs no button press.

Checks:
- [auto] A fit test at native resolution over every player-facing string, with no exceptions list: a
  long text is a writer's trim, never a wider box.
- [review] A cut pass on every string: delete what the screen already shows.
- [play] Blind playtesters report what they skipped reading and what they understood without reading.

Sources: VIB 07:18 (one game's board read at a glance, the other's was all text and icons); HUD 05:21,
08:37–10:44; TYP 00:34–02:55; GVB 11:19, 16:37, 17:23 (menus like an instruction manual); GD2
07:14–07:56 (Danganronpa narrows what to read), 09:27; MECH 09:35–11:18; LEC 1:29:22 (Ape Out's blood
instead of a health bar); VAL; owner ruling, 2026-10-24.

## 9. Alive, and fast the hundredth time

- **Every press answers**: a pressed state, a sound. Motion explains a change (a short slide, not a
  one-frame jump). Each kind of interaction has its own sound, and actions feel like what they
  represent.
- **Repeated feedback stays short and out of the way.** Nothing blocks input except the game's one
  signature moment, and that one briefly.

Checks:
- [auto] Harness timings: every press answered within 0.3 s (Valhalla's number, not the
  literature's); every input block listed and justified.
- [play] The hundredth repetition still feels good.

Sources: LEC 28:06; ZEL 04:29, 13:25; RIOT 07:54–09:19 (responsiveness, intention, awareness,
consistency, physical intuition); VIB 04:16 (actions with no weight); GD2 14:20 (restraint); Kotaku on
The Last of Us (a UI that feels good the hundredth time); VAL.

## 10. Type with roles

- **A display face and a body face.** The display face is for titles and the logo: expressive, read
  once. The body face is for UI and dialogue: readable and fast.
- **Two or three type treatments in the whole game**, one text effect at a time (an outline, a shadow
  or a gradient, not all three), and the same element gets the same treatment everywhere.
- **The font belongs in the game's world**, and is seen across the game rather than in one place
  only. Text margins are measured from the text's own box.
- **Legible at the smallest size it ships at.** Test confusable glyphs (1, l, I; 0, O), keep letter
  spacing tight enough to read fast, give pixel text over art an edge or a shadow, and prefer columns
  to very wide lines.
- **Text stays live**, never baked into images, so it can be localised.

Checks:
- [auto] A theme with type roles, and a guard test that no scene sets a font or size directly.
- [auto] A minimum-size and fit test.
- [review] A capture of confusable glyphs at the smallest size.

Sources: FONT 03:31–06:25 (does this font belong in this world; title versus body; Celeste's
dialogue face), 12:08–14:18 (pixel fonts at small sizes); GD1 08:52, 10:11–10:54 (five treatments on
one menu); GD2 04:13; LEC 57:22; VAL.

---

## Owner rulings, 2026-10-24

- **Intentional design is the thread** through all ten (1).
- **An element that can't be strongly linked to a pillar isn't shown**, where relevant (1).
- **Consistent style and patterns; layout from the activity** (2; was X1).
- **Minimal by default, unless the genre or the pillars require more** (7; was X2).
- **In-world verbs for flavour, plain verbs where a mistake costs** (7; was X3).
- **Text-heavy play only when a pillar calls for it** (8; was G21).

## What isn't a commandment

- **Process steps live in the skills that run them:** the final look before blind play in `playtest`
  and the critic; the fix-a-screen method in `feature-planning-core`, for layout decisions; the
  interface style sheet in `art-direction`.
- **The pattern library** (failure screens that show progress, run summaries, route recaps, stacking
  rules) stays in [notes.md](notes.md) as ideas to offer, not rules.
- **Dropped as taste rather than mechanism:** pairing a sharp frame with a soft font.

## Where the commandments are used

None of this is built yet. Each row is a change from the owner's open proposal for the skills
(numbered P1 to P25, not yet in the repository), named in its last column.

| Where | When it runs | Commandments | What happens there | Proposal |
|---|---|---|---|---|
| `game-ui` skill (new) | whenever an agent builds or changes anything the player sees, and when the owner runs `/game-sdlc:game-ui` on a screen or capture | all ten | holds the commandments and checks; returns a review with findings tagged by commandment | P4 |
| `gdd-core` and the GDD template | writing the GDD | 1, 7, 8 | suggests six to eight pillars and the owner picks three or writes their own; the interface section sets density (7), where text lives and in whose voice (8), and diegesis | P2, P3 |
| `gdd-handsoff` | the panel's rounds | 1 | pillars recorded as assumed; every mechanic must serve a pillar | P10 |
| `art-direction` | style frames and `art-direction.md` | 4, 7, 10 | frames include the most text-heavy screen and the loudest moment, judged at 1:1; the interface style sheet sets the material kit, colour jobs and type roles | P5 |
| `feature-planning-core` | the walkthrough, sketches and acceptance criteria | 1, 2, 3, 8 | every screen spec lists its elements with their pillar and the deliberate absences; "how the player sees it" for every mechanic; word budgets; acceptance checks drawn from the commandments | P7 |
| `team-lead` and its templates | build cards, the lead's playtest, the critic | the ones each package touches | the build card names them; the critic's sheet includes greyscale and blurred captures; findings cite the commandment | P13, P18 |
| `team-developer` agent | before touching anything the player sees | all ten | loads `game-ui` | P4 |
| `playtest` | blind panel reports | 4, 8 | the two reading questions | P9 |
| `setup-godot` project template | new projects | 4, 8, 9, 10 | pillars and a UI-and-text section in `AGENTS.md`; the fit and minimum-size test, the type-role guard, the capture script | P8 |
| `design-change` | when a pillar changes | 1 | every element linked to the changed pillar is re-tested | new |

Existing games use them through `/game-sdlc:game-ui` and their next `feature-planning` run, whose
first round settles the pillars if the GDD has none.

---

## Sources

| Code | Source | Kind | Weight |
|---|---|---|---|
| LEC | [Interface Essentials](https://www.youtube.com/watch?v=HdSSRTWmcw8) (Indie Game Clinic, 2 h) | lecture built on a DICE GDC talk, Gestalt theory and live critiques | the foundation; the speaker disclaims UI expertise and hedges the science |
| DKD | [Darkest Dungeon's Interface Design Principles](https://www.youtube.com/watch?v=onm8lIWBMEE) (Indie Game Clinic) | case study, an excerpt of LEC | medium-high |
| VIB | [The Hidden Cost of Vibe-Coding Games](https://www.youtube.com/watch?v=5cbonpAgR5A) (Indie Game Clinic) | one reviewer's critique of an AI-assisted game | the most direct source on the web-page look; opinion |
| TYP | [Game UI Design Explained in 4 minutes](https://www.youtube.com/watch?v=Xo5mzi3j204) (ZeDrake) | the diegetic, non-diegetic, spatial and meta taxonomy | vocabulary only |
| HUD | [The Power of Video Game HUDs](https://www.youtube.com/watch?v=4Bv45aPMGyI) (Game Maker's Toolkit) | essay with developer anecdotes | high; in-action HUDs only |
| ZEL | [Can I fix Zelda's UI using Unity?](https://www.youtube.com/watch?v=e4vsgC41bYg) (Game Maker's Toolkit) | rebuild-and-iterate experiment | high for method |
| RIOT | [So You Wanna Make Games?? Ep. 9](https://www.youtube.com/watch?v=sc3h5JXtIzw) (Riot Games) | career explainer | low |
| GVB | [The Art of Game UI: Good vs Boring](https://www.youtube.com/watch?v=dL152bMdK0k) (Angelikatosh) | appreciation essay, RPG-leaning | concrete examples of identity |
| FONT | [The Power of Font in Video Games](https://www.youtube.com/watch?v=KIvLywqLCW0) (Juniper Dev) | typography essay | good principles, no numbers |
| MECH | [10 Cool UI/UX Mechanics in Games](https://www.youtube.com/watch?v=d640TphrQYQ) (Game Design Library) | showcase | ideas |
| SAK | [Clarity vs. Style](https://www.youtube.com/watch?v=UjW_TTNtXEM) (Masahiro Sakurai) | 3-minute essay | short |
| GD1 | [Good Design, Bad Design](https://www.youtube.com/watch?v=bE_ZuNp1CTI) (Design Doc) | good and bad examples | heuristics with reasons |
| GD2 | [Good Design, Bad Design Vol. 2](https://www.youtube.com/watch?v=-_Tx5vbnH0M) (Design Doc) | good and bad examples | heuristics with reasons |
| Kotaku | [How we made The Last of Us's interface work so well](https://kotaku.com/how-we-made-the-last-of-uss-interface-work-so-well-1571841317) | developer article | high |
| VAL | the [Valhalla Intake](https://github.com/amramos/valhalla-intake) UI overhaul (epic #19, 2026-10-23/24) | our own evidence: an agent-built game, its planning ledger and the lead's retrospective | what actually went wrong |

**How this was made.** Captions were fetched with yt-dlp, uploader captions where they existed and
auto-generated otherwise; Sakurai's clip was read from its Japanese captions in a browser. Each video
was distilled by a separate reader agent into principles, pitfalls and checks with timestamps, then
merged here. Everything is paraphrased. Transcripts aren't kept in the repository. The talks lean on
what's on screen, and about sixty visual-only moments are listed in [notes.md](notes.md); no
commandment depends on any single one of them.
