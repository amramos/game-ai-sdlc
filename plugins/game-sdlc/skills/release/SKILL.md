---
name: release
description: Ship a build to itch.io — pick the version, write release notes from the features finished since the last tag, push a tag that makes CI export the game, smoke-test the exported build itself, and upload it to a private playtest page or the public page with butler. Steam is a later, separate step. Use when the user asks to release, publish, ship, upload a build, or make a playtest build.
argument-hint: "playtest | public, and optionally a version"
disable-model-invocation: true
---

# Release

Two kinds of release, both through CI:

- **Playtest build** — a restricted itch.io page for testers, one per milestone, so they play the real
  export rather than the editor.
- **Public release** — the game's public itch.io page.

The build and upload happen in **GitHub Actions on a tag** (the engine pack's setup creates the
workflows). This skill decides what to tag, prepares the notes, pushes the tag, and checks the result.

## 0. First release only: the itch.io setup

`setup-godot` deliberately leaves this for now, the first time it's needed. Check what already
exists (`gh variable list`, and `gh secret list` for the secret's *name* — its value is never
visible), and do only what's missing.

**The owner's part** — agents never handle store accounts or API keys, so give these as two short
steps with links:

1. create the itch.io game page (public, can stay in draft) and a second, **restricted** page for
   playtests (*Visibility → Restricted*, with testers' accounts or a password), and tell you the two
   page slugs;
2. create a butler API key (itch.io → Settings → API keys) and store it themselves by running
   `gh secret set BUTLER_API_KEY` in the project folder — it prompts for the value, so the key never
   passes through the agent.

**The agent's part**, once the owner gives the slugs: set the repository variables
`gh variable set ITCH_USER --body <user>`, `ITCH_GAME` (public slug) and `ITCH_PLAYTEST_GAME`
(restricted slug), then confirm all four names are listed.

## 1. Pick the version and write the notes

- Find the last tag (`git describe --tags --abbrev=0`) and the features finished since: merged PRs
  (`gh pr list --state merged --search "merged:>=<date>"`) and the issues they closed.
- Version: `vMAJOR.MINOR.PATCH` for public releases; `playtest-<yyyymmdd>[-n]` for playtest builds.
  Recommend a version and confirm it with the owner.
- Write player-facing notes — what's new, what changed, known issues — into `CHANGELOG.md` (newest
  first). No internal jargon, ticket ids or agent names. Update the version shown in the game if
  the project keeps one in its settings.

Commit the notes on a branch and open a PR; the tag goes on `main` after it merges.

## 2. Tag, and let CI build

Push the tag on the merged commit (`git tag <version> && git push origin <version>`). The release
workflow exports every platform preset, runs the export smoke test, and uploads with butler:

| Tag | Upload to | Channels |
|---|---|---|
| `v*` | `ITCH_USER/ITCH_GAME` | `windows`, `linux`, `mac`, `web` (whichever presets exist) |
| `playtest-*` | `ITCH_USER/ITCH_PLAYTEST_GAME` | same |

Watch the run (`gh run watch`) and report its result. A failed export or smoke test stops the upload.

## 3. Test the exported build, not the editor

The editor and an export can disagree: an export can silently drop settings or resources the editor
shows. The workflow's smoke test launches the exported build headless and checks it boots and reaches
its first screen. After a release that changed something visible, also play the exported build
(or have a blind AI playtester play it, see `playtest`) before telling testers it's ready.

## 4. After

- Playtest build: give the owner the restricted page link and a two-line "what to try" for testers.
- Public release: the store page text, screenshots and capsule images stay the owner's job; offer
  drafts (from `docs/art/` frames and real captures) if asked.
- Move the release's epic or milestone to `In Review`; the owner decides when it's done.

## Steam, later

Steam needs a Steamworks partner account, an app id and depots, set up by the owner. When the project
gets there, the same pattern applies: CI builds; agents prepare `steamcmd` build scripts; the owner
holds the account and Steam Guard and **sets builds live themselves**.
