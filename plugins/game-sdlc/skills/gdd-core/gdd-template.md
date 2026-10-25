# <Game title> — Game Design Document

**Version:** 0.1 · **Last full revision:** <date>
**Amendments:** none yet. <!-- Each later reversal is dated here with its ADR, newest last:
"<date> — **<what changed> (§<section>, ADR-XXXX)**" -->

This is the **single source of truth for design and scope**. Where it conflicts with an older ADR,
this document wins and the ADR gets a superseded note. Where it conflicts with the code, the code
wins for *what exists today*, and this document describes *what is being built*.

Markers: **[BUILT]** is shipped behavior. **[DESIGNED]** is specified but not built. **[OPEN]** is a
decision deliberately not made yet — it needs an answer from the owner, never an invented one.

---

## 1. Pitch

<Two sentences a stranger understands.>

**The fantasy:** <what the player gets to be or do>.
**The hook:** <what's new>.

**Closest comparables:** <Game> (<the one thing borrowed>), <Game> (<…>), <Game> (<…>).

### Pillars

Every feature, screen, sound and piece of content is tested against these. Changing one goes through
`design-change`.

1. **<Name>.** <The feeling, and where the player gets it.> *Test: <the question any work is tested
   against>*
2. **<Name>.** <…> *Test: <…>*
3. **<Name>.** <…> *Test: <…>*

## 2. Core loop **[DESIGNED]**

- **Moment to moment:** <what the player does every few seconds or every turn>.
- **Session:** <how a session starts, flows and ends; win and loss>.
- **Long loop:** <what draws the player into the next session>.

## 3. Mechanics **[DESIGNED]**

### 3.1 <System>
<What it is, what the player decides, how it resolves. Use glossary terms exactly.>

## 4. Progression and economy **[DESIGNED]**

<What carries across sessions and what never does.>

## 5. Content **[DESIGNED]**

| Kind | Amount for the first release | Authored or generated |
|---|---|---|

## 6. Story and tone **[DESIGNED]**

<If any: premise, how it is delivered, tone.>

## 7. Art and audio direction **[DESIGNED]**

- **Style:** <pixel art / low poly / painterly / …>, **camera and resolution:** <…>.
- **References:** <game or image> — <what it contributes>; <…>.
- **Palette mood:** <…>. **Audio mood:** <…>.

## 8. Interface **[DESIGNED]**

What reaches the player and why. How it looks is set in the art direction's interface section.

- **Density:** <minimal / rich>, and the genre or pillar reason.
- **Where words live:** <in the world's own objects and characters, or on a HUD>; what may stay
  outside the fiction (settings, pause).
- **Text:** <how much reading the game asks, which pillar wants it, and in whose voice>.
- **Never told:** <what the game withholds on purpose, and which pillar wants it withheld; how
  summaries and results treat the player's choices: consequences, nudges or verdicts>.
- **The loudest moment:** <the game's signature action, and the space kept for it>.
- **Readable at:** <target resolution; the smallest text or mark the player must read>.
- **Comparables:** <game> (<how it presents information; the one thing borrowed>), <…>.

## 9. Platform and business **[DESIGNED]**

Engine <…>, platforms <…>, input <…>, session length <…>, price model and store <…>.

## 10. Glossary

| Term | Meaning (exactly one) |
|---|---|

## 11. Scope boundary

**Out of scope for the first release:** <list>.
**Parked:** <ideas understood and deliberately deferred>.

## 12. Open questions **[OPEN]**

1. **<Question>** — options: <…>. Recommendation: <…>.

## 13. Risks

- <What could make this not fun, and how a prototype or playtest would show it.>
