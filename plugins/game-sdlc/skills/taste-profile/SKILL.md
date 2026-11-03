---
name: taste-profile
description: Build and keep the owner's taste profile — one short file per person, used across all their game projects, that tells agents how the owner judges a game (values, signature, hard limits, weak leanings) without choosing genres or content for them. A short interview (games and other media they love, moments that got them, their own game ideas, dealbreakers, a playback they correct) writes it; later skills propose additions only with the owner's yes. Use when the user asks to set up, review or update their taste profile, or accepts the offer that gdd, gdd-handsoff, art-direction or feature-planning makes when no profile exists. Other skills load it to read the profile under its visibility rules.
argument-hint: "Optional: review, or nothing to create one"
---

# Taste profile

When building is cheap, what decides whether a game is good is how intentional it is and how clear
its maker's opinions are. A hands-off panel has neither; without help it drifts to the average game.
The taste profile carries the owner's judgment between projects, so agents decide closer to how
the owner would, and the owner corrects less afterwards.

It can also do harm: a profile that names genres, settings or favourite devices pulls every game the
same way. So everything here constrains **why** and **when**, never **what**, and the sections are
shown to different agents (§3). Whether games stay varied depends more on who sees each section than
on how it's worded.

## 1. Where it lives

One file per person, shared by every project and every agent tool:

1. the path in the `GAME_SDLC_TASTE` environment variable, if it's set (a synced folder, a private
   dotfiles repository);
2. otherwise `~/.game-sdlc/taste.md`;
3. otherwise, in a run with no access to the owner's home folder (a cloud session, CI), the
   project's `docs/taste-snapshot.md`, if the owner chose to commit one.

Never keep it in a plugin's folder (updates replace it) or in a project by default (many game
repositories are public, and the profile is personal). Offer the snapshot only when a hands-off run
will happen where the home folder isn't available, and say that it will be committed. A snapshot is
read-only: proposals go to the real file when the owner is back.

**No profile is never an error.** Every skill that reads one works as it did before when it's
missing.

## 2. What it holds

Start from [taste-profile-template.md](taste-profile-template.md). Four sections:

| Section | What goes in | How strongly it binds |
|---|---|---|
| **Values** | How the owner judges *any* game, whatever its genre | Every game: a critic tests each element against them |
| **Signature** | What the owner wants to show up across their games *when the game has room for it*: recurring themes, structures, tonal contrasts | Looked for once an option exists; never forced |
| **Never** | Things to avoid by default | Breaking one takes a stated reason |
| **Leanings** | What the owner tends to make | Tiebreakers only |

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

Every skill that reads the profile follows this:

- **Agents that generate options** (concepts, art directions, a round's candidate answers) get
  **only Never**. Give them the Values, Signature or Leanings and they'll put them in every option.
- **Agents that judge** (pick between options, critique, recommend, answer a panel round) get the
  **whole file**. They test each option against the Values; they look for a way in for the Signature
  in the option that exists, not by asking for a new one; they use Leanings only to break a tie
  between options that are otherwise equal.
- **Name the entry** whenever one decides something: "→ Recommended: B, per the profile's *content
  earns its place*." In a hands-off record, a decision an entry settled is `panel — from profile
  (<entry>)`. It goes in the assumed list like any other assumption, so the owner can overturn the
  entry, not just the decision.
- **Breaking a Never** is allowed when the game needs it. Say which entry and why, in the same place
  the decision is recorded.
- **Check for leaks.** When most of a run's options share one Leaning or Signature item, the profile
  has reached the generators. Regenerate the options with Never only, and say so in the summary.

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

Then write the file (§1), tell the owner where it is and how to edit it by hand, and show the
sections once more.

## 5. When another skill finds no profile

`gdd`, `gdd-handsoff`, `art-direction`, `feature-planning` and `feature-planning-handsoff` check
for a profile when they start. If there's none, and the owner is there to answer:

- offer it once, in one line: what it gives (decisions closer to theirs, fewer corrections after) and
  what it costs (about 20 minutes, once, for every future game);
- answers: **set it up now** (run this skill, then go back), **not now** (carry on; ask again next
  time), **don't ask again** (write an empty `~/.game-sdlc/no-taste-prompt` file and never offer it
  again, unless the owner asks for this skill);
- never block. A hands-off skill whose owner has already left doesn't ask; its summary says one line
  about it instead.

## 6. Keeping it current

The profile changes only with the owner's yes. Corrections, rulings and feedback are about one game
until the owner says otherwise.

- **Notice candidates.** A ruling, overturned assumption or piece of feedback that would hold for
  the owner's *other* games too ("cut it unless it earns its place", not "the third boss is too
  hard").
- **Ask in batches, at an endpoint**, never mid-flow: when a ledger or GDD is approved, when the owner
  reads a hands-off run's assumptions, at the end of an epic (`docs-cleanup`). Hands-off runs list
  them in their summary or ledger under "Proposed for your taste profile".
- **Three answers for each:** **add to my profile** (`ruled`, dated), **this game only** (it goes in
  the GDD or the ledger, where it belongs), **no**.
- **Contradictions.** When a ruling goes against an entry: **update the entry**, **an exception for
  this game** (recorded in the GDD), or **drop the entry**.
- **Review** when the owner calls this skill with `review`, or when an `inferred` entry hasn't been
  confirmed by a ruling in about six months: play the whole file back and ask what still holds.

## 7. Called with a profile already there

Show it, then offer: **review it** (§6), **add a round** (when a new kind of game or medium is
coming), or **start over**. Starting over keeps the old file as `taste.<date>.md` next to it.
