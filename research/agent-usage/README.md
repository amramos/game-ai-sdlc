# Agent usage: where a second agent earns its cost

An audit of every place the `game-sdlc` and `game-sdlc-godot` plugins (0.8.1) spawn an agent, judged
against what the published evidence says multi-agent setups are good for. **Nothing here changes a
skill.** Each recommendation is for the owner to rule on; implementing one is a separate pull
request.

## 1. The evidence

### Sources

| Source | Kind | What it adds |
|---|---|---|
| Anthropic, [*Building agents: When to fold subagents into your main agent loop*](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop) (22 Oct 2026) | Vendor guidance from enterprise deployments; no published scores | The article behind the recent "one agent beats many" coverage |
| Anthropic, [*Building multi-agent systems: When and how to use them*](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them) (23 Jan 2026) | Vendor guidance | The three cases where splitting pays; 3–10× tokens; the verification subagent |
| Anthropic, [*How we built our multi-agent research system*](https://www.anthropic.com/engineering/multi-agent-research-system) (13 Jun 2025) | Internal eval | +90.2% on breadth-first research at ~15× chat tokens; LLM-as-judge findings |
| Anthropic, [*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents) (19 Dec 2024) | Vendor guidance | Simplest thing first; sectioning, voting, evaluator–optimizer |
| Vals AI, [*Do Agent Teams Pay Off? A Case Study on Vibe Code Bench*](https://www.vals.ai/blogs/multi-agent-vibe-code-bench) (9 Oct 2026) | Third-party benchmark, 50 apps, one run per setup | Measured cost, speed and quality of teams vs single agents on coding |
| Cognition, [*Don't Build Multi-Agents*](https://cognition.com/blog/dont-build-multi-agents) (12 Jun 2025) | Practitioner essay | Shared context; actions carry implicit decisions |
| The Decoder, [coverage of the Anthropic article](https://the-decoder.com/anthropic-says-one-ai-agent-beats-many-subagents-now-that-models-can-handle-complexity-alone/) (25 Oct 2026) and [of the Vals study](https://the-decoder.com/ai-agent-teams-waste-massive-tokens-for-barely-measurable-quality-gains-research-finds/) (11 Oct 2026) | Secondary | Used only to find the primary pages |

**A note on "in their tests".** The Anthropic article reports qualitative findings from customer
deployments (one customer saw a single loop run about twice as fast) and gives no cost or quality
scores. The measured result that teams cost more without reliably improving quality is the Vals
study, which The Decoder reported a fortnight earlier. Both point the same way; only Vals has
numbers.

### What they agree on

**Agents pay off when:**

1. **The work splits by context, not by role.** Independent research paths, components behind a
   clean interface, black-box verification. Each piece needs little from the rest and returns a
   compact result. (Anthropic 2026 ×2, Cognition.)
2. **Isolation keeps the main context clean.** A subtask that reads a lot that the main task doesn't
   need (web pages, logs, images, a long order history) and returns a short answer. Anthropic puts
   the threshold around 1,000 mostly-irrelevant tokens. Compaction is shrinking this case.
3. **Breadth-first research runs in parallel.** The research system's +90.2% came from many
   independent searches at once, and token use alone explained ~80% of the score variance: much of
   the gain is spending more, in parallel.
4. **A verifier gets the artifact and the criteria, but not the build history.** Anthropic calls
   this the one pattern that is "consistently effective". Its known failure is the early victory:
   one test, then "pass". The remedy is concrete criteria and negative tests.
5. **Something must stay hidden**, or the tools or instructions conflict. Separate prompts help when
   one agent would have to hold incompatible modes.

**They don't pay off when:**

- **The split is by role or work type** (planner → implementer → tester → reviewer). Anthropic's
  software-role experiment spent more tokens on coordination than on work, and handoffs act like a
  game of telephone. No source claims that a same-model persona improves results by itself.
- **The work is tightly coupled.** Shared state, sequential phases of one job, most coding.
  Cognition's example: parallel parts drift into different visual worlds.
- **One loop could do it.** Teams spent months on multi-agent designs that a better-prompted single
  agent matched. Recent models (from Opus 4.5 on) hold far more in one loop than teams expected.

**Cost:** 3–10× the tokens of a single agent (Anthropic 2026), ~15× chat (Anthropic 2025).
On coding (Vals), teams cost **1.8–5.1×** as much. Only one of four configurations gained
significantly (+7.3 points). Opus 5.5 teams ran **slower** (up to 2.3× at max effort), and Sol
teams ran a little faster. Anthropic's method for deciding: build a small eval (about ten golden
examples), fold one agent at a time, run each task more than once (one fold broke a passing flow in
only one of two runs), and keep what scores better.

**What the evidence doesn't cover:** none of it studies panels of agents making *creative design*
decisions. The 2024 "voting" pattern (several independent attempts for confidence) is the nearest
support for panels. Its value depends on the votes being independent, and same-vendor models given
the same brief are correlated. The recommendations below that touch panels are an extrapolation,
and §5 says how to check them.

## 2. Inventory

Frequency is per project unless noted. Cost and latency are **order-of-magnitude estimates from
reading the skills** (what each agent is given and asked to produce), not measurements. "Spawn" means
a fresh context that reads its own inputs; one panel round of four agents is four spawns.

| # | Where | Agent | Why it is separate | How often | Rough cost / latency |
|---|---|---|---|---|---|
| 1 | `team-lead` §3–4 | Developers (`team-developer`), at most 2–3 writers at once | Real parallelism on disjoint files; context isolation of each package's reading | One per independent piece, per epic | Highest per spawn (≈100–300k tokens each); parallel, so wall-clock ≈ the slowest piece |
| 2 | `team-lead` §4.5 | Fix agent, a tier below | Context isolation; cheaper model; keeps the lead small | Per finding not fixed inline | Small (≈20–50k); minutes |
| 3 | `team-lead` §4.4, `team-lead-handsoff` §1 | `adversarial-reviewer` (Sonnet wrapper → Codex) | **Vendor diversity**; fresh-context verifier | 1–2 cycles per PR | Wrapper ≈10–30k Claude tokens plus the Codex run; minutes, in the background |
| 4 | `team-lead` §4.6 | Visual critic | Images stay out of the lead's context; another vendor when available | One scoring round + one confirmation, per epic with screens | Image-heavy (≈30–100k); one or two runs |
| 5 | `team-lead` §3, templates | Art director (another vendor or model) | Different eye; "a role" when the style guide already exists | Per epic, at most two rounds | Small–medium; one or two runs |
| 6 | `team-lead` §4.9–10 | Cheap drafters for PR bodies, the report, the story page | Cheaper model; the lead checks the output anyway | Per PR and per epic | Small; adds a hop before delivery |
| 7 | `team-lead` §4.1, `feature-planning-core` §3 | Exploring/fact-finding agent | Context isolation for wide reading | Optional, per lookup | Small–medium |
| 8 | `team-lead` §4.6, `playtest` | Blind AI playtesters (2–4) | **Information that must stay hidden** (the design) | "For a bigger change" | Real window: high (screenshot per step, minutes per turn); headless: medium |
| 9 | `gdd-handsoff` §3 | **Four-agent panel**: designer (session model), player advocate (other model), market analyst, skeptic (other vendor when available) | Skeptic: vendor diversity. Designer: same model and job as the lead. Advocate and analyst: roles | **Every round** of the design tree (typically 6–10), once per game | 4 spawns × rounds ≈ 24–40 spawns, each reading GDD sections (≈10–30k); each round waits for the slowest |
| 10 | `gdd-handsoff` §2 | Concept drafter + profile judge | Profile must not reach whoever drafts (`taste-profile` §3) | Once, when a profile exists | Two small spawns |
| 11 | `gdd-core` §3 | Research agents | **Parallel breadth research + isolation** of web pages | ~4 typical moments per GDD, in the background | Medium each; hidden behind other work |
| 12 | `gdd-core` §6 | Builder's read | **Information that must stay hidden** (a fresh reader with only the GDD) | Once, a second time if fixes were large | Medium (whole GDD); one run |
| 13 | `gdd-handsoff` §5, `prototype` §3 | Ten-second check + ≥3 blind playtesters per variation | **Blindness** | Per variation, per pass; hands-off: 2 variations × up to 3 passes | Per pass ≈ 8 spawns (2 real-window); up to ≈ 24 in hands-off |
| 14 | `feature-planning-handsoff` §2 | **Three-agent panel**: designer, player advocate, skeptic | As #9 | **Every round, every feature** | 3 spawns × rounds; the most frequent panel in a project |
| 15 | `feature-planning-core` §9 | Two-way ledger ↔ plan reviewer | Vendor diversity + fresh-context verifier | Big plans only | Medium; one run |
| 16 | `gdd-core`, `feature-planning-core` (interactive) | **Per-round taste-profile judge** (added in 0.8.0) | Profile visibility: the session may not read the whole profile | **Every round**, while the owner waits | Small tokens (cheap model) but adds a serial hop of latency to every round the owner sees |
| 17 | `art-direction` §3 (hands-off) | Critic picks the direction | Generator is a poor judge of its own work; profile judge; images isolated | Once per game, at most one adjustment round | Image-heavy; one or two runs |
| 18 | `art-direction` §3, `comfyui-art` critic.md | Unattended seed critic | As #17 | Per seed round (default ≤3 concept + 2 pixel rounds), per asset or per direction | Image-heavy, repeated: grows with directions × rounds |
| 19 | `playtest` §3 | Second reviewer of the owner's findings | Vendor diversity | Per owner playtest | Small–medium |
| 20 | `bug-intake` | Triage agent, then fix agent (CI runs) | A safety gate: the fix runs only after a maintainer's label | Per bug | One agent per stage; asynchronous |
| 21 | `game-sdlc-godot` template, `godot-plan` | `godot-developer` / `godot-debugger` / `godot-reviewer` | `godot-plan` already defaults to single dispatch; parallel only for independent files | Per task, optional | As #1–3 |

No spawns: `design-change`, `docs-cleanup`, `issue-tracking`, `release` (it may point at #8),
`game-ui` (its review procedure is what #4 runs), `taste-profile` (0.8.1 replaced its reader agent
with a single command).

## 3. Recommendations, ranked by savings

Savings are ranked by spawns saved over a project's life, weighted by how often the skill runs.
Features are planned many times per game; a GDD is written once.

### R1. Hands-off feature planning: one reviewer instead of a three-agent panel *(conditional)*

**Now:** designer, player advocate and skeptic each answer every round; unanimous → taken, split →
the lead decides.
**Proposed:** the lead writes the round with its recommendations, as it already does, and is the
designer. **One** fresh reviewer per round answers it: the skeptic's brief plus the player
advocate's questions, and the whole taste profile as the round's judge (`taste-profile` §3). It is
another vendor's model when one is available, otherwise a different, cheaper model. Agreement →
take it; disagreement → the lead decides and records the dissent, as a split does now.
**Why:** the designer panelist has the lead's model and the lead's job, so it mostly re-derives the
lead's recommendation. The player advocate is a persona of a cheaper model guessing how a newcomer
feels, and the blind playtesters measure that later. The skeptic is the only panelist with a real
independence argument (vendor), and it stays.
**Saves:** two of three spawns per round, every round, every hands-off feature.
**Lost:** the "unanimous" signal from three views. A first-player point of view that isn't
contrarian. A second same-vendor opinion on rounds where Codex is unavailable (there the reviewer
is the only outside view).

### R2. Hands-off GDD: same change to the four-agent panel *(conditional)*

**Proposed:** the lead is the designer. The market analyst's job moves to the research agents
(#11), which already return comparables, prices and positioning, and to the existing "hook is real"
gate. The player advocate's job moves to the blind playtesters of §5. One reviewer per round
remains: skeptic + profile judge, from another vendor when available.
**Saves:** three of four spawns per round: roughly 18–30 spawns per hands-off GDD.
**Lost:** a market opinion in rounds that research didn't anticipate. The fix is to dispatch
research on that question, as `gdd-core` §1 already says ("decisions, never facts"). Also the
four-view vote on identity decisions. Those are recorded as `panel — assumed` anyway, and the
owner rules on them in the summary.

### R3. Fewer playtester passes, same blindness *(trim)*

**Proposed:**
- **Fold the ten-second check into the cold playtester.** It already starts with no tutorial and
  only the screen; it writes its ten-second read before its first input.
- **Hands-off retries re-test only the revised variation**, not both.
- **The real-window playtester plays the leading variation**, and headless playtesters play the
  others, whenever the question isn't readability.

**Saves:** one spawn per variation per pass. On a hands-off GDD that misses the bar, ≈ 8–12 spawns,
the costliest of them screenshot-driven.
**Lost:** a fully independent ten-second reader (the cold playtester's first look is nearly that).
Page-level readability evidence for the trailing variation, which is usually thrown away.
**Not touched:** blindness, the cold arm, the ≥3-per-variation panel on a variation being judged.

### R4. Interactive taste-profile judge: only rounds with taste questions *(conditional)*

**Now (0.8.0):** before every interactive round, a judge agent reads the round and the whole
profile and may change recommendations.
**Proposed:** run it only on rounds holding a question that is the owner's by nature: pillars, tone,
art style, the hook, interface identity. That is the same class `panel — assumed` already names.
Skip it on mechanical, scope and technical rounds.
**Why:** the owner is present and answers every round; the profile only nudges a recommendation the
owner then accepts or changes. The cost isn't tokens, it's a serial hop before each round the owner
waits for. It is the newest spawn point and the only one on the owner's critical path.
**Saves:** most judge runs (typically one or two of six to ten rounds keep it), and the waiting
before each of the others.
**Lost:** profile nudges on non-taste rounds, where they rarely apply; the owner corrects those
directly. **Alternative:** drop it entirely in interactive mode and keep it only in hands-off
(where it merges into R1/R2's reviewer).

### R5. Art direction inside `team-lead`: only when the epic needs new kinds of asset *(conditional)*

**Now:** an art-director agent (another model) gives decisions per epic, up to two rounds.
**Proposed:** skip it when `docs/art/art-direction.md` covers every asset the epic needs. The brief's
"Art direction" section then points to the guide. Spawn it only for an asset kind the guide doesn't
cover (a new character class, a new screen type).
**Saves:** one or two runs per epic, on most epics after the first.
**Lost:** a fresh eye on routine assets. The visual critic (#4) still judges the result.

### R6. The reviewer wrapper: call Codex directly once the route is known *(merge, small)*

**Now:** each review spawns a Sonnet `adversarial-reviewer`, which finds and runs Codex and returns
the findings verbatim.
**Proposed:** the lead already checks the Codex route in recon and records the CLI and model. When it
works, the lead runs it itself as a background command writing to a file, and reads only the
findings and the verdict line. The subagent stays as the **fallback** reviewer, which really does
review.
**Saves:** one Claude subagent per review cycle (one or two per PR), plus its startup latency.
**Lost:** the wrapper's retry and route-finding logic moves into the lead's playbook. Codex's output
must be read from the file's tail, not pasted, or the lead's context pays for it.

### R7. Hands-off art direction: one critic for the direction, none for seeds within it *(trim)*

**Proposed:** within each direction, the generating agent picks seeds by the critic brief as a
strict rubric (`critic.md` option 3), and the hands-off critic (#17) judges the finished directions
side by side. Standalone `comfyui-art` unattended runs keep their critic.
**Saves:** critic runs × directions × seed rounds; image-heavy each.
**Lost:** an independent eye on seed picks. The cross-direction critic sees the result of every pick
and can send one direction back for one adjustment round.

### R8. Concept drafter only when the session has seen the profile *(conditional, small)*

**Proposed:** in `gdd-handsoff` §2, spawn the separate drafter only when this session has read more
than the Never lines (for example, it just ran the taste-profile interview). Otherwise the session
holds exactly what the drafter would get, and can draft itself. The judge stays.
**Saves:** one spawn per GDD. **Lost:** nothing, as long as the session's inputs are checked
honestly; `taste-profile` §3's leak rule still applies.

### R9. Developers: no split by work type, single builder for coupled packages *(clarify)*

**Now:** one developer per independent piece, at most two or three writers. That already matches
the guidance.
**Proposed:** make two things explicit. (a) A package is never split into "feature / tests / review"
agents. (b) Packages that are sequential or share state go to **one** developer in order (or to the
lead), not one per package with a handoff each. Keep a fresh developer per package when the lead's
context would otherwise fill with that package's reading. That isolation is real.
**Saves:** handoff briefs and re-reading on coupled epics. Vals measured teams at 1.8–5× the cost of
a single agent on coding, with no reliable quality gain.
**Lost:** wall-clock time where packages really were independent. This rule doesn't touch those.

### R10. Report and PR drafters: optional *(small)*

The lead checks every draft, so a drafter only pays when the log is long. Make it "may", not the
default.

## 4. What we keep, and why

- **Blind playtesters** (`prototype`, `playtest`, `gdd-handsoff` §5). The design must stay hidden,
  and only a separate context can be blind. This is the strongest case in the package.
- **The builder's read.** It works only because the reader has nothing but the GDD.
- **The adversarial reviewer from another vendor**, and its fallback. Vendor diversity, plus the
  verifier pattern the evidence calls consistently effective. Its brief already asks for concrete
  failure scenarios, which guards against early victory.
- **The two-way ledger ↔ plan check**, for big plans only. A fresh verifier, gated by size already.
- **Research agents.** Parallel breadth research with web pages kept out of the main context, the
  case with the clearest measured gain.
- **The visual critic and the hands-off art-direction critic.** Images are heavy, the generator
  judges its own work poorly, and the art critic is a profile judge.
- **Fix agents a tier below.** They are cheap and isolated, and they keep the lead's context small,
  which `team-lead` §5 identifies as most of a run's cost.
- **The profile judge in hands-off mode**, merged into R1/R2's single reviewer: something has to
  read the whole profile, and it can't be the drafting session.
- **`bug-intake`'s two stages.** The split is a safety gate on untrusted issue text, not a role.
- **`godot-plan`'s dispatch rules.** They already default to single and parallelise only independent
  files.

## 5. How to check a ruling before shipping it

Following Anthropic's method: for each change the owner approves, run the affected skill before and
after on two or three small fixtures of different genres, **twice each**. Compare what the skill is
for (decisions the owner later overturns, blockers the builder's read finds, playtester bar met)
and the spawns and wall-clock per run. Keep the change if quality holds. R1 and R2 deserve this
most, since the evidence doesn't cover design panels directly.
