# The taste interview

Read this when the owner asks to set up a profile, accepts the offer (`taste-profile` §5), or calls
the skill with a profile already there. The session that runs it reads the whole profile, so it
never drafts afterwards (`taste-profile` §3, "After the interview").

## Placing an entry

Each entry is one or two lines and ends with its source and date: `stated` (the owner said it),
`inferred` (read from their answers and confirmed in playback) or `ruled` (from a ruling on real
work, added with the owner's yes).

To place an entry, ask: **would a game without it be worse by the owner's standards?**

- If yes, it's a Value.
- If no, but the owner wants it often, it's Signature or a Leaning.
- If it's something to stay away from, it's Never.

What stays out:

- **Content**: genres, settings, media, art styles, specific mechanics, anything from one of the
  owner's ideas. These belong in each game's GDD. A theme the owner keeps coming back to can be
  Signature; the setting they used it in can't.
- **Universal craft**: what any good game needs (readable text, saves that don't lose progress, a
  twist that's set up). That belongs in the skills (`game-ui`, the housekeeping baseline, the
  critics' checks), where every user gets it.
- **"I like it, but agents get it wrong."** That's a gap in a skill, not taste. Tell the owner, and
  suggest the skill it belongs in.

## The rounds

About 15–25 minutes, in four to six rounds. Each round is one message (or one multiple-choice call).
Short answers are fine. Throughout:

- **Ask for moments, not titles.** "A moment that got you, and why" says more than five names.
- **Infer before asking.** Read positions on things fans disagree about (permadeath, grinding,
  difficulty, hand-holding) from the answers.
  - Ask directly only when the signal is mixed.
  - Never add one by default.
- **Corroborate inferences.** An entry the owner didn't state needs two independent signals (say, a
  loved game and one of their own ideas) before it goes into the playback.
- **Write down the qualifiers.** "Both, but A for short games" is a conditional entry, and conditional
  entries are the ones that don't narrow.

1. **Seeds.**
   - Three to five games they love: the ones that feel like *theirs*, not the best.
   - One they find boring, ideally one others love.
   - One they admire but wouldn't make.
   - Two or three works from other media (film, series, books, comics, music) that they take
     something from.
2. **Moments.** Two or three moments, in any medium, that got them, and why. Plus one about play: a
   time an action or a mechanic in a game made them feel something.
3. **Their own ideas.** Two or three game ideas they've had, even half-formed, or a folder of notes,
   pitches or past design docs to read. This is where their taste *as a maker* shows; it can differ
   from their taste as a player, and the profile is about the maker. Take recurring themes, tones and
   structures from the ideas, never their content.
4. **Dealbreakers.** About a dozen things that can spoil a game they'd otherwise like, adapted to what
   rounds 1–3 showed. The owner marks each one:
   - **✗** spoils it;
   - **~** puts up with it;
   - **·** doesn't matter.

   Add one open line for anything missing. Pick from across genres, for example:
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
6. **Playback.** The draft profile, every entry tagged `stated` or `inferred`.
   - The owner marks each ✓ or ✗, or rewrites it.
   - Cut what they're unsure about; a short true profile beats a long plausible one.
   - Expect them to cut inferred content (a genre, an aesthetic) and keep inferred reasons.

Then write `taste.md` in the profile folder (`taste-profile` §1), starting from
[taste-profile-template.md](../taste-profile-template.md). Tell the owner where it is and that they
can edit it by hand, and show the sections once more.

## Called with a profile already there

Show it, ask about anything in `proposals.md` ([updates.md](updates.md)), then offer:

- **review it** ([updates.md](updates.md), "Review");
- **add a round**, when a new kind of game or medium is coming;
- **start over**. Starting over keeps the old file as `taste.<date>.md` next to it.
