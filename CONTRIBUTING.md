# Contributing

Thanks for wanting to help. Issues and pull requests are welcome: bug reports from real runs are the
most useful thing you can send.

## Reporting a problem

Open an issue with what you ran (which skill, which mode), what happened, and what you expected. A
transcript excerpt or a screenshot helps a lot. For anything security-related, see
[SECURITY.md](SECURITY.md) instead.

## Pull requests

- Keep each pull request to one change, and say why in its description.
- Write skills in plain, direct English. Constrain mechanisms, never creative taste.
- Run the checks before opening it. CI runs the same three:

  ```bash
  python scripts/check_package.py
  python -m unittest discover -s scripts/tests
  python scripts/test_template.py
  ```

- Don't bump versions or edit `CHANGELOG.md`. That happens when a release is cut.

`main` is protected: every change goes through a pull request, CI must pass, and the maintainer
reviews and merges.

## Versions

Both plugins share one version, `MAJOR.MINOR.PATCH`. A release bumps it, because auto-update only
delivers a change that comes with a new version. How to cut one is in the README.

- **Patch** (0.7.0 → 0.7.1): existing behavior now does what it already promised. A skill misread,
  a run that stopped when it shouldn't, a wrong default, a check that refused what it should allow.
  Nothing new to learn, and nothing an existing project has to change by hand.
- **Minor** (0.6 → 0.7): something new, or a change to what a skill produces or asks. A new skill,
  new steps or sections, a new template file. Also any change an existing project has to adopt by
  hand, since project files don't auto-update.
- **Major** (0 → 1): 1.0 marks the skills' contracts as stable: skill names, the markers the hooks
  read, and the files a project is set up with. After that, a major bump means one of those breaks.
  Until then, a breaking change is a minor bump, called out in the changelog.

When a change sits between two, take the higher one.
