#!/usr/bin/env bash
# Skillshare 一键部署脚本
# 支持 Linux 和 Windows (WSL/Git Bash)

set -euo pipefail

# 配置
REPO_URL="https://github.com/Merlynr/ai-skills.git"
REPO_BRANCH="master"
RUN_BOOTSTRAP=1
BOOTSTRAP_EXTRA=()

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-bootstrap)
            RUN_BOOTSTRAP=0
            shift
            ;;
        --with-l1)
            BOOTSTRAP_EXTRA+=(--with-l1)
            shift
            ;;
        --no-uzi)
            BOOTSTRAP_EXTRA+=(--no-uzi)
            shift
            ;;
        --no-gsd)
            BOOTSTRAP_EXTRA+=(--no-gsd)
            shift
            ;;
        --dry-run)
            BOOTSTRAP_EXTRA+=(--dry-run)
            shift
            ;;
        -h|--help)
            echo "Usage: deploy.sh [--no-bootstrap] [--with-l1] [--no-uzi] [--no-gsd] [--dry-run]"
            exit 0
            ;;
        *)
            log_warn "Unknown arg: $1 (ignored)"
            shift
            ;;
    esac
done

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测平台
detect_platform() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# 获取目标目录
get_target_dir() {
    local platform=$1
    case $platform in
        linux|macos)
            echo "$HOME/.config/skillshare"
            ;;
        windows)
            echo "$APPDATA/skillshare"
            ;;
        *)
            log_error "不支持的平台: $platform"
            exit 1
            ;;
    esac
}

# 检查依赖
check_dependencies() {
    local missing=()
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    # 检查 python3
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "缺少依赖: ${missing[*]}"
        log_info "请先安装这些依赖"
        exit 1
    fi
}

# 克隆或更新仓库
clone_or_update() {
    local target_dir=$1
    
    if [ -d "$target_dir/.git" ]; then
        log_info "目录已存在，更新中..."
        cd "$target_dir"
        git fetch origin
        git reset --hard "origin/$REPO_BRANCH"
        log_info "更新完成"
    else
        if [ -d "$target_dir" ]; then
            log_warn "目录存在但不是 git 仓库，备份中..."
            mv "$target_dir" "${target_dir}.bak.$(date +%Y%m%d%H%M%S)"
        fi
        
        log_info "克隆仓库..."
        git clone -b "$REPO_BRANCH" "$REPO_URL" "$target_dir"
        log_info "克隆完成"
    fi
}

# 激活平台配置
activate_config() {
    local target_dir=$1
    local platform=$2
    
    cd "$target_dir"
    
    case $platform in
        linux|macos)
            if [ -f "setup-config.sh" ]; then
                chmod +x setup-config.sh
                ./setup-config.sh
                log_info "Linux 配置已激活"
            else
                log_warn "未找到 setup-config.sh，使用默认配置"
                cp -f config.linux.yaml config.yaml
            fi
            ;;
        windows)
            if [ -f "setup-config.ps1" ]; then
                powershell -ExecutionPolicy Bypass -File setup-config.ps1
                log_info "Windows 配置已激活"
            else
                log_warn "未找到 setup-config.ps1，使用默认配置"
                cp -f config.windows.yaml config.yaml
            fi
            ;;
    esac
}

# 检查并安装 skillshare CLI
install_skillshare_cli() {
    if command -v skillshare &> /dev/null; then
        log_info "skillshare CLI 已安装: $(skillshare version 2>/dev/null | head -1)"
    else
        log_warn "skillshare CLI 未安装"
        log_info "请参考 https://github.com/runkids/skillshare 安装"
        
        # 尝试通过 npm 安装
        if command -v npm &> /dev/null; then
            log_info "尝试通过 npm 安装..."
            npm install -g skillshare || log_warn "npm 安装失败，请手动安装"
        fi
    fi
}

# 检查并安装 nmem
install_nmem() {
    if command -v nmem &> /dev/null; then
        log_info "nmem CLI 已安装: $(nmem --version 2>/dev/null || echo 'unknown')"
    else
        log_warn "nmem CLI 未安装（可选）"
        log_info "如需使用 nmem 功能，请运行: pip install nowledge-mem"
    fi
}

# 同步 skills
sync_skills() {
    local target_dir=$1
    cd "$target_dir"
    
    if command -v skillshare &> /dev/null; then
        log_info "同步 skills..."
        skillshare sync --all || log_warn "同步失败，请手动运行: skillshare sync --all"
        log_info "同步完成"
    else
        log_warn "skillshare CLI 未安装，跳过同步"
    fi
}

# Merlynr stack bootstrap (GSD base + UZI + OpenCode surface)
run_bootstrap() {
    local target_dir=$1

    if [ "$RUN_BOOTSTRAP" -eq 0 ]; then
        log_info "跳过 bootstrap（--no-bootstrap）"
        return 0
    fi

    if [ ! -f "$target_dir/script/bootstrap-merlynr.sh" ]; then
        log_warn "未找到 bootstrap-merlynr.sh，跳过 Merlynr stack 初始化"
        return 0
    fi

    log_info "运行 Merlynr bootstrap..."
    chmod +x "$target_dir/script/bootstrap-merlynr.sh" 2>/dev/null || true
    bash "$target_dir/script/bootstrap-merlynr.sh" "${BOOTSTRAP_EXTRA[@]}"
}

# 验证部署
verify_deployment() {
    local target_dir=$1
    
    log_info "验证部署..."
    
    # 检查关键文件
    local files=(
        "config.yaml"
        "skills"
        "script/gsd-team-engine.py"
        "script/skill-registry.json"
    )
    
    local missing=()
    for file in "${files[@]}"; do
        if [ ! -e "$target_dir/$file" ]; then
            missing+=("$file")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "缺少文件: ${missing[*]}"
        return 1
    fi
    
    # 检查 skills 数量
    local skill_count=$(ls -d "$target_dir/skills"/*/ 2>/dev/null | wc -l)
    log_info "Skills 数量: $skill_count"
    
    log_info "部署验证通过 ✓"
}

# 打印部署摘要
print_summary() {
    local target_dir=$1
    local platform=$2
    
    echo ""
    echo "=========================================="
    echo "  Skillshare 部署完成"
    echo "=========================================="
    echo ""
    echo "  平台: $platform"
    echo "  目录: $target_dir"
    echo ""
    echo "  已安装组件:"
    echo "    - Skills: $(ls -d "$target_dir/skills"/*/ 2>/dev/null | wc -l) 个"
    echo "    - Scripts: $(ls "$target_dir/script/"*.py 2>/dev/null | wc -l) 个"
    echo ""
    echo "  下一步:"
    echo "    skillshare status"
    echo "    skillshare doctor"
    echo "    # UZI 试跑: python3 $target_dir/skills/uzi/_UZI-Skill/run.py 600519.SH --no-browser --depth lite"
    echo ""
    echo "  文档:"
    echo "    - README.md"
    echo "    - UPGRADE-GUIDE.md"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  Skillshare 一键部署脚本"
    echo "=========================================="
    echo ""
    
    # 检测平台
    local platform=$(detect_platform)
    log_info "检测到平台: $platform"
    
    # 获取目标目录
    local target_dir=$(get_target_dir "$platform")
    log_info "目标目录: $target_dir"
    
    # 检查依赖
    log_info "检查依赖..."
    check_dependencies
    
    # 克隆或更新仓库
    clone_or_update "$target_dir"
    
    # 激活平台配置
    activate_config "$target_dir" "$platform"
    
    # 检查并安装组件
    install_skillshare_cli
    install_nmem
    
    # 同步 skills
    sync_skills "$target_dir"

    # Merlynr stack（GSD base + UZI + OpenCode surface）
    run_bootstrap "$target_dir"
    
    # 验证部署
    verify_deployment "$target_dir"
    
    # 打印摘要
    print_summary "$target_dir" "$platform"
}

# 运行主函数
main "$@"
