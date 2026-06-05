#!/usr/bin/env bash
# Install UZI Python deps with Windows-safe settings (UTF-8 + no broken proxy).
# Sourced by bootstrap-merlynr.sh or run: bash script/install-uzi-deps.sh [UZI_ROOT]

is_windows_env() {
  case "${OS:-}${MSYSTEM:-}${OSTYPE:-}" in
    *Windows_NT*|*MINGW*|*MSYS*|*CYGWIN*) return 0 ;;
  esac
  return 1
}

pick_python_for_uzi() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
  elif command -v python >/dev/null 2>&1; then
    echo python
  else
    echo "python3 not found" >&2
    return 1
  fi
}

# Save / clear / restore proxy env (pip only — git keeps git config http.proxy)
_UZI_PROXY_VARS=(HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy)
_UZI_PROXY_SAVED=()

_uzi_save_proxy_env() {
  _UZI_PROXY_SAVED=()
  local v
  for v in "${_UZI_PROXY_VARS[@]}"; do
    _UZI_PROXY_SAVED+=("${v}=${!v-}")
  done
}

_uzi_clear_proxy_env() {
  local v
  for v in "${_UZI_PROXY_VARS[@]}"; do
    unset "$v"
  done
  export NO_PROXY="*"
}

_uzi_restore_proxy_env() {
  local entry var val
  unset NO_PROXY
  for entry in "${_UZI_PROXY_SAVED[@]}"; do
    var="${entry%%=*}"
    val="${entry#*=}"
    if [ -n "$val" ]; then
      export "$var=$val"
    else
      unset "$var" 2>/dev/null || true
    fi
  done
}

install_uzi_pip_deps() {
  local uzi_root="${1:-}"
  local py dry_run="${2:-0}"

  if [ -z "$uzi_root" ]; then
    echo "[uzi-deps] ERROR: UZI_ROOT required" >&2
    return 1
  fi
  if [ ! -f "$uzi_root/requirements.txt" ]; then
    echo "[uzi-deps] WARN: requirements.txt missing: $uzi_root" >&2
    return 0
  fi

  py="$(pick_python_for_uzi)" || return 1

  local -a pip_args=(
    -m pip install --isolated
    -r "$uzi_root/requirements.txt"
    -i https://pypi.tuna.tsinghua.edu.cn/simple
    --trusted-host pypi.tuna.tsinghua.edu.cn
  )

  if is_windows_env; then
    echo "[uzi-deps] Windows: temporarily clearing proxy env for pip (direct domestic mirror)"
    _uzi_save_proxy_env
    _uzi_clear_proxy_env
  fi

  if [ "$dry_run" = "1" ]; then
    echo "[uzi-deps] [dry-run] PYTHONUTF8=1 $py ${pip_args[*]}"
  else
    PYTHONUTF8=1 "$py" "${pip_args[@]}"
  fi
  local rc=$?

  if is_windows_env; then
    _uzi_restore_proxy_env
  fi

  return "$rc"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  set -euo pipefail
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  UZI_ROOT="${1:-${UZI_ROOT:-$REPO_ROOT/skills/uzi/_UZI-Skill}}"
  install_uzi_pip_deps "$UZI_ROOT"
fi
