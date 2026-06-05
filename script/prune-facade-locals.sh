#!/usr/bin/env bash
# Remove stale local skill copies on copy-mode targets (cursor) after facade include sync.
set -euo pipefail

TARGET="${1:-$HOME/.cursor/skills}"
FACADE_GSD='^(gsd-ns-context|gsd-ns-ideate|gsd-ns-manage|gsd-ns-project|gsd-ns-review|gsd-ns-workflow|gsd-team|gsd-do|gsd-fast|gsd-quick|gsd-update|gsd-reapply-patches)$'

removed=0
for d in "$TARGET"/gsd-*; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  if [[ "$name" =~ $FACADE_GSD ]]; then
    continue
  fi
  rm -rf "$d"
  removed=$((removed + 1))
  echo "removed: $name"
done

echo "Pruned $removed non-facade gsd skill(s) from $TARGET"
