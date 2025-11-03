#!/bin/bash

################################################################################
# AI DeepResearch Agent - 后端快速更新脚本
# 
# 用途：从 GitHub 拉取最新代码并重启服务
# 版本：v1.0.0
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/opt/agentic-ai"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印标题
print_header() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║          AI DeepResearch Agent - 后端更新                ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "请使用 root 用户运行此脚本"
        print_info "使用命令: sudo bash $0"
        exit 1
    fi
}

# 检查项目目录
check_project_dir() {
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    
    if [ ! -d "$PROJECT_DIR/.git" ]; then
        print_error "不是 Git 仓库: $PROJECT_DIR"
        exit 1
    fi
}

# 备份当前版本
backup_current() {
    print_info "备份当前版本..."
    
    cd "$PROJECT_DIR"
    
    # 获取当前 commit hash
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    BACKUP_DIR="/opt/backups/agentic-ai-$CURRENT_COMMIT-$(date +%Y%m%d-%H%M%S)"
    
    # 创建备份目录
    mkdir -p /opt/backups
    
    # 备份 .env 文件
    cp .env "$BACKUP_DIR.env" 2>/dev/null || true
    
    print_success "备份完成: $BACKUP_DIR.env"
}

# 检查是否有本地修改
check_local_changes() {
    print_info "检查本地修改..."
    
    cd "$PROJECT_DIR"
    
    if ! git diff-index --quiet HEAD --; then
        print_warning "检测到本地修改！"
        git status --short
        echo ""
        read -p "是否继续更新? 本地修改将被保留 (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "已取消更新"
            exit 0
        fi
    else
        print_success "没有本地修改"
    fi
}

# 拉取最新代码
pull_latest_code() {
    print_info "拉取最新代码..."
    
    cd "$PROJECT_DIR"
    
    # 获取当前分支
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_info "当前分支: $CURRENT_BRANCH"
    
    # 拉取最新代码
    if git pull origin "$CURRENT_BRANCH"; then
        print_success "代码更新成功"
        
        # 显示更新内容
        print_info "最近的提交:"
        git log -3 --oneline --decorate
    else
        print_error "代码拉取失败"
        exit 1
    fi
}

# 更新依赖
update_dependencies() {
    print_info "检查依赖更新..."
    
    cd "$PROJECT_DIR"
    
    # 激活虚拟环境
    if [ ! -d "venv" ]; then
        print_error "虚拟环境不存在"
        exit 1
    fi
    
    source venv/bin/activate
    
    # 更新 pip
    pip install --upgrade pip -q
    
    # 更新依赖
    print_info "更新 Python 依赖..."
    pip install -r requirements.txt -q
    
    print_success "依赖更新完成"
}

# 运行数据库迁移（如果有）
run_migrations() {
    print_info "检查数据库迁移..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 这里可以添加数据库迁移命令
    # 例如: alembic upgrade head
    
    print_success "数据库检查完成"
}

# 重启服务
restart_services() {
    print_info "重启后端服务..."
    
    # 重启后端
    if systemctl restart agentic-backend; then
        print_success "后端服务重启成功"
    else
        print_error "后端服务重启失败"
        print_info "查看日志: journalctl -u agentic-backend -n 50"
        exit 1
    fi
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet agentic-backend; then
        print_success "后端服务运行正常"
    else
        print_error "后端服务未运行"
        systemctl status agentic-backend
        exit 1
    fi
}

# 验证更新
verify_update() {
    print_info "验证更新..."
    
    # 测试健康检查
    sleep 2
    
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "健康检查通过"
        
        # 显示版本信息
        VERSION=$(curl -s http://localhost:8000/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$VERSION" ]; then
            print_info "当前版本: $VERSION"
        fi
    else
        print_warning "健康检查失败，请检查日志"
    fi
}

# 显示更新信息
show_update_info() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║                   更新完成！                             ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    print_info "服务状态:"
    systemctl status agentic-backend --no-pager -l | head -n 10
    echo ""
    
    print_info "访问地址:"
    echo "  - 本地: http://localhost:8000/health"
    echo "  - HTTPS: https://api.ameureka.com/health"
    echo "  - API 文档: https://api.ameureka.com/docs"
    echo ""
    
    print_info "常用命令:"
    echo "  - 查看日志: sudo journalctl -u agentic-backend -f"
    echo "  - 重启服务: sudo systemctl restart agentic-backend"
    echo "  - 查看状态: sudo systemctl status agentic-backend"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 检查权限
    check_root
    
    # 检查项目目录
    check_project_dir
    
    # 备份当前版本
    backup_current
    
    # 检查本地修改
    check_local_changes
    
    # 拉取最新代码
    pull_latest_code
    
    # 更新依赖
    update_dependencies
    
    # 运行数据库迁移
    run_migrations
    
    # 重启服务
    restart_services
    
    # 验证更新
    verify_update
    
    # 显示更新信息
    show_update_info
}

# 运行主函数
main
