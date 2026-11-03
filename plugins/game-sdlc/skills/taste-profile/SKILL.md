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
it stays out of everything other people can read unless the owner chooses otherwise. Whether games
stay varied depends more on which agent sees which section (§3) than on how the entries are worded.

## 1. Where it lives

One folder per person, shared by every project and every agent tool. The **profile folder** is:

1. the folder named in the `GAME_SDLC_TASTE` environment variable, if it's set (a synced folder, a
   private dotfiles repository);
2. otherwise `.game-sdlc` in the user's home folder (`$HOME`; `%USERPROFILE%` on Windows).

It holds `taste.md` (the profile), and, when they exist, `proposals.md` (additions waiting for the
owner's answer, §6) and an empty `no-taste-prompt` file (the owner asked not to be offered a profile
again, §5).

**Reading it.** The session running a skill never opens `taste.md` (§3). It runs one command that
prints only the Never lines, or `MISSING` or `INACCESSIBLE`, from the project's root, so the rest of
the file never enters its context. Judges read the file themselves.

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

Pass the printed lines on to drafters as text. If the command can't run at all, treat the profile
as inaccessible; never fall back to reading the whole file.

- **Missing** (the folder or `taste.md` doesn't exist, and there's no snapshot): carry on without a
  profile. Never an error.
- **Inaccessible** (the read is denied, as in a sandbox): say so in one line and carry on without
  it. Don't treat it as missing: don't offer the interview, and never write a new profile over one
  you couldn't read.
- **Can't write**: with the owner there (the end of an interview), show them the text and ask where
  to save it. Without the owner (a hands-off run adding a proposal), put the text in the run's report
  and carry on; ask where to save it when they're back. Never fall back to the project, and never stop
  a run over it.

Never keep the profile in a plugin's folder (updates replace it) or in a project by default. The one
exception is a **snapshot**, `docs/taste-snapshot.md`: a copy of `taste.md` for a hands-off run in
a place with no access to the profile folder (a cloud session, CI). It is the only committed file
allowed to hold profile text.

- Offer it only when the owner is starting such a run, and only when the repository is private.
  Check it (e.g. `gh repo view --json visibility`); if you can't confirm it's private, don't offer
  it. Say that it will be committed, and create it only on a clear yes.
- The commands above use it only when the profile folder has no `taste.md`. It follows the same
  rules as `taste.md`.
- It's read-only. Proposals from that run go in its report. Delete the snapshot when the owner says
  the run is over.

## 2. What it holds

Start from [taste-profile-template.md](taste-profile-template.md). Four sections:

| Section | What goes in | How strongly it binds |
|---|---|---|
| **Values** | How the owner judges *any* game, whatever its genre | Every game: a judge tests each element against them |
| **Signature** | What the owner wants to show up across their games *when the game has room for it*: recurring themes, structures, tonal contrasts | Looked for once an option exists; never forced |
| **Never** | Things to avoid by default | Breaking one takes a stated reason |
| **Leanings** | What the owner tends to make | Tiebreakers only |

Agents from any vendor and any tool read it alike: the profile is only useful if whoever does the
work can use it. What's restricted is the *kind* of agent (§3), not its vendor.

Each entry is one or two lines and ends with its source and date: `stated` (the owner said it),
`inferred` (read from their answers and confirmed in playback) or `ruled` (from a ruling on real
work, added with the owner's yes).

To place an entry, ask: **would a game without it be worse by the owner's standards?** If yes, it's a
Value. If no but the owner wants it often, Signature or a Leaning. If it's something to stay away
from, Never.

What stays out:

- **Content**: genres, settings, media, art styles, specific mechanics, anything from one of the
  owner's ideas. These belong in each game's GDD. A theme the owner keeps coming back to can be
  Signature; the setting they used it in can't.
- **Universal craft**: what any good game needs (readable text, saves that don't lose progress, a
  twist that's set up). That belongs in the skills (`game-ui`, the housekeeping baseline, the
  critics' checks), where every user gets it.
- **"I like it, but agents get it wrong."** That's a gap in a skill, not taste. Tell the owner, and
  suggest the skill it belongs in.

## 3. Who sees what

An agent puts whatever it's shown into what it makes. So the profile reaches only agents that
**judge** finished options, never agents that **make** them, and never the session that runs the
work, since that session also drafts. Each agent below starts in a fresh context with only what the
table gives it:

| Agent | Gets |
|---|---|
| **The session running the skill** (it writes rounds, options and recommendations, and briefs the drafters) | **Never** only |
| **Drafters**: whoever writes concepts, art directions or candidate answers | **Never** only, as text in their prompt, never the file's path |
| **Image and asset generators** (ComfyUI, Codex image generation, Meshy) | nothing; the frames are judged afterwards |
| **Judges**: hands-off panelists, the hands-off art critic, the interactive recommendation check | the **whole file**, read in their own context |
| **Any agent not listed** (research, builders, reviewers, playtesters, `comfyui-art`'s seed critic) | nothing |

How judges use it: they test each option against the **Values**; they look for a way in for the
**Signature** in options that exist, without asking for new ones; they use **Leanings** only to break
a tie between options that are otherwise equal. A judge that wants a different option says so in
one line, without profile reasons; a drafter writes it.

**What a judge returns** is in two parts, and only the first goes back to the session:

- the **decision**, with a reason that stands on the game alone (its pillars, its GDD, the player).
  If the only reason is the profile, it says `(profile)` and the entry's **label** (e.g. `Value 3`,
  `Never 2`), never its text or a paraphrase;
- the **explanation**: which entry, and why. This goes only in the run's report to the owner.

- **The interactive recommendation check.** Before a round that holds a question the owner's by
  nature (the pillars, tone, art style, the hook, interface identity) goes to the owner, one judge
  agent reads the round and the whole profile, and may change a recommendation, citing the label.
  The owner sees the label; they know their own file. Mechanical, scope and technical rounds skip
  it: the owner answers them directly and corrects what the profile would have nudged.
- **Hands-off panelists** (`feature-planning-handsoff`, `gdd-handsoff`) are the judges for their
  rounds; no separate judge runs.
- **Judges' models.** A Claude judge runs on the session's model or a tier below it: never above
  it, and never below a mid-size model (on a mid-size session, the same model). Another vendor's
  model may be stronger than the session's.
- **What gets recorded.** Committed or shared files (GDDs, ledgers, style guides, saved prompts,
  issues, pull requests, commits) carry **no profile text and no paraphrase of it**: only decisions
  with reasons that stand on the game alone. A decision an entry settled is recorded as
  `panel — assumed (profile)`: it is an assumption like any other, listed in the same "Assumed by the
  panel" appendix or section. The explanation goes only in the run's report to the owner, so the
  owner can overturn the entry as well as the decision.
- **After the interview**, start the next skill in a fresh session or context. The one that ran the
  interview has read the whole profile. If it goes on anyway, it never drafts itself: a separate
  drafter with only the Never lines does (`gdd-handsoff` §2). A session that has read only the Never
  lines may draft; spawning a drafter then buys nothing.
- **Breaking a Never** is allowed when the game needs it. Give the game's reason where the decision
  is recorded, with no entry text.
- **If the profile reached a drafter** (its prompt or context held more than the Never lines),
  discard those options and draft them once more in a fresh context. Say so in the report. Options
  that happen to share a trait aren't proof of a leak; the drafter's inputs are what to check.

The owner's direct instruction always beats the profile.

## 4. The interview

About 15–25 minutes, in four to six rounds. Each round is one message (or one multiple-choice call).
Short answers are fine. Throughout:

- **Ask for moments, not titles.** "A moment that got you, and why" says more than five names.
- **Infer before asking.** Read positions on things fans disagree about (permadeath, grinding,
  difficulty, hand-holding) from the answers, and ask directly only when the signal is mixed. Never
  add one by default.
- **Corroborate inferences.** An entry the owner didn't state needs two independent signals (say, a
  loved game and one of their own ideas) before it goes into the playback.
- **Write down the qualifiers.** "Both, but A for short games" is a conditional entry, and conditional
  entries are the ones that don't narrow.

The rounds:

1. **Seeds.** Three to five games they love (the ones that feel like *theirs*, not the best); one
   they find boring, ideally one others love; one they admire but wouldn't make; and two or three
   works from other media (film, series, books, comics, music) that they take something from.
2. **Moments.** Two or three moments, in any medium, that got them, and why. Plus one about play: a
   time an action or a mechanic in a game made them feel something.
3. **Their own ideas.** Two or three game ideas they've had, even half-formed, or a folder of notes,
   pitches or past design docs to read. This is where their taste *as a maker* shows; it can differ
   from their taste as a player, and the profile is about the maker. Take recurring themes, tones and
   structures from the ideas, never their content.
4. **Dealbreakers.** About a dozen things that can spoil a game they'd otherwise like, adapted to what
   rounds 1–3 showed, each marked **✗** (spoils it), **~** (puts up with it) or **·** (doesn't
   matter), plus one open line for anything missing. Pick from across genres, for example:
   - side content that's busywork;
   - grinding required to move forward;
   - lore or rules delivered as walls of text;
   - a mystery explained away into something smaller;
   - a twist that wasn't set up;
   - humour that undercuts every serious moment;
   - choices presented as mattering that don't;
   - a section that breaks the mood without a reason;
   - challenge that feels like a toll on the way to the good part;
   - systems so deep that the game is mostly menus;
   - a look with no identity.

   This round usually says more than any other: people explain their taste best when defending it.
   Listen for the word they keep using; it's often the first Value.
5. **When would you pick each** *(only if needed)*. For points still unclear, two things the owner
   already likes, asked as "when would you pick each", never "which do you prefer": they usually like
   both, and the answer is in the condition.
6. **Playback.** The draft profile, every entry tagged `stated` or `inferred`. The owner marks each ✓,
   ✗ or rewrites it. Cut what they're unsure about; a short true profile beats a long plausible one.
   Expect them to cut inferred content (a genre, an aesthetic) and keep inferred reasons.

Then write `taste.md` in the profile folder (§1), tell the owner where it is and that they can edit
it by hand, and show the sections once more.

## 5. When another skill finds no profile

`gdd`, `gdd-handsoff`, `art-direction`, `feature-planning` and `feature-planning-handsoff` look
for the profile when they start. Every offer they make, at the start or in a closing summary, goes
through this check. Offer only when the profile is **missing** (not inaccessible, §1), the profile
folder has no `no-taste-prompt` (if you can't check, don't offer), and the owner is there to answer:

- offer it once, in one line: what it gives (decisions closer to theirs, fewer corrections after) and
  what it costs (about 20 minutes, once, for every future game);
- answers: **set it up now** (run this skill, then go back), **not now** (carry on; ask again next
  time), **don't ask again** (create the empty `no-taste-prompt` in the profile folder, and never
  offer it again unless the owner calls this skill);
- never block. A hands-off skill whose owner has already left doesn't ask; its report says one line
  about it instead.

## 6. Keeping it current

`taste.md` changes only when the owner explicitly answers **add** (or, for a contradiction, **update**
or **drop**) to a specific item. Anything else, including "continue", "looks good" or no answer, is a
no for the profile. Corrections, rulings and feedback are about one game until the owner says
otherwise.

- **Notice candidates.** A ruling, overturned assumption or piece of feedback that would hold for
  the owner's *other* games too ("cut it unless it earns its place", not "the third boss is too
  hard").
- **Ask in batches, at an endpoint where the owner is present**, never mid-flow: when a ledger or GDD
  is approved, at the end of an epic (`docs-cleanup`), when the owner reads a hands-off run's report.
  Ask in the conversation, never in a committed file.
- **When the owner isn't there**, append the candidates to `proposals.md` in the profile folder (one
  line each, with the date and the project; if it can't be written, §1). The next skill that runs
  from this list with the owner present asks about them first. Remove only the items the owner
  answered or dismissed; keep the rest for the next endpoint.
- **Three answers for each:** **add to my profile** (written as `ruled`, dated, by the agent the owner
  answered), **this game only** (it goes in the GDD or the ledger, where it belongs), **no**.
- **Contradictions.** When a ruling goes against an entry: **update the entry**, **an exception for
  this game** (recorded in the GDD, without quoting the entry), or **drop the entry**.
- **Review**, only with the owner present: when they call this skill with `review`, or, at an
  endpoint, when an `inferred` entry hasn't been confirmed by a ruling in about six months. Play the
  whole file back and ask what still holds. A hands-off run never stops for this; it uses the profile
  as it is.

## 7. Called with a profile already there

Show it, ask about anything in `proposals.md`, then offer: **review it** (§6), **add a round** (when
a new kind of game or medium is coming), or **start over**. Starting over keeps the old file as
`taste.<date>.md` next to it.
