# Unattended mode: the critic loop

In unattended mode a critic stands in for the user at each decision point. The point is a second
pair of eyes with no stake in the prompt you wrote — the generator is a poor judge of its own work,
and "it passed lint" is not taste.

## Who the critic is

Prefer, in order:
1. **The user's configured second designer**, if their memory or project notes name one
   (e.g. Codex via `codex exec` in a scratchpad). Different model, different eye.
2. **A subagent** (Agent tool) with the brief below. Give it the image paths and let it read them;
   pass `model:` explicitly if the project's instructions ask for that.

3. **Neither available** (e.g. you are yourself a subagent without the Agent tool, and no
   second-designer CLI works): judge with the brief below as a strict rubric, write the ranking
   *before* your own preference, and say plainly in the final report that no independent critic
   was used.

Never let the critic see your reasoning for a candidate before it judges — send images, the
target, and the art direction; ask for its ranking first, then compare with yours. If you and the
critic disagree, say so in the round log and pick with the critic unless the critic's choice
breaks a hard rule (palette, canvas, reserved colours).

## Brief template

```
You are reviewing candidate images for a game asset. Judge them; do not edit files.

Target: <asset, canvas size, where it appears in the game, what it must read as at true size>
Art direction (verbatim excerpts): <the few lines from the project's art docs that matter>
Hard rules: <palette file, colour budget, reserved colours, canvas>
Round <N> of at most <M>. Previous choice and why: <one line, or "first round">

Candidates: <paths>  (review sheet: <path>; true-size copies are under each)

Reply with:
1. Ranking, best first, one sentence each on why.
2. For the winner: the 1–3 most important things to change next round, as concrete visual
   instructions (not "make it better").
3. Verdict: CONTINUE (worth another round) or STOP (good enough / no further progress likely).
```

## The critic's fixes are proposals

The critic picks; it does not dictate edits. Check each suggested change against the hard rules
and the project's art docs before applying it, and log it as accepted or rejected with the reason.
In testing, the critic called a correct sage cap "sea-green" and asked to remove Sailcloth, which
the project prescribes as the top step of grey hair — both rightly rejected.

Take the brief's **hard rules from the palette tool's config** (e.g. `pixelforge.toml`: reserved
colours and where they are allowed, canvases, colour budgets), not from prose docs. Prose can lag
the config: one art-direction doc still granted crew a colour the config reserves for map art,
and a critic quoting the prose then proposed it. If you find such a contradiction, follow the
config and tell the user — it is theirs to fix.

## Loop rules

- **Cap the rounds** (default: 3 concept rounds, 2 pixel rounds). Stop early on a STOP verdict or
  when two rounds in a row fail to improve the winner.
- One change per round, taken from the critic's list — several at once makes it impossible to
  tell what worked.
- Keep a round log (`$W/log.md`): prompt diff, seeds, candidates, critic ranking, your ranking,
  choice, reason.
- Unattended never means approved. Finish with the report below and leave everything outside the
  project; the user decides what enters it.

## Final report to the user

- The chosen result(s) with the review sheet and an in-context composite, sent as files.
- A short round-by-round table: what changed, what the critic picked and why, where you disagreed.
- Known defects the loop did not fix, and what a human artist would touch up.
- The exact commands to reproduce (prompt files and seeds are in `$W`).
