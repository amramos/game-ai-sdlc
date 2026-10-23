# Security

These plugins give AI agents instructions, and `setup-godot` installs hooks and scripts that run on
your machine and in your CI. A problem in them could reach everyone who installs the package, so
reports are welcome.

## Reporting a vulnerability

Please **don't open a public issue**. Use GitHub's private reporting instead: the repository's
**Security** tab → **Report a vulnerability**. Include what you found, how to reproduce it, and what it
could affect.

You'll get an answer as soon as I can manage; this is a one-person project, so there is no fixed
response time and no bounty.

## What counts

- a hook in the project template (`plugins/game-sdlc-godot/skills/setup-godot/project-template/.agents/hooks/`)
  that can be bypassed or tricked into allowing what it should block, or into running something it shouldn't;
- a workflow template (CI, release, bug intake) that leaks a secret or lets untrusted input run with
  more permission than it should;
- a skill that tells an agent to do something unsafe with credentials, files or repositories.

## Supported versions

Only the latest release is supported. Turn on auto-update (see the README) to stay on it.
