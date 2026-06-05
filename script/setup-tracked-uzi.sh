#!/usr/bin/env bash
# Register wbh604/UZI-Skill as skillshare tracked repo under skills/uzi/.
set -euo pipefail
cd "$(dirname "$0")/.."

skillshare install wbh604/UZI-Skill \
  --into uzi \
  --track \
  --force \
  --kind skill \
  --skip-audit \
  --name _UZI-Skill

echo ""
echo "Next:"
echo "  bash script/install-uzi-deps.sh"
echo "  # Windows PowerShell: .\\script\\install-uzi-deps.ps1"
echo "  # optional: playwright install chromium"
echo "  skillshare sync --all --force"
echo "  export UZI_ROOT=\"\$(pwd)/skills/uzi/_UZI-Skill\""
