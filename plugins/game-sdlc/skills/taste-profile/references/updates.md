# Keeping the profile current

Read this at an endpoint where the owner is present and there are candidates to ask about, or
`proposals.md` has items, or the owner asked for a review. A hands-off run with the owner away needs
only `taste-profile` §6.

## The one rule

`taste.md` changes only when the owner explicitly answers **add** (or, for a contradiction,
**update** or **drop**) to a specific item.

- Anything else is a no for the profile: "continue", "looks good", or no answer.
- Corrections, rulings and feedback are about one game until the owner says otherwise.

## Candidates

A candidate is a ruling, overturned assumption or piece of feedback that would hold for the owner's
*other* games too. "Cut it unless it earns its place" is one; "the third boss is too hard" isn't.

## Asking

- **Ask in batches, at an endpoint where the owner is present**, never mid-flow:
  - when a ledger or GDD is approved;
  - at the end of an epic (`docs-cleanup`);
  - when the owner reads a hands-off run's report.
- Ask in the conversation, never in a committed file.
- Start with what `proposals.md` holds, then this run's candidates.
- Each candidate gets three answers:
  - **add to my profile**: written as `ruled`, dated, by the agent the owner answered;
  - **this game only**: it goes in the GDD or the ledger, where it belongs;
  - **no**.
- **Contradictions.** When a ruling goes against an entry, the answers are:
  - **update the entry**;
  - **an exception for this game**, recorded in the GDD without quoting the entry;
  - **drop the entry**.
- Afterwards, remove from `proposals.md` only the items the owner answered or dismissed. Keep the
  rest for the next endpoint.

## Review

Only with the owner present:

- when they call `taste-profile` with `review`;
- at an endpoint, when an `inferred` entry hasn't been confirmed by a ruling in about six months.

Play the whole file back and ask what still holds. A hands-off run never stops for this; it uses the
profile as it is.

## A snapshot for runs without the profile folder

`docs/taste-snapshot.md` is a copy of `taste.md` for a hands-off run in a place with no access to
the profile folder (a cloud session, CI). It is the only committed file allowed to hold profile
text.

- Offer it only when the owner is starting such a run, and only when the repository is private.
  - Check it (e.g. `gh repo view --json visibility`).
  - If you can't confirm it's private, don't offer it.
- Say that it will be committed, and create it only on a clear yes.
- The command in `taste-profile` §1 uses it only when the profile folder has no `taste.md`. It
  follows the same rules as `taste.md`.
- It's read-only. Proposals from that run go in its report.
- Delete the snapshot when the owner says the run is over.
