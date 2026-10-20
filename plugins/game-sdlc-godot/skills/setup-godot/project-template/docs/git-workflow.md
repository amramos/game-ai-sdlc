# Git workflow

Solo or small-team, AI-assisted development. No Git Flow, no long-lived branches.

## Branches

- `main` is the only long-lived branch and always opens in Godot without a parse error. It is
  protected: pull requests only, CI required.
- **Agents never commit to `main`.** Every agent change goes on a branch and lands through a pull
  request — including one-line doc fixes. `.agents/hooks/guard_bash.py` refuses commits while `main`
  is checked out and any push to `main`, for both Claude and Codex.
- **Branch at the start of an epic** from a freshly pulled `main`:
  `git pull --ff-only origin main && git checkout -b feature/<slug>`.
- **Confirm the current branch right before each commit.** A session can be moved onto `main` by a
  merge or a pull between two commands.
- An epic's features ship as **stacked pull requests**, one per feature. With *Automatically delete
  head branches* enabled in the repository settings, merging one retargets the next on its own;
  `git rebase --update-refs` moves the whole stack after a change lower down.
- Milestones are tags (`v0.1.0`, `playtest-YYYYMMDD`), never release branches. A tag triggers the
  release workflow.

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`,
  `refactor:`, `chore:`, `test:`.
- One commit, one coherent change. The message explains *why*; the diff shows *what*.
- Reference the ADR when a commit implements or changes one.

## Never commit

- `.godot/`, `*.import` (editor cache) and `build/` (exports).
- Secrets of any kind. Godot 4.1+ keeps export signing credentials in
  `.godot/export_credentials.cfg`, which is ignored; `export_presets.cfg` itself is committed.
- Binary scenes or resources (`.scn`/`.res`, ADR-0004).

## Before a change is done

1. The project parses; the relevant tests pass.
2. `git status` and `git diff` reviewed — nothing unexpected.
3. Pull request bodies end with their issue references (`Closes …` / `Ref …`).

## Conflicts in `.tscn`/`.tres`

Avoid two branches editing the same scene. When it happens, resolve by re-applying one side's change
in the editor (or by careful text edit of distinct nodes), then open the scene once and check
`git diff` before committing.
