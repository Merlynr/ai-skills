#!/usr/bin/env bash
# Merlynr stack bootstrap — GSD base + UZI engine + sync + OpenCode surface + facade cleanup.
#
# Usage:
#   ./script/bootstrap-merlynr.sh              # default: GSD (skip L1) + UZI + sync
#   ./script/bootstrap-merlynr.sh --with-l1      # include npx @opengsd/gsd-core
#   ./script/bootstrap-merlynr.sh --no-uzi       # skip UZI tracked + pip
#   ./script/bootstrap-merlynr.sh --no-gsd       # skip GSD tracked + upgrade-gsd-stack
#   ./script/bootstrap-merlynr.sh --dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SSOT="${SKILLSHARE_SKILLS:-$REPO_ROOT/skills}"

# shellcheck source=install-uzi-deps.sh
source "$SCRIPT_DIR/install-uzi-deps.sh"

DRY_RUN=0
WITH_L1=0
NO_GSD=0
NO_UZI=0
NO_OPENCODE_SURFACE=0
NO_PRUNE=0
FORCE_UZI=0
FORCE_GSD_BASE=0

log() { printf '[bootstrap] %s\n' "$*"; }
warn() { printf '[bootstrap] WARN: %s\n' "$*" >&2; }
die() { printf '[bootstrap] ERROR: %s\n' "$*" >&2; exit 1; }

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    log "[dry-run] $*"
  else
    log "$*"
    "$@"
  fi
}

usage() {
  cat <<'EOF'
Usage: bootstrap-merlynr.sh [options]

  Post-deploy Merlynr stack: tracked upstreams, pip deps, GSD upgrade, OpenCode surface.

Options:
  --with-l1              Run L1 npx @opengsd/gsd-core (slow; default skips L1)
  --no-gsd               Skip GSD tracked base + upgrade-gsd-stack
  --no-uzi               Skip UZI tracked clone + pip install
  --no-opencode-surface  Skip apply-opencode-gsd-surface.js
  --no-prune             Skip prune-facade-locals.sh (~/.claude/skills)
  --force-uzi            Re-run setup-tracked-uzi even if clone exists
  --force-gsd-base       Re-run setup-tracked-base even if clone exists
  --dry-run              Print steps only
  -h, --help             Show this help

Typical entry points:
  ./deploy.sh                          # clone + config + sync + bootstrap (default)
  curl .../deploy.sh | bash            # remote one-liner (needs pushed master)
EOF
}

for arg in "$@"; do
  case "$arg" in
    --with-l1) WITH_L1=1 ;;
    --no-gsd) NO_GSD=1 ;;
    --no-uzi) NO_UZI=1 ;;
    --no-opencode-surface) NO_OPENCODE_SURFACE=1 ;;
    --no-prune) NO_PRUNE=1 ;;
    --force-uzi) FORCE_UZI=1 ;;
    --force-gsd-base) FORCE_GSD_BASE=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) die "Unknown option: $arg (use --help)" ;;
  esac
done

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing command: $1"
}

step_sync() {
  log "=== skillshare sync ==="
  require_cmd skillshare
  run skillshare sync --all --force
}

step_gsd_base() {
  [ "$NO_GSD" -eq 1 ] && return 0
  local base_clone="$SSOT/base/_get-shit-done"
  if [ -d "$base_clone/.git" ] && [ "$FORCE_GSD_BASE" -eq 0 ]; then
    log "GSD tracked base already present: $base_clone"
    return 0
  fi
  log "=== GSD tracked base ==="
  run bash "$SCRIPT_DIR/setup-tracked-base.sh"
}

step_uzi_engine() {
  [ "$NO_UZI" -eq 1 ] && return 0
  local uzi_root="$SSOT/uzi/_UZI-Skill"
  if [ -f "$uzi_root/run.py" ] && [ "$FORCE_UZI" -eq 0 ]; then
    log "UZI engine already present: $uzi_root"
  else
    log "=== UZI tracked engine ==="
    run bash "$SCRIPT_DIR/setup-tracked-uzi.sh"
  fi

  if [ ! -f "$uzi_root/requirements.txt" ]; then
    warn "UZI requirements.txt missing at $uzi_root — skip pip"
    return 0
  fi

  log "=== UZI Python dependencies ==="
  if [ "$DRY_RUN" -eq 1 ]; then
    install_uzi_pip_deps "$uzi_root" 1 || warn "pip install dry-run failed"
  else
    install_uzi_pip_deps "$uzi_root" 0 \
      || warn "pip install failed (retry: bash script/install-uzi-deps.sh)"
  fi
}

step_gsd_upgrade() {
  [ "$NO_GSD" -eq 1 ] && return 0
  log "=== GSD stack upgrade (L2/L3/sync/surface) ==="
  local extra=()
  if [ "$WITH_L1" -eq 0 ]; then
    extra+=(--skip-l1)
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    extra+=(--dry-run)
  fi
  run bash "$SCRIPT_DIR/upgrade-gsd-stack.sh" "${extra[@]}"
}

step_opencode_surface() {
  [ "$NO_OPENCODE_SURFACE" -eq 1 ] && return 0
  [ "$NO_GSD" -eq 1 ] && return 0
  if [ ! -f "$SCRIPT_DIR/apply-opencode-gsd-surface.js" ]; then
    warn "apply-opencode-gsd-surface.js not found — skip"
    return 0
  fi
  if ! command -v node >/dev/null 2>&1; then
    warn "node not found — skip OpenCode GSD surface"
    return 0
  fi
  log "=== OpenCode GSD slash surface ==="
  run node "$SCRIPT_DIR/apply-opencode-gsd-surface.js"
}

step_prune_claude() {
  [ "$NO_PRUNE" -eq 1 ] && return 0
  if [ ! -x "$SCRIPT_DIR/prune-facade-locals.sh" ]; then
    return 0
  fi
  if [ -d "$HOME/.claude/skills" ]; then
    log "=== Prune non-facade gsd-* in ~/.claude/skills ==="
    run bash "$SCRIPT_DIR/prune-facade-locals.sh" "$HOME/.claude/skills"
  fi
}

verify() {
  log "=== Verify ==="
  local ok=1
  if [ -f "$SSOT/uzi-analysis-stack/SKILL.md" ]; then
    log "  uzi-analysis-stack: OK"
  else
    warn "  uzi-analysis-stack: MISSING (push/pull ai-skills?)"
    ok=0
  fi
  if [ "$NO_UZI" -eq 0 ] && [ -f "$SSOT/uzi/_UZI-Skill/run.py" ]; then
    log "  UZI run.py: OK"
  elif [ "$NO_UZI" -eq 0 ]; then
    warn "  UZI run.py: MISSING"
    ok=0
  fi
  if [ "$NO_GSD" -eq 0 ] && [ -d "$SSOT/base/_get-shit-done" ]; then
    log "  GSD tracked base: OK"
  elif [ "$NO_GSD" -eq 0 ]; then
    warn "  GSD tracked base: MISSING"
    ok=0
  fi
  if command -v skillshare >/dev/null 2>&1; then
    skillshare doctor 2>&1 | tail -5 || true
  fi
  [ "$ok" -eq 1 ] || warn "Some checks failed — see messages above"
}

main() {
  cd "$REPO_ROOT"
  log "REPO_ROOT=$REPO_ROOT"
  log "SSOT=$SSOT"

  step_sync
  step_gsd_base
  step_uzi_engine
  step_gsd_upgrade
  step_opencode_surface
  step_prune_claude
  verify

  log "=== Bootstrap done ==="
  log "Optional: playwright install chromium  # UZI deep mode"
  log "Optional: ./script/upgrade-gsd-stack.sh --with-l1  # if you skipped L1 and need runtime update"
}

main "$@"
