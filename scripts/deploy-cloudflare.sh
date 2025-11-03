#!/bin/bash

################################################################################
# AI DeepResearch Agent - Cloudflare Tunnel 一键部署脚本
# 
# 用途：自动部署后端到腾讯云服务器，使用 Cloudflare Tunnel 实现 HTTPS
# 版本：v1.0.0
# 作者：AI DeepResearch Team
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo "║     AI DeepResearch Agent - Cloudflare Tunnel 部署      ║"
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

# 检查操作系统
check_os() {
    print_info "检查操作系统..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "无法检测操作系统"
        exit 1
    fi
    
    if [[ "$OS" != *"Ubuntu"* ]]; then
        print_warning "此脚本仅在 Ubuntu 上测试过，当前系统: $OS"
        read -p "是否继续? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "操作系统: $OS $VER"
}

# 收集配置信息
collect_config() {
    print_info "收集配置信息..."
    echo ""
    
    # API 密钥
    read -p "请输入 DeepSeek API Key: " DEEPSEEK_API_KEY
    read -p "请输入 OpenAI API Key: " OPENAI_API_KEY
    read -p "请输入 Tavily API Key: " TAVILY_API_KEY
    
    # 数据库连接
    read -p "请输入 Neon 数据库连接字符串: " DATABASE_URL
    
    # 域名
    read -p "请输入你的 API 域名 (例如: api.yourdomain.com): " API_DOMAIN
    
    # Vercel 域名（可选）
    read -p "请输入 Vercel 前端域名 (可选，稍后可修改): " VERCEL_DOMAIN
    if [ -z "$VERCEL_DOMAIN" ]; then
        VERCEL_DOMAIN="https://*.vercel.app"
    fi
    
    # 确认信息
    echo ""
    print_info "请确认以下配置信息:"
    echo "  DeepSeek API Key: ${DEEPSEEK_API_KEY:0:10}..."
    echo "  OpenAI API Key: ${OPENAI_API_KEY:0:10}..."
    echo "  Tavily API Key: ${TAVILY_API_KEY:0:10}..."
    echo "  Database URL: ${DATABASE_URL:0:30}..."
    echo "  API Domain: $API_DOMAIN"
    echo "  Vercel Domain: $VERCEL_DOMAIN"
    echo ""
    
    read -p "确认无误? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "已取消部署"
        exit 1
    fi
}

# 安装系统依赖
install_dependencies() {
    print_info "安装系统依赖..."
    
    # 更新系统
    apt update
    apt upgrade -y
    
    # 安装基础工具
    apt install -y \
        git \
        curl \
        wget \
        vim \
        build-essential \
        libpq-dev \
        software-properties-common \
        jq
    
    # 安装 Python 3.11
    if ! command -v python3.11 &> /dev/null; then
        print_info "安装 Python 3.11..."
        add-apt-repository ppa:deadsnakes/ppa -y
        apt update
        apt install -y python3.11 python3.11-venv python3-pip
    fi
    
    print_success "系统依赖安装完成"
}

# 克隆项目代码
clone_project() {
    print_info "克隆项目代码..."
    
    PROJECT_DIR="/opt/agentic-ai"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "项目目录已存在: $PROJECT_DIR"
        read -p "是否删除并重新克隆? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
        else
            print_info "使用现有项目目录"
            cd "$PROJECT_DIR"
            git pull origin main
            return
        fi
    fi
    
    cd /opt
    git clone https://github.com/ameureka/ai-deepresearch-agent.git agentic-ai
    cd "$PROJECT_DIR"
    
    print_success "项目代码克隆完成"
}

# 配置 Python 环境
setup_python() {
    print_info "配置 Python 环境..."
    
    cd /opt/agentic-ai
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3.11 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    print_success "Python 环境配置完成"
}

# 配置环境变量
setup_env() {
    print_info "配置环境变量..."
    
    cd /opt/agentic-ai
    
    # 创建 .env 文件
    cat > .env << EOF
# ============================================================================
# API Keys
# ============================================================================
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
TAVILY_API_KEY=$TAVILY_API_KEY

# ============================================================================
# Database (Neon PostgreSQL)
# ============================================================================
DATABASE_URL=$DATABASE_URL

# ============================================================================
# Server Configuration
# ============================================================================
HOST=0.0.0.0
PORT=8000
ENV=production
LOG_LEVEL=INFO

# ============================================================================
# CORS Configuration
# ============================================================================
ALLOWED_ORIGINS=$VERCEL_DOMAIN,http://localhost:3000

# ============================================================================
# Uvicorn Workers
# ============================================================================
WORKERS=4

# ============================================================================
# Model Configuration
# ============================================================================
PLANNER_MODEL=deepseek:deepseek-reasoner
RESEARCHER_MODEL=deepseek:deepseek-chat
WRITER_MODEL=deepseek:deepseek-chat
EDITOR_MODEL=deepseek:deepseek-chat
FALLBACK_MODEL=openai:gpt-4o-mini

# ============================================================================
# Context Management
# ============================================================================
ENABLE_CHUNKING=true
CHUNKING_THRESHOLD=0.8
MAX_CHUNK_SIZE=6000
CHUNK_OVERLAP=200
EOF
    
    print_success "环境变量配置完成"
}

# 配置 Systemd 服务
setup_systemd() {
    print_info "配置 Systemd 服务..."
    
    # 创建日志目录
    mkdir -p /opt/agentic-ai/logs
    
    # 创建服务文件
    cat > /etc/systemd/system/agentic-backend.service << EOF
[Unit]
Description=Agentic AI FastAPI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/agentic-ai
EnvironmentFile=/opt/agentic-ai/.env
ExecStart=/opt/agentic-ai/venv/bin/uvicorn main:app \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --workers 4 \\
    --proxy-headers \\
    --timeout-keep-alive 75 \\
    --log-level info

Restart=always
RestartSec=10
KillSignal=SIGQUIT
TimeoutStopSec=20

StandardOutput=append:/opt/agentic-ai/logs/backend.log
StandardError=append:/opt/agentic-ai/logs/backend-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载 systemd
    systemctl daemon-reload
    
    # 启用并启动服务
    systemctl enable agentic-backend
    systemctl start agentic-backend
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet agentic-backend; then
        print_success "后端服务启动成功"
    else
        print_error "后端服务启动失败"
        print_info "查看日志: journalctl -u agentic-backend -n 50"
        exit 1
    fi
}

# 安装 Cloudflare Tunnel
install_cloudflared() {
    print_info "安装 Cloudflare Tunnel..."
    
    # 下载 cloudflared
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    
    # 安装
    dpkg -i cloudflared-linux-amd64.deb
    
    # 清理
    rm cloudflared-linux-amd64.deb
    
    # 验证安装
    if command -v cloudflared &> /dev/null; then
        print_success "cloudflared 安装成功: $(cloudflared --version)"
    else
        print_error "cloudflared 安装失败"
        exit 1
    fi
}

# 配置 Cloudflare Tunnel
setup_cloudflare_tunnel() {
    print_info "配置 Cloudflare Tunnel..."
    echo ""
    print_warning "接下来需要手动完成以下步骤:"
    echo ""
    echo "1. 运行命令: cloudflared tunnel login"
    echo "   - 会打开浏览器，登录 Cloudflare 账号"
    echo "   - 选择你的域名并授权"
    echo ""
    echo "2. 创建隧道: cloudflared tunnel create agentic-backend"
    echo "   - 记下隧道 ID"
    echo ""
    echo "3. 配置 DNS: cloudflared tunnel route dns agentic-backend $API_DOMAIN"
    echo ""
    echo "4. 编辑配置文件: nano ~/.cloudflared/config.yml"
    echo "   - 参考文档配置隧道"
    echo ""
    echo "5. 安装服务: sudo cloudflared service install"
    echo ""
    echo "6. 启动服务: sudo systemctl start cloudflared"
    echo ""
    
    print_info "详细步骤请参考: docs/TENCENT_CLOUD_DEPLOYMENT.md"
    echo ""
    
    read -p "按任意键继续..." -n 1 -r
    echo
}

# 配置防火墙
setup_firewall() {
    print_info "配置防火墙..."
    
    # 安装 ufw
    apt install -y ufw
    
    # 允许 SSH
    ufw allow 22/tcp
    
    # 启用防火墙
    echo "y" | ufw enable
    
    print_success "防火墙配置完成"
    print_info "已开放端口: 22 (SSH)"
    print_info "使用 Cloudflare Tunnel，无需开放 8000 端口"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║                   部署完成！                             ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    
    print_success "后端服务已启动"
    echo ""
    
    print_info "访问地址:"
    echo "  - 本地健康检查: http://localhost:8000/health"
    echo "  - API 文档: http://localhost:8000/docs"
    echo ""
    
    print_info "下一步操作:"
    echo "  1. 配置 Cloudflare Tunnel（参考上面的步骤）"
    echo "  2. 测试 HTTPS 访问: https://$API_DOMAIN/health"
    echo "  3. 部署 Vercel 前端"
    echo "  4. 更新后端 CORS 配置（添加 Vercel 域名）"
    echo ""
    
    print_info "常用命令:"
    echo "  - 查看后端状态: systemctl status agentic-backend"
    echo "  - 查看后端日志: journalctl -u agentic-backend -f"
    echo "  - 重启后端: systemctl restart agentic-backend"
    echo "  - 查看隧道状态: systemctl status cloudflared"
    echo "  - 查看隧道日志: journalctl -u cloudflared -f"
    echo ""
    
    print_info "文档:"
    echo "  - 完整部署指南: /opt/agentic-ai/docs/TENCENT_CLOUD_DEPLOYMENT.md"
    echo "  - GitHub: https://github.com/ameureka/ai-deepresearch-agent"
    echo ""
}

# 主函数
main() {
    print_header
    
    # 检查权限
    check_root
    
    # 检查操作系统
    check_os
    
    # 收集配置信息
    collect_config
    
    # 安装系统依赖
    install_dependencies
    
    # 克隆项目代码
    clone_project
    
    # 配置 Python 环境
    setup_python
    
    # 配置环境变量
    setup_env
    
    # 配置 Systemd 服务
    setup_systemd
    
    # 安装 Cloudflare Tunnel
    install_cloudflared
    
    # 配置防火墙
    setup_firewall
    
    # 配置 Cloudflare Tunnel（手动步骤）
    setup_cloudflare_tunnel
    
    # 显示部署信息
    show_deployment_info
}

# 运行主函数
main
