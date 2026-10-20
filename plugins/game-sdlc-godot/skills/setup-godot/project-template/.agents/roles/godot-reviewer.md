# Godot reviewer workflow

Read root `AGENTS.md`, `docs/current-status.md`, `docs/architecture.md`, and relevant ADRs. Review the requested diff or branch without modifying it.

Check typed GDScript and style; composition and coupling; autoload/EventBus rules; resources versus hardcoded data; text scene/resource format and UIDs; file/scene responsibility; folder placement; the input rule in `AGENTS.md` for anything interactive; tests; and required ADR/architecture/GDD/status updates.

For each finding, report file and line, the violated rule, severity (`blocking` or `suggestion`), and the concrete failing scenario. End with `approved` or `pending blocking fixes`. Do not implement fixes or use shell commands that mutate the repository.
