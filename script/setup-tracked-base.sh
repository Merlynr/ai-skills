#!/usr/bin/env bash
# Register gsd-build/get-shit-done as skillshare tracked repo under skills/base/.
# Vendored gsd-*/SKILL.md remain in skills/base/ and refresh via upgrade-gsd-stack.sh B2 path.
set -euo pipefail

cd "$(dirname "$0")/.."
skillshare install gsd-build/get-shit-done --into base --track --force --kind skill --skip-audit
echo "Tracked: skills/base/_get-shit-done"
echo "Update later: skillshare update --group base"
