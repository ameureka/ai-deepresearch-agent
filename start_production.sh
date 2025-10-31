#!/bin/bash

# 生产环境启动脚本（模拟 Render 环境）
# 用于本地测试生产配置

set -e

echo "🚀 启动 AI Research Assistant (生产模式)"
echo "=========================================="

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ 错误: .env 文件不存在"
    echo "请复制 .env.example 并填入实际的 API Keys"
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 设置生产环境
export ENV=production
export PORT=8000

# 检查必需的环境变量
required_vars=("DATABASE_URL" "OPENAI_API_KEY" "DEEPSEEK_API_KEY" "TAVILY_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 错误: 环境变量 $var 未设置"
        exit 1
    fi
done

echo "✅ 环境变量检查通过"
echo ""

# 检查依赖
echo "📦 检查依赖..."
if ! pip show gunicorn > /dev/null 2>&1; then
    echo "⚠️  gunicorn 未安装，正在安装..."
    pip install gunicorn
fi

echo "✅ 依赖检查通过"
echo ""

# 启动应用（使用 Gunicorn，模拟 Render 环境）
echo "🌐 启动服务器..."
echo "访问地址: http://localhost:8000"
echo "健康检查: http://localhost:8000/api/health"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

gunicorn main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
