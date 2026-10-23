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
