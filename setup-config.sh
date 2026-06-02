#!/usr/bin/env bash
# 激活 Linux 版 skillshare 配置
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -f "$here/config.linux.yaml" "$here/config.yaml"
echo "Activated config.linux.yaml -> config.yaml"
