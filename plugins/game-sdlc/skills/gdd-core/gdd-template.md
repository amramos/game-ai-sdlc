# <Game title> — Game Design Document

**Version:** 0.1 · **Last full revision:** <date>
**Amendments:** none yet. <!-- Each later reversal is dated here with its ADR, newest last:
"<date> — **<what changed> (§<section>, ADR-XXXX)**" -->

<!-- Hands-off only (gdd-handsoff §6); delete in interactive mode: -->
**Provisional** — written by agents from a short intake; the decisions marked *assumed* in the
appendix are the owner's to confirm.

This is the **single source of truth for design and scope**; the code wins for *what exists today*.
Changing a decision goes through `design-change`.

Markers: **[BUILT]** is shipped behavior. **[DESIGNED]** is specified but not built. **[OPEN]** is a
decision deliberately not made yet — it needs an answer from the owner, never an invented one.
*(tune)* marks a value that is set but provisional. Any value a rule needs that is neither stated nor
marked is a mistake in this document: report it.

<!-- In a GDD written in another language, keep these labels in English, since check_gdd.py reads
them: the heading "Appendix: Assumed by the panel", *Check:*, *Test:*, options:, Recommendation:, runner-up:,
**Provisional**, the `panel — assumed` labels, the A1, A2… ids and "§14, item <n>". A translated "When rules meet" subsection still has a
*Check:* line ("none — the order rules apply in"). -->

---

## 1. Pitch

<Two sentences a stranger understands.>

**The fantasy:** <what the player gets to be or do>.
**The hook:** <what's new>.

**Closest comparables:** <Game> (<the one thing borrowed>), <Game> (<…>), <Game> (<…>).

<One paragraph of positioning: the niche and what sets this game apart in it.>

### Pillars

Every feature, screen, sound and piece of content is tested against these.

1. **<Name>.** <The feeling, and where the player gets it.> *Test: <the question any work is tested
   against>*
2. **<Name>.** <…> *Test: <…>*
3. **<Name>.** <…> *Test: <…>*

## 2. Core loop **[DESIGNED]**

- **Moment to moment:** <what the player does every few seconds or every turn>.
- **Session:** <how a session starts, flows and ends; win and loss>.
- **Long loop:** <what draws the player into the next session>.

<Up to two Mermaid diagrams where they help: the core loop, and how the main resources move.>

## 3. Mechanics **[DESIGNED]**

### 3.1 <System>
<What it is, what the player decides, how it resolves, and one sentence of why for any rule a
builder might simplify away. Use glossary terms exactly.>

| <Value> | <Amount> |
|---|---|

*Check:* <the move or decision this mechanic gives the player that they wouldn't have without it,
and the test that would show it missed when removed>.

### 3.<N> When rules meet
<If rules can act at the same moment: the order they apply in, and how conflicts resolve — something
used up, how long a temporary effect lasts, an effect whose target is gone, a loss during a reward,
ties. Otherwise delete this section.>

## 4. Progression and economy **[DESIGNED]**

<What the player gains within a session and across sessions, where each gain comes from, what they
spend or give up for it, and how often gains arrive. What carries over between sessions and what
never does. A game with no economy says so in one line.>

## 5. Worked example **[DESIGNED]**

<One short stretch of the core loop, played concretely: what the player sees and knows, a choice and
why, how the game resolves it (every value, when the rules use numbers), and the consequence. Name
any open rule it leaves out (§14).>

## 6. Content **[DESIGNED]**

| Kind | Amount for the first release | Authored or generated |
|---|---|---|

**Examples:** <two or three of each kind, described in full: what it is and everything it does>.
**Generator:** <if content is generated: its inputs, the invariants it keeps, and what guarantees each
result works. Otherwise delete this line.>

## 7. Story and tone **[DESIGNED]**

<If any: premise, how it is delivered, tone, and the writing rules for each voice.>

## 8. Art and audio direction **[DESIGNED]**

- **Style:** <pixel art / low poly / painterly / …>, **camera and resolution:** <…>.
- **References:** <game or image> — <what it contributes>; <…>.
- **Palette mood:** <…>. **Audio mood:** <…>; **during play:** <what music and sound do as play
  changes>.

## 9. Interface **[DESIGNED]**

What reaches the player and why. How it looks is set in the art direction's interface section.

- **Density:** <minimal / rich>, and the genre or pillar reason.
- **Where words live:** <in the world's own objects and characters, or on a HUD>; what may stay
  outside the fiction (settings, pause).
- **Text:** <how much reading the game asks, which pillar wants it, and in whose voice>.
- **Never told:** <what the game withholds on purpose, and which pillar wants it withheld; how
  summaries and results treat the player's choices: consequences, nudges or verdicts>.
- **The loudest moment:** <the game's signature action, and the space kept for it>.
- **Feedback:**

  | Moment | What the player sees and hears | How big, how long |
  |---|---|---|

- **Accessibility:** <options; the second cue for anything colour carries alone>.
- **Readable at:** <target resolution; the smallest text or mark the player must read>.
- **Comparables:** <game> (<how it presents information; the one thing borrowed>), <…>.

## 10. Platform and business **[DESIGNED]**

Engine <…>, platforms <…>, input <…>, session length <…>, price model and store <…>.

## 11. Glossary

| Term | Meaning (one line, exactly one meaning) |
|---|---|

## 12. First playable **[DESIGNED]**

<The least content that lets someone judge the core loop: what it includes, what it stubs, and any
temporary rule standing in for an open one (§14, item n).>

**Go/no-go:** <the one thing this build must show, or nothing after it matters>.

## 13. Scope boundary

**Scope:** <game jam / prototype / small release / commercial>.
**Housekeeping baseline:** <build / backlog / not built> — <owner / panel — assumed>. Struck: <item
— reason, or none>. N/a: <item — the section that shows it, or none>.
**Out of scope for the first release:** <list>.
**Parked:** <ideas understood and deliberately deferred>.

## 14. Open questions **[OPEN]**

1. **<Question>** — options: <…>. Recommendation: <…>.

## 15. Risks

- <What could make this not fun, and how a prototype or playtest would show it.>
- <How long the content plan takes, for this team.>

## Appendix: Assumed by the panel

<!-- Hands-off only (gdd-handsoff §6); delete in interactive mode. Needs no marker. Only the
assumed decisions, never a plain `panel` one; one line each, numbered A1, A2…; the owner reads these
first: -->

- **A1** <decision> (§<section>) — `panel — assumed` / `panel — assumed (profile)` — runner-up: <…>
