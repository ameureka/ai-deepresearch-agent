#!/bin/bash

# 腾讯云一键部署脚本
# 用途: 自动化部署 AI Research Assistant 到腾讯云
# 使用: bash deploy_tencent.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    print_error "请使用 root 用户运行此脚本"
    print_info "使用: sudo bash deploy_tencent.sh"
    exit 1
fi

print_info "==================================="
print_info "AI Research Assistant 腾讯云部署脚本"
print_info "==================================="
echo ""

# 步骤 1: 更新系统
print_info "步骤 1/8: 更新系统..."
apt update -y
apt upgrade -y
print_info "✅ 系统更新完成"
echo ""

# 步骤 2: 安装基础软件
print_info "步骤 2/8: 安装基础软件..."
apt install -y git curl wget vim htop net-tools
print_info "✅ 基础软件安装完成"
echo ""

# 步骤 3: 安装 Docker
print_info "步骤 3/8: 安装 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    print_info "✅ Docker 安装完成"
else
    print_info "✅ Docker 已安装"
fi
docker --version
echo ""

# 步骤 4: 安装 Docker Compose
print_info "步骤 4/8: 安装 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_info "✅ Docker Compose 安装完成"
else
    print_info "✅ Docker Compose 已安装"
fi
docker-compose --version
echo ""

# 步骤 5: 安装 Nginx
print_info "步骤 5/8: 安装 Nginx..."
if ! command -v nginx &> /dev/null; then
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
    print_info "✅ Nginx 安装完成"
else
    print_info "✅ Nginx 已安装"
fi
nginx -v
echo ""

# 步骤 6: 克隆代码
print_info "步骤 6/8: 克隆代码..."
cd /opt
if [ -d "ai-deepresearch-agent" ]; then
    print_warn "目录已存在，拉取最新代码..."
    cd ai-deepresearch-agent
    git pull origin main
else
    git clone https://github.com/ameureka/ai-deepresearch-agent.git
    cd ai-deepresearch-agent
fi
print_info "✅ 代码克隆完成"
echo ""

# 步骤 7: 配置环境变量
print_info "步骤 7/8: 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warn "请编辑 .env 文件填入实际的 API Keys"
    print_info "文件位置: /opt/ai-deepresearch-agent/.env"
    print_info ""
    print_info "需要配置的变量:"
    print_info "  - DATABASE_URL"
    print_info "  - OPENAI_API_KEY"
    print_info "  - DEEPSEEK_API_KEY"
    print_info "  - TAVILY_API_KEY"
    print_info ""
    read -p "是否现在编辑 .env 文件? (y/n): " edit_env
    if [ "$edit_env" = "y" ]; then
        vim .env
    fi
else
    print_info "✅ .env 文件已存在"
fi
echo ""

# 步骤 8: 构建并运行 Docker 容器
print_info "步骤 8/8: 构建并运行应用..."

# 停止并删除旧容器（如果存在）
if [ "$(docker ps -aq -f name=ai-app)" ]; then
    print_info "停止旧容器..."
    docker stop ai-app || true
    docker rm ai-app || true
fi

# 构建镜像
print_info "构建 Docker 镜像..."
docker build -t ai-research-assistant:latest .

# 运行容器
print_info "启动容器..."
docker run -d \
  --name ai-app \
  --restart always \
  -p 8000:8000 \
  --env-file .env \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ai-research-assistant:latest

# 等待容器启动
sleep 5

# 检查容器状态
if [ "$(docker ps -q -f name=ai-app)" ]; then
    print_info "✅ 容器启动成功"
    docker ps -f name=ai-app
else
    print_error "容器启动失败"
    print_info "查看日志: docker logs ai-app"
    exit 1
fi
echo ""

# 测试健康检查
print_info "测试健康检查..."
sleep 3
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_info "✅ 健康检查通过"
else
    print_warn "健康检查失败，请查看日志"
fi
echo ""

# 配置 Nginx
print_info "配置 Nginx..."
SERVER_IP=$(curl -s ifconfig.me)

cat > /etc/nginx/sites-available/ai-app << EOF
server {
    listen 80;
    server_name ${SERVER_IP};

    access_log /var/log/nginx/ai-app-access.log;
    error_log /var/log/nginx/ai-app-error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    location /static {
        alias /opt/ai-deepresearch-agent/static;
        expires 30d;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/ai-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并重启 Nginx
nginx -t
systemctl restart nginx
print_info "✅ Nginx 配置完成"
echo ""

# 部署完成
print_info "==================================="
print_info "🎉 部署完成！"
print_info "==================================="
echo ""
print_info "访问地址:"
print_info "  HTTP:  http://${SERVER_IP}"
print_info "  健康检查: http://${SERVER_IP}/api/health"
echo ""
print_info "常用命令:"
print_info "  查看日志: docker logs -f ai-app"
print_info "  重启应用: docker restart ai-app"
print_info "  停止应用: docker stop ai-app"
print_info "  查看状态: docker ps"
echo ""
print_info "下一步:"
print_info "  1. 如果有域名，配置 DNS A 记录指向: ${SERVER_IP}"
print_info "  2. 配置 SSL 证书: certbot --nginx -d 你的域名"
print_info "  3. 更新 ALLOWED_ORIGINS 环境变量"
echo ""
print_info "文档位置:"
print_info "  - 部署指南: /opt/ai-deepresearch-agent/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md"
print_info "  - 设计文档: /opt/ai-deepresearch-agent/TENCENT_CLOUD_DEPLOYMENT_DESIGN.md"
echo ""
print_info "==================================="
