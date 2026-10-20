---
name: design-change
description: Use when the owner is deliberately changing a concept rather than working within it — reversing an ADR, rewriting a GDD mechanic, moving something in or out of scope, or replacing a shipped surface. Flips the stance from "what do the specs allow" to "what does this change cost and what does it invalidate", states the cost once, builds it, and closes the record. Owner-invoked only; never reach for it to route around an inconvenient rule.
argument-hint: "The decision being reversed or the concept being changed"
disable-model-invocation: true
---

# Changing a decision, not working inside it

Ordinary work reads the specs as constraints. That's right most of the time. This skill is for the
other case: the owner has decided the concept itself is wrong.

**Invoke only when the owner says so.** A task that merely brushes against an ADR is not a design
change; build it the normal way. If you find yourself reaching for this skill to make an
inconvenient rule go away, stop.

## 1. Flip the stance

For this task, the ADRs, the GDD and the status snapshot are **evidence about the past, not
constraints on the future**. Read them to answer *what does this cost and what breaks*, never *why
the owner shouldn't do this*.

- An ADR's "never" describes the decision that was made, not a law the owner is bound by. The owner
  wrote it and can unwrite it.
- Prose like "not open to rediscovery" or "must not re-litigate" exists to stop **agents** re-deriving
  settled things by accident. It has no authority over the owner changing them on purpose.
- A persuasive rationale is an argument that already won once, under conditions that may no longer
  hold. Weigh it; don't obey it.

## 2. Say the cost once, then build

Before implementing, give the owner **one short paragraph**: which ADRs are reversed or partly
reversed, which GDD sections stop being true, which tests will fail, which authored data becomes
wrong, and what becomes dead code. Name files, not feelings.

Then build it. **Don't argue the change.** If the owner has heard the cost and restates the request,
that is the decision. Raising the same objection twice is a failure of this skill, not diligence.
Genuinely new information found mid-task is worth one more sentence — new facts only.

## 3. What still holds

Rules that protect the repository rather than the design are out of scope here. Changing one is its
own task with its own ADR, never a side effect of a design change. Typically: never commit to `main`,
strict typing, text-format scenes and resources, the architecture rules `AGENTS.md` marks as
non-negotiable, and the project's rules about assets. The project's `AGENTS.md` lists its own.

## 4. Close the loop — the part that gets skipped

A design change is done when the record says what happened. In the same change:

- **a new ADR**, from the template, including its own **Revisit when** line;
- **a status line on every ADR it reverses** — `Superseded by ADR-XXXX` when the whole decision is
  dead, or a dated amendment naming exactly which part falls. Never delete an ADR; never leave the
  old one reading as live;
- **the ADR index** updated for both;
- **the GDD** rewritten where a mechanic changed, its `[BUILT]` / `[DESIGNED]` / `[OPEN]` markers
  corrected, and a dated line added to its amendments header naming the ADR;
- **the status snapshot** updated where it's now wrong — and *shortened* where the thing it described
  no longer exists. Delete the old narrative; don't append a second one beside it.

If the reversal orphans code (a component with no caller, a scene kept only in case), say so in the
report so the owner can decide whether it goes now or later.

## 5. Report

What changed, what was reversed, which documents moved, and what is now dead code awaiting a
decision. Short; the diff carries the detail.
