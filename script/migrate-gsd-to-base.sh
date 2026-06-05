#!/usr/bin/env bash
# One-time (or idempotent) migration: move upstream GSD skills into skills/base/.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$(python3 - <<PY
import sys
sys.path.insert(0, "$SCRIPT_DIR")
from _common import resolve_skills_dir
print(resolve_skills_dir())
PY
)"

KEEP='^(gsd-ns-context|gsd-ns-ideate|gsd-ns-manage|gsd-ns-project|gsd-ns-review|gsd-ns-workflow|gsd-team|gsd-do|gsd-fast|gsd-quick|gsd-update|gsd-reapply-patches)$'

mkdir -p "$SKILLS/base"
moved=0
for d in "$SKILLS"/gsd-*; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  if [[ "$name" =~ $KEEP ]]; then
    continue
  fi
  if [ -d "$SKILLS/base/$name" ]; then
    echo "skip (already in base): $name"
    continue
  fi
  mv "$d" "$SKILLS/base/"
  moved=$((moved + 1))
done

echo "Migration complete: moved $moved skills into $SKILLS/base/"
echo "Next: skillshare sync --all --force"
