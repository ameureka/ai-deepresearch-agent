#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  系统检查${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查 Docker
echo -e "${BLUE}1. 检查 Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "   ${GREEN}✅ Docker 已安装${NC}"
    DOCKER_VERSION=$(docker --version)
    echo -e "   ${BLUE}   版本: ${DOCKER_VERSION}${NC}"
    
    if docker info &> /dev/null; then
        echo -e "   ${GREEN}✅ Docker 正在运行${NC}"
    else
        echo -e "   ${RED}❌ Docker 未运行${NC}"
        echo -e "   ${YELLOW}   请启动 Docker Desktop${NC}"
    fi
else
    echo -e "   ${RED}❌ Docker 未安装${NC}"
    echo -e "   ${YELLOW}   请安装: https://www.docker.com/products/docker-desktop${NC}"
fi
echo ""

# 2. 检查 .env 文件
echo -e "${BLUE}2. 检查配置文件...${NC}"
if [ -f .env ]; then
    echo -e "   ${GREEN}✅ .env 文件存在${NC}"
    
    # 检查 OPENAI_API_KEY
    if grep -q "OPENAI_API_KEY=sk-" .env && ! grep -q "your-openai-api-key-here\|sk-your-key-here" .env; then
        echo -e "   ${GREEN}✅ OPENAI_API_KEY 已配置${NC}"
    else
        echo -e "   ${RED}❌ OPENAI_API_KEY 未配置${NC}"
    fi
    
    # 检查 TAVILY_API_KEY
    if grep -q "TAVILY_API_KEY=tvly-" .env && ! grep -q "your-tavily-api-key-here\|tvly-your-key-here" .env; then
        echo -e "   ${GREEN}✅ TAVILY_API_KEY 已配置${NC}"
    else
        echo -e "   ${RED}❌ TAVILY_API_KEY 未配置${NC}"
    fi
else
    echo -e "   ${RED}❌ .env 文件不存在${NC}"
    echo -e "   ${YELLOW}   运行: cp .env.example .env${NC}"
fi
echo ""

# 3. 检查 Docker 镜像
echo -e "${BLUE}3. 检查 Docker 镜像...${NC}"
if docker images | grep -q fastapi-postgres-service; then
    echo -e "   ${GREEN}✅ Docker 镜像已构建${NC}"
    IMAGE_SIZE=$(docker images fastapi-postgres-service --format "{{.Size}}")
    echo -e "   ${BLUE}   大小: ${IMAGE_SIZE}${NC}"
else
    echo -e "   ${YELLOW}⚠️  Docker 镜像未构建${NC}"
    echo -e "   ${YELLOW}   运行: docker build -t fastapi-postgres-service .${NC}"
fi
echo ""

# 4. 检查容器状态
echo -e "${BLUE}4. 检查容器状态...${NC}"
if docker ps | grep -q fpsvc; then
    echo -e "   ${GREEN}✅ 容器正在运行${NC}"
    echo -e "   ${BLUE}   访问: http://localhost:8000${NC}"
    echo -e "   ${BLUE}   API 文档: http://localhost:8000/docs${NC}"
elif docker ps -a | grep -q fpsvc; then
    echo -e "   ${YELLOW}⚠️  容器已停止${NC}"
    echo -e "   ${YELLOW}   运行: docker start fpsvc${NC}"
else
    echo -e "   ${YELLOW}⚠️  容器不存在${NC}"
    echo -e "   ${YELLOW}   运行: ./start.sh${NC}"
fi
echo ""

# 5. 检查端口占用
echo -e "${BLUE}5. 检查端口占用...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   ${YELLOW}⚠️  端口 8000 已被占用${NC}"
    echo -e "   ${BLUE}   占用进程:${NC}"
    lsof -Pi :8000 -sTCP:LISTEN | tail -n +2
else
    echo -e "   ${GREEN}✅ 端口 8000 可用${NC}"
fi

if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "   ${YELLOW}⚠️  端口 5432 已被占用${NC}"
    echo -e "   ${BLUE}   占用进程:${NC}"
    lsof -Pi :5432 -sTCP:LISTEN | tail -n +2
else
    echo -e "   ${GREEN}✅ 端口 5432 可用${NC}"
fi
echo ""

# 6. 测试服务（如果运行中）
if docker ps | grep -q fpsvc; then
    echo -e "${BLUE}6. 测试服务...${NC}"
    if curl -s http://localhost:8000/api > /dev/null; then
        echo -e "   ${GREEN}✅ API 响应正常${NC}"
        RESPONSE=$(curl -s http://localhost:8000/api)
        echo -e "   ${BLUE}   响应: ${RESPONSE}${NC}"
    else
        echo -e "   ${RED}❌ API 无响应${NC}"
    fi
    echo ""
fi

# 总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  检查完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 给出建议
if [ -f .env ] && docker images | grep -q fastapi-postgres-service && docker ps | grep -q fpsvc; then
    echo -e "${GREEN}🎉 系统运行正常！${NC}"
    echo -e "${BLUE}访问: http://localhost:8000${NC}"
elif [ ! -f .env ]; then
    echo -e "${YELLOW}📝 下一步: 配置 .env 文件${NC}"
    echo -e "   1. cp .env.example .env"
    echo -e "   2. 编辑 .env 文件，填入 API Keys"
    echo -e "   3. ./start.sh"
elif ! docker images | grep -q fastapi-postgres-service; then
    echo -e "${YELLOW}🔨 下一步: 构建 Docker 镜像${NC}"
    echo -e "   ./start.sh"
else
    echo -e "${YELLOW}🚀 下一步: 启动服务${NC}"
    echo -e "   ./start.sh"
fi
