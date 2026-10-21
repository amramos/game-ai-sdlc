#!/usr/bin/env bash
# Runs one shared hook with the first working Python 3.9+.
#
# On Windows, `python3` and `python` can be the Microsoft Store stub: present on PATH, but it only
# prints an install hint and fails. So each candidate is actually run, not just looked up, and the
# interpreter that worked is cached in .agents/local/python (git-ignored) so later hooks start at once.
#
# Usage (from the hook registrations): bash .agents/hooks/run.sh <hook>.py
set -u
hook="${1:?usage: run.sh <hook>.py}"
shift
hooks_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cache="$hooks_dir/../local/python"

if [ -s "$cache" ]; then
  IFS= read -r cached <"$cache" || true
  if [ -n "${cached:-}" ] && command -v "$cached" >/dev/null 2>&1; then
    exec "$cached" "$hooks_dir/$hook" "$@"
  fi
fi

probe='import sys; assert sys.version_info >= (3, 9); print(sys.executable)'
for candidate in "${PYTHON:-}" python3 python "py -3"; do
  [ -n "$candidate" ] || continue
  # Unquoted on purpose: "py -3" is a command plus an argument.
  # shellcheck disable=SC2086
  found="$($candidate -c "$probe" </dev/null 2>/dev/null)" || continue
  found="${found%$'\r'}"
  [ -n "$found" ] || continue
  if command -v cygpath >/dev/null 2>&1; then
    found="$(cygpath -u "$found")"
  fi
  mkdir -p "$(dirname "$cache")" 2>/dev/null && printf '%s\n' "$found" >"$cache" 2>/dev/null
  exec "$found" "$hooks_dir/$hook" "$@"
done

echo "Hook $hook did not run: no working Python 3.9+ found (tried \$PYTHON, python3, python, py -3)." >&2
exit 1
