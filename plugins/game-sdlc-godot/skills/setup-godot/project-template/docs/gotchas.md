# Gotchas

Failure modes that cost real time and give a poor or misleading signal. Read this before an editor
session, a test-baseline change or an asset move. Add an entry whenever a trap costs a session;
nothing here is a design rule (ADRs own those).

The first entries are known Godot and GUT traps, carried over from an earlier project.

## Godot editor

**Saving a scene can delete nodes placed inside an instanced scene's interior.** Godot serializes an
instance's interior children only when the instance has *Editable Children*, written as
`[editable path="..."]` at the end of the `.tscn`. Nodes added there by hand or by script run fine
but vanish on the next editor save. A node is at risk when its `parent=` path descends into an
instance *and* it declares its own `type=` or `instance=`. Fix: add the `[editable path]` line; never
delete one; `git restore` a scene that already lost nodes rather than re-adding them by hand.

**Check `git diff` after any editor session.** The editor rewrites resources (reordering, adding
`uid=`), usually harmlessly; the node tree is where the damage happens.

**An exported build can differ from the editor.** Settings and resources the editor shows can be
missing from an export. Test the exported build itself before a release (the release workflow's
smoke test is the minimum).

## Tests and GUT

**GUT silently excludes a script that fails to load.** A test naming a renamed symbol vanishes and the
run stays green. A script count that drops for no visible reason is the only signal — read the
counts whenever the baseline moves.

**A new `class_name` needs `godot --headless --import` before it resolves.** Without it, unrelated
scripts fail with `Nonexistent function 'new' in base 'GDScript'`.

**A fresh clone can fail on "invalid UID".** An asset's uid lives in its git-ignored `.import` file, so
a fresh import may draw a different one than a tracked resource names. Copy the `uid=` from a working
checkout's `.import` into the local one and import again; never edit the tracked resource's `uid=`.

**`-gselect` is a substring match and takes one pattern.** `-gselect=a_test.gd` can run several
files; a comma list selects nothing useful. Run one file per invocation and read the counts.

**A test that asserts nothing is worse than none.** A guard that skips everything shows up as
"risky" forever and teaches everyone to ignore the count. Collect offenders and assert once.

**A wide tolerance swallows the bug it points at.** Assert exact equality where a value is exact.

## Assets and UIDs

**Moving assets invalidates every `uid=` that referenced them.** Strip the stale `uid=` and let Godot
regenerate it; never hand-write one.

**Godot's CSV translation importer claims every `.csv`.** Keep data tables in another format, or set
their import to "keep file".
