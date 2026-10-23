# Plugins and external dependencies

Dependencies are deliberately few: every one is code an agent must understand and a version that must
track Godot. Read this before proposing one.

## Installed

- **GUT** (`addons/gut/`, {{GUT_VERSION}}) — the test framework (ADR-0003). Vendored; never edited.
  Upgrade by replacing the folder with a release that supports the Godot version in `.godot-version`.

## Tools outside the project

- **gdtoolkit** (`gdformat`, `gdlint`) — style and lint, run by the hooks and CI (`pip install "gdtoolkit==4.*"`).
- **Godot MCP** (`@coding-solo/godot-mcp`, through `npx`) — lets agents run the game and read its
  output (ADR-0002).
- **butler** — itch.io uploads, used only in CI.
- **Dependabot** (`.github/dependabot.yml`) — opens a pull request each month when a GitHub Action used
  by the workflows has a new version. Review and merge them like any other change.

## Proposing a new one

1. Say what it does that a small amount of our own code can't.
2. Check it supports this Godot version and is maintained (recent releases, issues answered).
3. Check its licence allows shipping it.
4. Record the choice in an ADR, add it here, and vendor it under `addons/` if it's a Godot plugin.
