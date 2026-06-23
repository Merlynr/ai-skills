#!/usr/bin/env bash
# Apply Merlynr-minimal GSD slash-command surface for OpenCode (L1 command/ dir).
set -euo pipefail
cd "$(dirname "$0")/.."
node script/apply-opencode-gsd-surface.js "$@"
