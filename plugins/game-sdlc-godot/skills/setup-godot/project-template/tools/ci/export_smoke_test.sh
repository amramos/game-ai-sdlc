#!/usr/bin/env bash
# Boots an exported Linux build headless for a few seconds and fails on any script or engine error.
# The editor and an export can disagree, so this runs against the export itself.
# Usage: bash tools/ci/export_smoke_test.sh [build/linux] [frames]
set -euo pipefail

dir="${1:-build/linux}"
frames="${2:-300}"
bin="$(find "$dir" -maxdepth 1 -name '*.x86_64' 2>/dev/null | head -n 1)"
if [ -z "$bin" ]; then
  echo "::warning::No Linux export in $dir; smoke test skipped. Add a Linux preset to run it."
  exit 0
fi

chmod +x "$bin"
log="$(mktemp)"
if ! "$bin" --headless --quit-after "$frames" >"$log" 2>&1; then
  cat "$log"
  echo "The exported build exited with an error."
  exit 1
fi
cat "$log"
if grep -E "SCRIPT ERROR|^ERROR:|Parse Error" "$log" >/dev/null; then
  echo "The exported build logged errors."
  exit 1
fi
echo "The exported build booted cleanly."
