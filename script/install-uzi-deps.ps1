# Install UZI Python deps on Windows — UTF-8 + temporarily clear proxy for pip.
param(
    [string]$RepoRoot = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Write-UziInfo([string]$Message) {
    Write-Host "[uzi-deps] $Message" -ForegroundColor Green
}

function Write-UziWarn([string]$Message) {
    Write-Host "[uzi-deps] WARN: $Message" -ForegroundColor Yellow
}

if ($RepoRoot -eq "") {
    $RepoRoot = Join-Path $env:APPDATA "skillshare"
}

$UziRoot = Join-Path $RepoRoot "skills\uzi\_UZI-Skill"
$ReqFile = Join-Path $UziRoot "requirements.txt"

if (-not (Test-Path $ReqFile)) {
    Write-UziWarn "requirements.txt missing: $ReqFile"
    exit 0
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-UziWarn "python not found"
    exit 1
}

$ProxyVars = @(
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy"
)

$saved = @{}
foreach ($name in $ProxyVars) {
    $item = Get-Item -Path "Env:$name" -ErrorAction SilentlyContinue
    $saved[$name] = if ($item) { $item.Value } else { $null }
}

Write-UziInfo "Temporarily clearing proxy env for pip (domestic mirror / direct)"
foreach ($name in $ProxyVars) {
    Remove-Item -Path "Env:$name" -ErrorAction SilentlyContinue
}
$env:NO_PROXY = "*"
$env:PYTHONUTF8 = "1"

$pipArgs = @(
    "-m", "pip", "install", "--isolated",
    "-r", $ReqFile,
    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
    "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
)

try {
    if ($DryRun) {
        Write-UziInfo "[dry-run] $($python.Source) $($pipArgs -join ' ')"
    } else {
        & $python.Source @pipArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-UziInfo "UZI Python dependencies installed"
    }
} finally {
    Remove-Item -Path Env:NO_PROXY -ErrorAction SilentlyContinue
    Remove-Item -Path Env:PYTHONUTF8 -ErrorAction SilentlyContinue
    foreach ($name in $ProxyVars) {
        if ($null -ne $saved[$name] -and $saved[$name] -ne "") {
            Set-Item -Path "Env:$name" -Value $saved[$name]
        } else {
            Remove-Item -Path "Env:$name" -ErrorAction SilentlyContinue
        }
    }
    Write-UziInfo "Proxy env restored"
}
