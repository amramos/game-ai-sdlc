---
name: taste-profile
description: Build and keep the owner's taste profile — one short private file per person, used across all their game projects, that tells agents how the owner judges a game (values, signature, hard limits, weak leanings) without choosing genres or content for them. A short interview (games and other media they love, moments that got them, their own game ideas, dealbreakers, a playback they correct) writes it; later skills propose additions only with the owner's explicit yes. Use when the user asks to set up, review or update their taste profile, or accepts the offer that gdd, gdd-handsoff, art-direction or feature-planning makes when no profile exists. Other skills load it to read the profile under its visibility and privacy rules.
argument-hint: "Optional: review, or nothing to create one"
---

# Taste profile

When building is cheap, what decides whether a game is good is how intentional it is and how clear
its maker's opinions are. A hands-off panel has neither; without help it drifts to the average game.
The taste profile carries the owner's judgment between projects, so agents decide closer to how
the owner would, and the owner corrects less afterwards.

It can also do harm. A profile that names genres, settings or favourite devices pulls every game the
same way, so everything here constrains **why** and **when**, never **what**. And it's personal, so
it stays out of everything other people can read unless the owner chooses otherwise.

**If another skill sent you here to use the profile**, you need §1 (the command) and §3 (who sees
what). The interview and the update steps live in references, read only when you run them.

## 1. Reading it

**Never open `taste.md` yourself**, not even to check that it exists. Run the command below from the
project's root, before reading anything else about the profile. It prints only the Never lines, or
`MISSING` or `INACCESSIBLE`, so the rest of the file never enters your context. Only judges read
the whole file (§3), in their own context.

The one exception: a session running this skill's own interview or review
([references/interview.md](references/interview.md), [references/updates.md](references/updates.md))
reads and shows the whole file, with the owner present. Afterwards it never drafts (§3, "After the
interview").

In bash or zsh (Linux, macOS, Git Bash):

```bash
d="${GAME_SDLC_TASTE:-$HOME/.game-sdlc}"; f="$d/taste.md"
[ -e "$f" ] || [ ! -e docs/taste-snapshot.md ] || f=docs/taste-snapshot.md
if [ ! -e "$f" ]; then echo MISSING; elif [ ! -r "$f" ]; then echo INACCESSIBLE
else sed -n '/^## Never/,/^## /{/^## /!p;}' "$f"; fi
```

In PowerShell:

```powershell
$d = if ($env:GAME_SDLC_TASTE) { $env:GAME_SDLC_TASTE } else { Join-Path $HOME '.game-sdlc' }
$f = Join-Path $d 'taste.md'
if (-not (Test-Path $f) -and (Test-Path 'docs/taste-snapshot.md')) { $f = 'docs/taste-snapshot.md' }
if (-not (Test-Path $f)) { 'MISSING' } else {
  try { $t = Get-Content -Raw -LiteralPath $f -ErrorAction Stop
        if ($t -match '(?ms)^## Never[^\n]*\n(.*?)(?=^## |\z)') { $Matches[1].Trim() -replace '\r' } }
  catch { 'INACCESSIBLE' } }
```

Pass the printed lines on to drafters as text, never the file's path.

- **The command can't run at all**: treat the profile as inaccessible. Never fall back to reading the
  whole file.
- **Missing** (no `taste.md` and no snapshot): carry on without a profile. Never an error.
- **Inaccessible** (the read is denied, as in a sandbox): say so in one line and carry on without
  it.
  - Don't treat it as missing: don't offer the interview.
  - Never write a new profile over one you couldn't read.
- **Can't write** (a proposal or a new profile):
  - With the owner there, show them the text and ask where to save it.
  - Without the owner, put the text in the run's report and carry on; ask where to save it when
    they're back.
  - Never fall back to the project, and never stop a run over it.

**Where it lives.** One folder per person, shared by every project and every agent tool:

1. the folder named in the `GAME_SDLC_TASTE` environment variable, if it's set (a synced folder, a
   private dotfiles repository);
2. otherwise `.game-sdlc` in the user's home folder (`$HOME`; `%USERPROFILE%` on Windows).

It holds `taste.md` (the profile), and, when they exist, `proposals.md` (additions waiting for the
owner's answer, §6) and an empty `no-taste-prompt` file (the owner asked not to be offered a profile
again, §5).

- Never keep the profile in a plugin's folder (updates replace it) or in a project by default.
- The one exception is `docs/taste-snapshot.md`, a committed copy for a hands-off run with no access
  to the profile folder (a cloud session, CI). **When the owner is starting such a run**, read
  [references/updates.md](references/updates.md), "A snapshot", before it starts: that's where the
  offer and its rules are.

## 2. What it holds

Four sections (the file starts from [taste-profile-template.md](taste-profile-template.md)):

| Section | What goes in | How strongly it binds |
|---|---|---|
| **Values** | How the owner judges *any* game, whatever its genre | Every game: a judge tests each element against them |
| **Signature** | What the owner wants to show up across their games *when the game has room for it*: recurring themes, structures, tonal contrasts | Looked for once an option exists; never forced |
| **Never** | Things to avoid by default | Breaking one takes a stated reason |
| **Leanings** | What the owner tends to make | Tiebreakers only |

Each entry has a **label**: its section and number (`Value 2`, `Signature 1`, `Never 3`). Labels
are what other files may carry; entry text never leaves the profile.

Agents from any vendor and any tool read it alike. What's restricted is the *kind* of agent (§3),
not its vendor.

## 3. Who sees what

An agent puts whatever it's shown into what it makes. So the profile reaches only agents that
**judge** finished options, never agents that **make** them, and never the session that runs the
work, since that session also drafts. Each agent below starts in a fresh context with only what the
table gives it:

| Agent | Gets |
|---|---|
| **The session running the skill** (it writes rounds, options and recommendations, and briefs the drafters) | **Never** only, through §1's command |
| **Drafters**: whoever writes concepts, art directions or candidate answers | **Never** only, as text in their prompt, never the file's path |
| **Image and asset generators** (ComfyUI, an agent's built-in image tool, image APIs, Meshy) | nothing; the frames are judged afterwards |
| **Judges**: the hands-off round reviewer, the hands-off art critic, the interactive recommendation check | the **whole file**, read in their own context |
| **Any agent not listed** (research, builders, reviewers, playtesters, `comfyui-art`'s seed critic) | nothing |

**How judges use it.**

- They test each option against the **Values**.
- They look for a way in for the **Signature** in options that exist, without asking for new ones.
- They use **Leanings** only to break a tie between options that are otherwise equal.
- A judge that wants a different option says so in one line, without profile reasons; a drafter
  writes it.

**What a judge returns** is in two parts, split by a line that reads exactly
`=== EXPLANATION (owner only) ===`. The session never reads past that line: the judge writes its
reply to a file, and `team-lead/scripts/codex_review.py --split <reply> --out <answers>` keeps only
the decisions in `<answers>`.

1. **Above the line, the decisions.** Each has a reason that stands on the game alone (its pillars,
   its GDD, the player).
   - If the only reason is the profile, the decision ends with `(profile)` and the entry's
     **label**, never its text or a paraphrase.
   - A **Signature addition** states the change to the option in game terms (what is added, where,
     how often), then `(profile)` and the label. A bare label gives the session nothing to act on.
2. **Below the line, the explanation**: which entry, and why. It goes only in the run's report to
   the owner.

**What gets recorded.** Committed or shared files (GDDs, ledgers, style guides, saved prompts,
issues, pull requests, commits) carry **no profile text and no paraphrase of it**: only decisions
with reasons that stand on the game alone.

- A decision an entry settled is recorded as `panel — assumed (profile)`. It is an assumption like
  any other, listed in the same "Assumed by the panel" appendix or section.
- Write it as the concrete game change (what, where, how often), never as a general principle.
- The explanation goes only in the run's report to the owner, so the owner can overturn the entry as
  well as the decision.
- **If a judge's decisions carry entry text** (a quote or a paraphrase above the line), take only
  the decision and its label, write the game change in your own words, and say in the report that
  the reply slipped.

**The judges.**

- **The interactive recommendation check.** Before a round that holds a question the owner's by
  nature goes to the owner, one judge agent reads the round and the whole profile, and may change a
  recommendation, citing the label. The owner sees the label; they know their own file.
  - Owner's by nature: the pillars, tone, art style, the hook, interface identity.
  - Mechanical, scope and technical rounds skip it: the owner answers them directly and corrects
    what the profile would have nudged.
- **The hands-off round reviewer** (`feature-planning-handsoff`, `gdd-handsoff`) is the judge for
  its rounds; no separate judge runs. A Signature opening goes among its decisions, above the line,
  never only in the explanation.
- **Judges' models.** A Claude judge runs on the session's model or a tier below it.
  - Never above the session's model.
  - Never below a mid-size model; on a mid-size session, the same model.
  - On a session smaller than mid-size, with no other vendor's model, the same model; the report says
    the judge had no independence of model.
  - Another vendor's model may be stronger than the session's.

**The rest.**

- **After the interview**, start the next skill in a fresh session or context: the one that ran the
  interview has read the whole profile.
  - If it goes on anyway, it never drafts itself: a separate drafter with only the Never lines does
    (`gdd-handsoff` §2).
  - A session that has read only the Never lines may draft; spawning a drafter then buys nothing.
- **Breaking a Never** is allowed when the game needs it. Give the game's reason where the decision
  is recorded, with no entry text.
- **If the profile reached a drafter** (its prompt or context held more than the Never lines),
  discard those options and draft them once more in a fresh context. Say so in the report. Options
  that happen to share a trait aren't proof of a leak; the drafter's inputs are what to check.
- The owner's direct instruction always beats the profile.

## 4. The interview

When the owner asks to set up a profile, accepts the offer (§5), or calls this skill with a profile
already there, follow [references/interview.md](references/interview.md).

## 5. When another skill finds no profile

`gdd`, `gdd-handsoff`, `art-direction`, `feature-planning` and `feature-planning-handsoff` look
for the profile when they start. Every offer they make, at the start or in a closing summary, goes
through this check. Offer only when all three hold:

- the profile is **missing** (not inaccessible, §1);
- the profile folder has no `no-taste-prompt` (if you can't check, don't offer);
- the owner is there to answer.

Then:

- offer it once, in one line: what it gives (decisions closer to theirs, fewer corrections after) and
  what it costs (about 20 minutes, once, for every future game);
- answers: **set it up now** (run this skill, then go back), **not now** (carry on; ask again next
  time), **don't ask again** (create the empty `no-taste-prompt` in the profile folder, and never
  offer it again unless the owner calls this skill);
- never block. A hands-off skill whose owner has already left doesn't ask; its report says one line
  about it instead.

## 6. Keeping it current

After it is written, `taste.md` changes only when the owner explicitly answers **add** (or
**update** or **drop**) to a specific item. Nothing else changes it. The interview's playback and a
**start over** are the owner writing the whole file, item by item
([references/interview.md](references/interview.md)).

- **Owner away** (a hands-off run): append each ruling, overturned assumption or piece of feedback
  that would hold for the owner's *other* games too to `proposals.md` in the profile folder.
  - One line each, with the date and the project.
  - A run that read `docs/taste-snapshot.md` (no `taste.md` in the profile folder) puts them in its
    report instead, never in `proposals.md`.
  - If it can't be written, §1, "Can't write".
  - If there are none, say so in the run's report.
- **Owner present** at an endpoint (a ledger or GDD approved, an epic's end, a hands-off report
  read), or a `review`: follow [references/updates.md](references/updates.md).
