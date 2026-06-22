#!/usr/bin/env bash
# Upgrade Merlynr GSD stack: L1 runtime → reapply patches → L2 skills → L3 overlay → sync all targets.
#
# Usage:
#   ./script/upgrade-gsd-stack.sh           # full upgrade
#   ./script/upgrade-gsd-stack.sh --dry-run # preview only
#   ./script/upgrade-gsd-stack.sh --skip-l1 # skills/overlay/sync only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SSOT="${SKILLSHARE_SKILLS:-$REPO_ROOT/skills}"

is_windows_env() {
  case "${OS:-}${MSYSTEM:-}${OSTYPE:-}" in
    *Windows_NT*|*MINGW*|*MSYS*|*CYGWIN*) return 0 ;;
  esac
  return 1
}

# MSYS2/Git Bash often set HOME=/home/user while Codex lives under USERPROFILE.
resolve_codex_home() {
  if [ -n "${CODEX_HOME:-}" ]; then
    printf '%s\n' "$CODEX_HOME"
    return
  fi
  if is_windows_env && [ -n "${USERPROFILE:-}" ]; then
    local up="${USERPROFILE//\\//}"
    if [[ "$up" =~ ^([A-Za-z]):/(.*) ]]; then
      up="/$(printf '%s' "${BASH_REMATCH[1]}" | tr 'A-Z' 'a-z')/${BASH_REMATCH[2]}"
    fi
    printf '%s/.codex\n' "${up%/}"
    return
  fi
  printf '%s/.codex\n' "$HOME"
}

CODEX_HOME="$(resolve_codex_home)"
RUNTIME_DIR="$CODEX_HOME/get-shit-done"
PATCHES_DIR="$CODEX_HOME/gsd-local-patches"
BASE_DIR="$SSOT/base"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
BACKUP_DIR="$REPO_ROOT/backups/gsd-base.$TIMESTAMP"

DRY_RUN=0
SKIP_L1=0

log() { printf '[upgrade-gsd] %s\n' "$*"; }
warn() { printf '[upgrade-gsd] WARN: %s\n' "$*" >&2; }
die() { printf '[upgrade-gsd] ERROR: %s\n' "$*" >&2; exit 1; }

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    log "[dry-run] $*"
  else
    log "$*"
    "$@"
  fi
}

# MSYS2 paths (/c/Users/...) break Windows Python when embedded in -c strings.
resolve_py_path() {
  local p="${1//\\//}"
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -m "$p"
    return
  fi
  if [[ "$p" =~ ^/([a-zA-Z])/(.*)$ ]]; then
    printf '%s:/%s\n' "$(printf '%s' "${BASH_REMATCH[1]}" | tr 'a-z' 'A-Z')" "${BASH_REMATCH[2]}"
    return
  fi
  printf '%s\n' "$p"
}

run_python() {
  local script_path="$1"
  shift
  run python3 "$(resolve_py_path "$script_path")" "$@"
}

python_script() {
  local script_path="$1"
  shift
  python3 "$(resolve_py_path "$script_path")" "$@"
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --skip-l1) SKIP_L1=1 ;;
    -h|--help)
      cat <<'EOF'
Usage: upgrade-gsd-stack.sh [--dry-run] [--skip-l1]

  L1  npx @opengsd/gsd-core@latest + remind gsd-reapply-patches
  L2  skillshare update --group base (fallback: rsync from codex)
  L3  add-gsd-metadata.py (+ refine-gsd-tags.py)
  sync skillshare sync --all --force
  verify L1 VERSION, L2 count, workflow reference spot-check
EOF
      exit 0
      ;;
    *) die "Unknown option: $arg (use --help)" ;;
  esac
done

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing command: $1"
}

backup_base_layer() {
  if [ ! -d "$BASE_DIR" ]; then
    warn "No $BASE_DIR yet (legacy flat layout or not migrated)."
    return 0
  fi
  log "Backing up base layer → $BACKUP_DIR"
  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi
  mkdir -p "$(dirname "$BACKUP_DIR")"
  cp -a "$BASE_DIR" "$BACKUP_DIR"
}

# rsync is often missing on Windows MSYS2; cp -a is enough for skill trees.
same_skill_path() {
  local a b
  a="$(cd "$1" 2>/dev/null && pwd -P)" || a="$1"
  b="$(cd "$2" 2>/dev/null && pwd -P)" || b="$2"
  [ "$a" = "$b" ]
}

sync_skill_dir() {
  local src="$1" dest="$2"
  if same_skill_path "$src" "$dest"; then
    return 0
  fi
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --backup --suffix=".bak.$TIMESTAMP" "$src/" "$dest/"
  else
    if [ -d "$dest" ] && [ -n "$(ls -A "$dest" 2>/dev/null || true)" ]; then
      cp -a "$dest" "${dest}.bak.$TIMESTAMP"
    fi
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -a "$src/." "$dest/"
  fi
}

read_l1_version() {
  if [ -f "$RUNTIME_DIR/VERSION" ]; then
    tr -d '\r\n' < "$RUNTIME_DIR/VERSION"
  else
    echo "unknown"
  fi
}

remind_reapply_patches() {
  if [ -d "$PATCHES_DIR" ] && [ -n "$(ls -A "$PATCHES_DIR" 2>/dev/null || true)" ]; then
    warn "Detected runtime local patches in $PATCHES_DIR"
    warn "Run gsd-reapply-patches (or \$gsd-reapply-patches) before using GSD workflows."
  fi
}

upgrade_l1_runtime() {
  log "=== L1: Runtime (get-shit-done) ==="
  local before after
  before="$(read_l1_version)"
  log "L1 version before: $before"

  require_cmd npx
  run npx @opengsd/gsd-core@latest

  after="$(read_l1_version)"
  log "L1 version after: $after"
  remind_reapply_patches
}

upgrade_l2_skills() {
  log "=== L2: Skills SSOT (base layer) ==="
  require_cmd skillshare
  mkdir -p "$BASE_DIR"

  local l2_ok=0
  if [ "$DRY_RUN" -eq 1 ]; then
    log "[dry-run] skillshare update --group base --diff"
  elif skillshare update --group base --diff 2>/dev/null; then
    log "L2: tracked base/_get-shit-done updated"
    l2_ok=1
  fi

  # Vendored gsd-*/SKILL.md still refresh from codex after L1 (upstream has no agent skills tree)
  if [ "$DRY_RUN" -eq 0 ] && [ "$l2_ok" -eq 0 ]; then
    warn "tracked update unavailable — trying B2 fallback from codex"
  elif [ "$DRY_RUN" -eq 1 ]; then
    log "[dry-run] B2 refresh vendored gsd-* from $CODEX_HOME/skills/"
  else
    log "L2: refreshing vendored gsd-*/SKILL.md from codex (post-tracked pull)"
  fi

  local src_count=0
  shopt -s nullglob
  local sources=( "$CODEX_HOME/skills/gsd-"* )
  shopt -u nullglob
  local skip='^(gsd-ns-context|gsd-ns-ideate|gsd-ns-manage|gsd-ns-project|gsd-ns-review|gsd-ns-workflow|gsd-team|gsd-do|gsd-fast|gsd-quick|gsd-update|gsd-reapply-patches)$'

  if [ "${#sources[@]}" -eq 0 ]; then
    local existing=( "$BASE_DIR/gsd-"* )
    if [ "${#existing[@]}" -gt 0 ]; then
      warn "L2 vendored refresh skipped: no gsd-* under $CODEX_HOME/skills/ (using existing $BASE_DIR)"
      return 0
    fi
    die "L2 vendored refresh: no gsd-* skills under $CODEX_HOME/skills/"
  fi

  for src in "${sources[@]}"; do
    [ -d "$src" ] || continue
    local name dest
    name="$(basename "$src")"
    if [[ "$name" =~ $skip ]]; then
      continue
    fi
    dest="$BASE_DIR/$name"
    if same_skill_path "$src" "$dest"; then
      continue
    fi
    src_count=$((src_count + 1))
    if [ "$DRY_RUN" -eq 1 ]; then
      log "[dry-run] sync $src → $dest"
    else
      mkdir -p "$dest"
      sync_skill_dir "$src" "$dest"
    fi
  done

  log "L2 vendored refresh synced $src_count skills into $BASE_DIR"
}

apply_l3_overlay() {
  log "=== L3: Merlynr overlay ==="
  require_cmd python3
  run_python "$SCRIPT_DIR/add-gsd-metadata.py"
  if [ -f "$SCRIPT_DIR/refine-gsd-tags.py" ]; then
    run_python "$SCRIPT_DIR/refine-gsd-tags.py" || warn "refine-gsd-tags.py failed (non-fatal)"
  fi
}

sync_all_targets() {
  log "=== Sync all skillshare targets ==="
  require_cmd skillshare
  run skillshare sync --all --force
  if [ -x "$SCRIPT_DIR/prune-facade-locals.sh" ] && [ "$DRY_RUN" -eq 0 ]; then
    run "$SCRIPT_DIR/prune-facade-locals.sh" "${CURSOR_SKILLS:-$HOME/.cursor/skills}"
  fi
  if command -v node >/dev/null 2>&1 && [ -f "$SCRIPT_DIR/apply-opencode-gsd-surface.js" ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      run node "$SCRIPT_DIR/apply-opencode-gsd-surface.js" --dry-run
    else
      run node "$SCRIPT_DIR/apply-opencode-gsd-surface.js"
    fi
  fi
}

verify_upgrade() {
  log "=== Verify ==="
  local l1 l2_count meta_count py_script_dir py_ssot

  py_script_dir="$(resolve_py_path "$SCRIPT_DIR")"
  py_ssot="$(resolve_py_path "$SSOT")"

  l1="$(read_l1_version)"
  l2_count="$(SKILLSHARE_SKILLS="$py_ssot" python_script "$SCRIPT_DIR/_common.py" 2>/dev/null || echo "?")"
  meta_count="$(SKILLSHARE_SCRIPT_DIR="$py_script_dir" python3 -c "
import os, importlib.util
p = os.path.join(os.environ['SKILLSHARE_SCRIPT_DIR'], 'add-gsd-metadata.py')
spec = importlib.util.spec_from_file_location('gsd_meta', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(len(mod.GSD_METADATA))
" 2>/dev/null || echo "?")"

  log "L1 runtime VERSION: $l1"
  log "L2 gsd skills count: $l2_count (metadata entries: $meta_count)"

  local sample_md
  if [ -f "$BASE_DIR/gsd-plan-phase/SKILL.md" ]; then
    sample_md="$BASE_DIR/gsd-plan-phase/SKILL.md"
  elif [ -f "$SSOT/gsd-plan-phase/SKILL.md" ]; then
    sample_md="$SSOT/gsd-plan-phase/SKILL.md"
  else
    warn "Spot-check skipped: gsd-plan-phase/SKILL.md not found"
    return 0
  fi

  local wf_rel wf_path
  wf_rel="$(grep -oE 'get-shit-done/workflows/[^)[:space:]]+' "$sample_md" | head -1 || true)"
  if [ -n "$wf_rel" ]; then
    wf_path="$CODEX_HOME/$wf_rel"
    if [ -f "$wf_path" ]; then
      log "Spot-check OK: $wf_rel exists"
    else
      warn "Spot-check FAILED: missing $wf_path (L1/L2 version skew?)"
    fi
  fi

  if command -v skillshare >/dev/null 2>&1; then
    skillshare status 2>/dev/null | tail -20 || true
  fi
}

print_rollback_hint() {
  log "=== Done ==="
  if [ -d "$BACKUP_DIR" ]; then
    log "L2 rollback: cp -a $BACKUP_DIR/. $BASE_DIR/ && skillshare sync --all --force"
  fi
  log "L1 rollback: npx @opengsd/gsd-core@<previous-version>"
  log "Runtime patches: run gsd-reapply-patches after L1 rollback"
}

prune_stale_base_backups() {
  local d
  # Legacy: backups lived under skills/ and broke skillshare discovery.
  for d in "$SSOT"/base.backup.*; do
    [ -d "$d" ] || continue
    if [ "$DRY_RUN" -eq 1 ]; then
      log "[dry-run] rm -rf $d"
    else
      log "Removing legacy base backup (duplicate skill discovery): $d"
      rm -rf "$d"
    fi
  done
  for d in "$REPO_ROOT"/backups/gsd-base.*; do
    [ -d "$d" ] || continue
    [ "$d" = "$BACKUP_DIR" ] && continue
    if [ "$DRY_RUN" -eq 1 ]; then
      log "[dry-run] rm -rf $d"
    else
      log "Removing stale gsd-base backup: $d"
      rm -rf "$d"
    fi
  done
}

main() {
  cd "$REPO_ROOT"
  log "SSOT=$SSOT"
  log "CODEX_HOME=$CODEX_HOME"

  backup_base_layer

  if [ "$SKIP_L1" -eq 0 ]; then
    upgrade_l1_runtime
  else
    log "Skipping L1 (--skip-l1)"
  fi

  upgrade_l2_skills
  apply_l3_overlay
  prune_stale_base_backups
  sync_all_targets
  verify_upgrade || warn "Verify step failed (non-fatal)"
  print_rollback_hint
}

main "$@"
