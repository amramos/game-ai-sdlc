"""Copy this package's skills into Antigravity's global skill folder (~/.gemini/config/skills by default).

Antigravity (the `agy` CLI, its desktop app and its IDE) loads skills from folders holding a SKILL.md, and
doesn't read this package's Claude Code marketplace. So this mirrors every plugins/*/skills/<name>/ folder
into <target>/<name>/, adds a generated banner after each SKILL.md's frontmatter, and drops a marker file
so later runs only ever update or remove folders this script created. It shares its logic with
install_codex.py.

    python scripts/install_antigravity.py            # install or update
    python scripts/install_antigravity.py --check    # exit 1 if anything is missing or stale
    python scripts/install_antigravity.py --remove   # remove what this script installed
    python scripts/install_antigravity.py --dry-run  # show what would change

For one project only, pass --target <project>/.agents/skills.

Standard library only.
"""

from __future__ import annotations

from pathlib import Path
import sys

import install_codex

DEFAULT_TARGET = Path.home() / ".gemini" / "config" / "skills"

if __name__ == "__main__":
    sys.exit(install_codex.main(DEFAULT_TARGET, "install_antigravity.py", __doc__))
