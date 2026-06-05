# Skillshare 一键部署脚本 (Windows PowerShell)
# 支持 Windows 10/11

param(
    [string]$Branch = "master",
    [string]$Username = "",
    [switch]$Force,
    [switch]$NoBootstrap,
    [switch]$WithL1,
    [switch]$NoUzi,
    [switch]$NoGsd
)

# 如果未提供用户名，自动检测当前 Windows 用户
if ($Username -eq "" -and ($IsWindows -or $env:OS -eq "Windows_NT")) {
    $Username = $env:USERNAME
    if ($Username -ne "") {
        Write-Host "[INFO] 自动检测到用户名: $Username" -ForegroundColor Green
    }
}

# 配置
$REPO_URL = "https://github.com/Merlynr/ai-skills.git"

# 颜色输出
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 检测平台
function Get-Platform {
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        return "windows"
    } elseif ($IsLinux) {
        return "linux"
    } elseif ($IsMacOS) {
        return "macos"
    } else {
        return "unknown"
    }
}

# 获取目标目录
function Get-TargetDir {
    param([string]$Platform)
    
    switch ($Platform) {
        "windows" {
            return "$env:APPDATA\skillshare"
        }
        "linux" {
            return "$HOME/.config/skillshare"
        }
        "macos" {
            return "$HOME/.config/skillshare"
        }
        default {
            Write-Error "不支持的平台: $Platform"
            exit 1
        }
    }
}

# 检查依赖
function Test-Dependencies {
    $missing = @()
    
    # 检查 git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        $missing += "git"
    }
    
    # 检查 python
    if (-not (Get-Command python -ErrorAction SilentlyContinue) -and 
        -not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        $missing += "python"
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "缺少依赖: $($missing -join ', ')"
        Write-Info "请先安装这些依赖"
        exit 1
    }
}

# 克隆或更新仓库
function Update-Repository {
    param([string]$TargetDir)
    
    if (Test-Path "$TargetDir\.git") {
        Write-Info "目录已存在，更新中..."
        Set-Location $TargetDir
        git fetch origin
        git reset --hard "origin/$Branch"
        Write-Info "更新完成"
    } else {
        if (Test-Path $TargetDir) {
            Write-Warn "目录存在但不是 git 仓库，备份中..."
            $backup = "${TargetDir}.bak.$(Get-Date -Format 'yyyyMMddHHmmss')"
            Rename-Item $TargetDir $backup
        }
        
        Write-Info "克隆仓库..."
        git clone -b $Branch $REPO_URL $TargetDir
        Write-Info "克隆完成"
    }
}

# 激活平台配置
function Set-PlatformConfig {
    param([string]$TargetDir, [string]$Platform, [string]$Username)
    
    Set-Location $TargetDir
    
    switch ($Platform) {
        "windows" {
            if (Test-Path "setup-config.ps1") {
                & .\setup-config.ps1
                Write-Info "Windows 配置已激活"
            } else {
                Write-Warn "未找到 setup-config.ps1，使用默认配置"
                Copy-Item config.windows.yaml config.yaml -Force
            }
            
            # 如果提供了用户名，替换配置文件中的用户名
            if ($Username -ne "") {
                Write-Info "替换用户名: $Username"
                $configPath = Join-Path $TargetDir "config.yaml"
                if (Test-Path $configPath) {
                    $content = Get-Content $configPath -Raw -Encoding UTF8
                    # 替换所有 C:/Users/xxx/ 为 C:/Users/$Username/
                    $content = $content -replace 'C:/Users/[^/]+/', "C:/Users/$Username/"
                    Set-Content $configPath -Value $content -Encoding UTF8 -NoNewline
                    Write-Info "用户名已替换为: $Username"
                } else {
                    Write-Warn "config.yaml 不存在，无法替换用户名"
                }
            }
        }
        "linux" {
            if (Test-Path "setup-config.sh") {
                & bash setup-config.sh
                Write-Info "Linux 配置已激活"
            } else {
                Write-Warn "未找到 setup-config.sh，使用默认配置"
                Copy-Item config.linux.yaml config.yaml -Force
            }
        }
    }
}

# 检查并安装 skillshare CLI
function Install-SkillshareCli {
    if (Get-Command skillshare -ErrorAction SilentlyContinue) {
        $version = skillshare version 2>&1 | Select-Object -First 1
        Write-Info "skillshare CLI 已安装: $version"
    } else {
        Write-Warn "skillshare CLI 未安装"
        Write-Info "请参考 https://github.com/runkids/skillshare 安装"
        
        # 尝试通过 npm 安装
        if (Get-Command npm -ErrorAction SilentlyContinue) {
            Write-Info "尝试通过 npm 安装..."
            try {
                npm install -g skillshare
                Write-Info "安装成功"
            } catch {
                Write-Warn "npm 安装失败，请手动安装"
            }
        }
    }
}

# 检查并安装 nmem
function Install-Nmem {
    if (Get-Command nmem -ErrorAction SilentlyContinue) {
        Write-Info "nmem CLI 已安装"
    } else {
        Write-Warn "nmem CLI 未安装（可选）"
        Write-Info "如需使用 nmem 功能，请运行: pip install nowledge-mem"
    }
}

# 同步 skills
function Sync-Skills {
    param([string]$TargetDir)
    
    Set-Location $TargetDir
    
    if (Get-Command skillshare -ErrorAction SilentlyContinue) {
        Write-Info "同步 skills..."
        try {
            skillshare sync --all
            Write-Info "同步完成"
        } catch {
            Write-Warn "同步失败，请手动运行: skillshare sync --all"
        }
    } else {
        Write-Warn "skillshare CLI 未安装，跳过同步"
    }
}

# Merlynr bootstrap (Git Bash / WSL; falls back to PowerShell UZI pip on Windows)
function Get-GitBashPath {
    $candidates = @(
        (Get-Command bash -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
        "${env:ProgramFiles}\Git\bin\bash.exe",
        "${env:ProgramFiles(x86)}\Git\bin\bash.exe"
    )
    foreach ($p in $candidates) {
        if ($p -and (Test-Path $p)) { return $p }
    }
    return $null
}

function Install-UziPythonDeps {
    param([string]$TargetDir)

    if ($NoUzi) { return }

    $ps1 = Join-Path $TargetDir "script\install-uzi-deps.ps1"
    if (-not (Test-Path $ps1)) {
        Write-Warn "未找到 install-uzi-deps.ps1，跳过 UZI pip"
        return
    }

    Write-Info "安装 UZI Python 依赖（临时清代理 + 清华源）..."
    try {
        & $ps1 -RepoRoot $TargetDir
    } catch {
        Write-Warn "UZI pip 安装失败: $_"
        Write-Info "可手动运行: .\script\install-uzi-deps.ps1"
    }
}

function Invoke-MerlynrBootstrap {
    param([string]$TargetDir)

    if ($NoBootstrap) {
        Write-Info "跳过 bootstrap（-NoBootstrap）"
        return
    }

    $bootstrap = Join-Path $TargetDir "script\bootstrap-merlynr.sh"
    if (-not (Test-Path $bootstrap)) {
        Write-Warn "未找到 bootstrap-merlynr.sh，跳过"
        Install-UziPythonDeps $TargetDir
        return
    }

    $bashPath = Get-GitBashPath
    if (-not $bashPath) {
        Write-Warn "未找到 bash — 跳过 bootstrap shell 步骤"
        Install-UziPythonDeps $TargetDir
        return
    }

    $args = @()
    if ($WithL1) { $args += "--with-l1" }
    if ($NoUzi) { $args += "--no-uzi" }
    if ($NoGsd) { $args += "--no-gsd" }

    Write-Info "运行 Merlynr bootstrap ($bashPath)..."
    & $bashPath $bootstrap @args

    # Windows: ensure pip deps even if bash pip step failed (proxy/encoding)
    if (-not $NoUzi) {
        Install-UziPythonDeps $TargetDir
    }
}

# 验证部署
function Test-Deployment {
    param([string]$TargetDir)
    
    Write-Info "验证部署..."
    
    # 检查关键文件
    $files = @(
        "config.yaml",
        "skills",
        "script\gsd-team-engine.py",
        "script\skill-registry.json"
    )
    
    $missing = @()
    foreach ($file in $files) {
        if (-not (Test-Path "$TargetDir\$file")) {
            $missing += $file
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "缺少文件: $($missing -join ', ')"
        return $false
    }
    
    # 检查 skills 数量
    $skillCount = (Get-ChildItem "$TargetDir\skills" -Directory -ErrorAction SilentlyContinue).Count
    Write-Info "Skills 数量: $skillCount"
    
    Write-Info "部署验证通过 ✓"
    return $true
}

# 打印部署摘要
function Show-Summary {
    param([string]$TargetDir, [string]$Platform, [string]$Username)
    
    $skillCount = (Get-ChildItem "$TargetDir\skills" -Directory -ErrorAction SilentlyContinue).Count
    $scriptCount = (Get-ChildItem "$TargetDir\script\*.py" -ErrorAction SilentlyContinue).Count
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Skillshare 部署完成" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  平台: $Platform"
    Write-Host "  目录: $TargetDir"
    if ($Username -ne "") {
        Write-Host "  用户名: $Username"
    }
    Write-Host ""
    Write-Host "  已安装组件:"
    Write-Host "    - Skills: $skillCount 个"
    Write-Host "    - Scripts: $scriptCount 个"
    Write-Host ""
    Write-Host "  已完成:"
    Write-Host "    - 配置文件已生成"
    Write-Host "    - Skills 已同步到各工具"
    Write-Host ""
    Write-Host "  验证:"
    Write-Host "    skillshare status"
    Write-Host "    skillshare doctor"
    Write-Host ""
    Write-Host "  UZI 试跑 (Git Bash):"
    Write-Host "    python skills/uzi/_UZI-Skill/run.py 600519.SH --no-browser --depth lite"
    Write-Host ""
    Write-Host "  文档:"
    Write-Host "    - README.md"
    Write-Host "    - UPGRADE-GUIDE.md"
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
}

# 主函数
function Main {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Skillshare 一键部署脚本 (Windows)" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 检测平台
    $platform = Get-Platform
    Write-Info "检测到平台: $platform"
    
    # 获取目标目录
    $targetDir = Get-TargetDir $platform
    Write-Info "目标目录: $targetDir"
    
    # 检查依赖
    Write-Info "检查依赖..."
    Test-Dependencies
    
    # 克隆或更新仓库
    Update-Repository $targetDir
    
    # 激活平台配置
    Set-PlatformConfig $targetDir $platform $Username
    
    # 检查并安装组件
    Install-SkillshareCli
    Install-Nmem
    
    # 同步 skills
    Sync-Skills $targetDir

    # Merlynr stack bootstrap
    Invoke-MerlynrBootstrap $targetDir
    
    # 验证部署
    $valid = Test-Deployment $targetDir
    
    if ($valid) {
        # 打印摘要
        Show-Summary $targetDir $platform $Username
    } else {
        Write-Error "部署验证失败，请检查错误信息"
        exit 1
    }
}

# 运行主函数
Main
