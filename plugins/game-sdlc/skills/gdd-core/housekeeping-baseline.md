# The housekeeping baseline

The player-facing features almost every shipped game needs, whatever its genre. They are quality
baseline, not taste: a player who loses an hour of progress by closing the window, or can't turn the
music down, blames the game, not its design. So no skill asks whether the game "wants" them as a
design question. The project's **scope** decides how strictly they're pursued (§3), and the owner
can strike any item.

The baseline fixes **what must work**, never how it looks, sounds or is reached. Where the menu sits,
how saving is presented, which save rules the game has: those stay design decisions, made in
`feature-planning` like any other.

## 1. The items

Each item applies when the game has the thing it protects. An item whose condition the game doesn't
meet is marked *n/a* with the GDD line that shows it; that's a fact, not a strike.

| # | Item | Applies when | Done when |
|---|---|---|---|
| H1 | **Save and continue** | anything carries over between sessions (GDD §4) | progress is saved by the game's own rules, and the next launch offers to continue where those rules left the player |
| H2 | **No silent progress loss** | H1 applies, or quitting mid-session would discard anything the player made or earned, session-only progress included | quitting from the menu, closing the window and the platform's quit all either save or warn before discarding; a failed save is reported, never swallowed |
| H3 | **Main menu** | always | the first screen after launch starts or continues the game, reaches settings, and quits on platforms that have a quit |
| H4 | **Settings that persist** | always | separate volumes for music and effects (and voice, if any), window or fullscreen and scale where the platform offers a choice, text size, subtitles if any line is spoken, language if the game ships more than one; every change survives a restart |
| H5 | **Control rebinding** | the game takes keyboard or gamepad input | every action on every supported device can be rebound, a conflict is shown, defaults can be restored, and every on-screen prompt shows the current binding |
| H6 | **Pause** | always | from any play state the player can stop and reach settings and quit; where the game can't stop time (online play), the same menu opens without stopping it |
| H7 | **Skip and speed up** | the game has dialogue, text that types out, or cutscenes | a press completes the current line and the next advances it; a cutscene can be skipped, guarded against an accidental press, and a repeat viewing can always be skipped |

## 2. What is not in it

These are legitimate design choices in some genres, so they belong to the GDD and `feature-planning`,
never to this list: pop-ups that interrupt play, failing without being told why, difficulty options,
tutorials and hints, permanent loss by design (a run that ends on death, a single save slot, saving
only at set points), achievements. The baseline protects against **loss the player didn't choose and
couldn't foresee**, not against loss the design intends.

## 3. Scope decides strictness

The scope is the GDD's **Scope** line (§13 Scope boundary): game jam, prototype, small release or
commercial.

| Scope | Interactive | Hands-off |
|---|---|---|
| Game jam or prototype | offer the list, **recommended: not built**, with "add it to the backlog" as the second answer | not built, recorded as assumed; the summary offers "backlog" as a one-word swap |
| Small release | offer the list, **recommended: build** | build, recorded as assumed |
| Commercial | **build**; the owner may strike items | build, recorded as assumed; nothing is struck |

**Always at least offer the backlog.** A "not built" answer still records the list, so a jam game
that grows into a release finds it waiting.

## 4. Where the decision lives

In the GDD's §13, one line under the scope:

```
**Housekeeping baseline:** build | backlog | not built — <owner | panel — assumed>.
Struck: <H5 — reason, owner>. N/a: <H7 — no dialogue or cutscenes (§7)>.
```

The board follows the line (`issue-tracking`, "The housekeeping baseline epic"): **build** and
**backlog** both create the epic; **not built** creates nothing. Striking an item later is the
owner's call: its feature is cancelled with the reason as a comment, and the GDD line updated.
Changing the line itself after the GDD is approved goes through `design-change`.
