# Working on this repository

This repository is the SDLC itself: skills, templates, hooks and scripts that run in many different
game projects. [CONTRIBUTING.md](CONTRIBUTING.md) has the pull request rules, the checks and the
versioning; follow it.

## Keep other projects out of the SDLC

The owner often brings an example from a game project's session to show what needs to change. That
example is evidence for the change, not part of it.

- Fix the mechanism the example exposed, stated so it holds for any game. Ask yourself whether the
  rule would still read right in a game of another genre, medium and tone.
- Never carry the example's specifics into skills, templates, references, tests, the README or the
  changelog: its game's name, characters, places, mechanics, art, wording, file paths or the story
  of what went wrong there. Commit messages and pull request descriptions describe the general
  problem too ("a hands-off run stopped at a setup question"), not that project.
- When a skill needs an example, invent a neutral one, and vary the genre between examples so no
  single kind of game becomes the default.
- Before finishing, search your diff for the names and terms from the owner's example. Anything
  left is a leak: make it generic or remove it.
