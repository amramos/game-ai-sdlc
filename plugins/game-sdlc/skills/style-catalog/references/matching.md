# Matching a game to the catalog

Mechanical on purpose: a match an agent argues itself into stretches entries to fit. Read only the
index blocks until step 3.

## Inputs, from the GDD

- **medium:** the GDD's style, or, when it's assumed or open, the medium most of its reference
  games share (counted as gdd-handsoff §2 counts them);
- **camera:** the GDD's camera, in the index's framing words;
- **tone:** the GDD's tone and art-direction words;
- **genre and loop:** the genre and the core loop's main verbs.

## 1. Hard filters

An entry is out on any one of these:

- **medium:** the game's medium is not in the entry's `medium`. References in a medium the catalog
  lacks (realistic 3D, detailed anime illustration) fail every entry: that's a correct "nothing
  fits", not a gap to bridge;
- **framing:** the game's camera is not in the entry's `framings`;
- **avoid-for:** the game's genre or loop matches an item of the entry's `avoid-for`;
- **requires:** something it needs that art-direction §2's stock-take can't provide and the owner
  hasn't offered to set up.

## 2. Soft score

For each entry that passes: **+1** for each `mood` word the game's tone shares (or a close
synonym), **+1** for each `suits` item its genre or loop matches. `mood` is the range the look can
carry with the game's own palette and lighting, so never score down a look because its example
frames are darker or brighter than the game's tone.

**Offer an entry at 2 points or more.**

## 3. Shortlist

Keep at most **3**, highest score first; on a tie, the entry with fewer `avoid-for` near misses.
Now read each one's `style.md`, and confirm the fit in one line against the GDD's references and
pillars. A reference asking for what the entry can't do ends it.

## Near misses

An entry that passes the hard filters with **1 point** is a near miss. With the owner present,
offer it as a base with one named variation from its `style.md` ("this look, warm-keyed"). Hands-off
runs never use a near miss.

## Record

Write this block wherever the result lands (the style guide or the GDD's art section):

```
Catalog match (<date>, catalog <plugin version>):
- <id>: passed, <n> points (<mood words>; <suits items>) → offered | picked | not picked
- <id>: failed <filter> (<why, in a few words>)
Outcome: catalog <id> v<version> | built from scratch (closest: <id>, failed <filter>)
```

## Tuning

The knobs are the **2-point threshold**, **which filters are hard**, and the **shortlist of 3**.
Change them here only, in a pull request that cites match records:

- an owner swapping away from a catalog pick (art-direction §7) means the match was too loose;
- an accepted near miss, or a built look that closely matches an existing entry, means it was too
  strict.
