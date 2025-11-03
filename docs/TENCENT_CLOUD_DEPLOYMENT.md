# 腾讯云服务器单体部署教程

> 完整的后端 + 前端单服务器部署指南（使用 Neon 数据库）

## 📋 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│              腾讯云 CVM (Ubuntu)                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  前端 (Next.js)                                       │  │
│  │  端口: 3000                                           │  │
│  │  URL: http://服务器IP:3000                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  后端 (FastAPI)                                       │  │
│  │  端口: 8000                                           │  │
│  │  URL: http://服务器IP:8000                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Neon PostgreSQL      │
              │   (云端托管数据库)      │
              └────────────────────────┘
```

## 🎯 部署信息

- **仓库地址**: https://github.com/ameureka/ai-deepresearch-agent
- **服务器**: 腾讯云 CVM Ubuntu (root 用户)
- **数据库**: Neon PostgreSQL (已配置)
- **部署方式**: 单体部署（前端 + 后端同一服务器）
- **端口需求**: 
  - 22 (SSH)
  - 3000 (前端)
  - 8000 (后端)

---

## 📝 准备工作

### 1. 腾讯云安全组配置

登录腾讯云控制台，为你的 CVM 配置安全组规则：

| 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|
| TCP | 22 | 0.0.0.0/0 | SSH 登录 |
| TCP | 3000 | 0.0.0.0/0 | Next.js 前端 |
| TCP | 8000 | 0.0.0.0/0 | FastAPI 后端 |

> ⚠️ **生产环境建议**：
> - 限制 SSH (22) 端口仅允许特定 IP 访问
> - 后续可以配置 Nginx 反向代理，只开放 80/443 端口

### 2. 创建部署用户（推荐）

虽然你当前使用 root 用户，但建议创建专用部署用户：

```bash
# 创建部署用户
sudo useradd -m -s /bin/bash appuser

# 设置密码
sudo passwd appuser

# 添加 sudo 权限（可选）
sudo usermod -aG sudo appuser

# 切换到部署用户
sudo -iu appuser
```

> 💡 **提示**：如果继续使用 root 用户部署，跳过此步骤即可。

### 3. 准备 API 密钥

确保你已经获取以下 API 密钥：

- ✅ **DeepSeek API Key**: https://platform.deepseek.com/
- ✅ **OpenAI API Key**: https://platform.openai.com/
- ✅ **Tavily API Key**: https://tavily.com/
- ✅ **Neon Database URL**: 从 Neon 控制台获取连接字符串

---

## 🚀 部署步骤

### 步骤 1: SSH 登录服务器

```bash
ssh root@你的服务器IP
```

### 步骤 2: 安装系统依赖

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装必要的依赖
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    build-essential \
    libpq-dev

# 安装 Node.js 18+ (使用 NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
python3.11 --version  # 应该显示 Python 3.11.x
node --version        # 应该显示 v18.x 或更高
npm --version         # 应该显示 npm 版本
```

### 步骤 3: 克隆项目代码

```bash
# 进入部署目录
cd /opt

# 克隆仓库
sudo git clone https://github.com/ameureka/ai-deepresearch-agent.git agentic-ai

# 设置目录权限（如果使用 appuser）
sudo chown -R appuser:appuser /opt/agentic-ai

# 进入项目目录
cd /opt/agentic-ai
```

### 步骤 4: 配置后端环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

**配置 `.env` 文件**（重要！）：

```bash
# ============================================================================
# API Keys
# ============================================================================
DEEPSEEK_API_KEY=sk-your-deepseek-key-here
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# ============================================================================
# Database (Neon PostgreSQL)
# ============================================================================
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require

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
# 允许前端访问（重要！）
ALLOWED_ORIGINS=http://你的服务器IP:3000,http://localhost:3000

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
```

> ⚠️ **重要提示**：
> - 将 `你的服务器IP` 替换为实际的腾讯云服务器公网 IP
> - 确保 `DATABASE_URL` 包含 `?sslmode=require` 参数
> - `ALLOWED_ORIGINS` 必须包含前端地址，否则会出现 CORS 错误

### 步骤 5: 安装后端依赖

```bash
# 创建 Python 虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import fastapi; import aisuite; print('Dependencies OK')"
```

### 步骤 6: 测试后端服务

```bash
# 激活虚拟环境（如果未激活）
source venv/bin/activate

# 启动后端服务（测试模式）
uvicorn main:app --host 0.0.0.0 --port 8000

# 在另一个终端测试
curl http://localhost:8000/health
# 应该返回: {"status":"healthy","version":"..."}
```

如果测试成功，按 `Ctrl+C` 停止服务，继续下一步。

### 步骤 7: 配置前端环境变量

```bash
# 进入前端目录
cd /opt/agentic-ai/ai-chatbot-main

# 复制环境变量模板
cp .env.local.example .env.local

# 编辑环境变量
nano .env.local
```

**配置 `.env.local` 文件**：

```bash
# ============================================================================
# Database (与后端使用相同的 Neon 连接)
# ============================================================================
POSTGRES_URL=postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require

# ============================================================================
# Backend API Configuration
# ============================================================================
# 服务器端调用（Next.js 服务器组件）
RESEARCH_API_URL=http://localhost:8000

# 客户端调用（浏览器）
NEXT_PUBLIC_API_URL=http://你的服务器IP:8000

# ============================================================================
# Authentication
# ============================================================================
# 生成随机密钥: openssl rand -base64 32
AUTH_SECRET=your-random-secret-min-32-chars-here
AUTH_URL=http://你的服务器IP:3000/api/auth

# ============================================================================
# Node Environment
# ============================================================================
NODE_ENV=production

# ============================================================================
# Vercel Services (可选，如果不使用可以注释掉)
# ============================================================================
# BLOB_READ_WRITE_TOKEN=vercel_blob_xxx
# AI_GATEWAY_API_KEY=vercel_ag_xxx
```

> ⚠️ **重要提示**：
> - `NEXT_PUBLIC_API_URL` 必须使用服务器公网 IP，因为这是浏览器访问的地址
> - `AUTH_SECRET` 必须是至少 32 字符的随机字符串
> - 生成 AUTH_SECRET: `openssl rand -base64 32`

### 步骤 8: 安装前端依赖

```bash
# 确保在前端目录
cd /opt/agentic-ai/ai-chatbot-main

# 安装 pnpm（推荐）
npm install -g pnpm

# 安装依赖
pnpm install

# 或者使用 npm
# npm install
```

### 步骤 9: 构建前端

```bash
# 运行数据库迁移
pnpm db:migrate

# 构建生产版本
pnpm build

# 验证构建
ls -la .next/
```

### 步骤 10: 测试前端服务

```bash
# 启动前端服务（测试模式）
pnpm start

# 在浏览器访问
# http://你的服务器IP:3000
```

如果能正常访问，按 `Ctrl+C` 停止服务，继续配置服务常驻。

---

## 🔧 配置服务常驻（Systemd）

### 1. 创建后端服务

```bash
sudo nano /etc/systemd/system/agentic-backend.service
```

**写入以下内容**：

```ini
[Unit]
Description=Agentic AI FastAPI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/agentic-ai
EnvironmentFile=/opt/agentic-ai/.env
ExecStart=/opt/agentic-ai/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --proxy-headers \
    --timeout-keep-alive 75 \
    --log-level info

Restart=always
RestartSec=10
KillSignal=SIGQUIT
TimeoutStopSec=20

StandardOutput=append:/opt/agentic-ai/logs/backend.log
StandardError=append:/opt/agentic-ai/logs/backend-error.log

[Install]
WantedBy=multi-user.target
```

> 💡 **提示**：如果使用 appuser，将 `User=root` 改为 `User=appuser`

### 2. 创建前端服务

```bash
sudo nano /etc/systemd/system/agentic-frontend.service
```

**写入以下内容**：

```ini
[Unit]
Description=Agentic AI Next.js Frontend
After=network.target agentic-backend.service
Requires=agentic-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/agentic-ai/ai-chatbot-main
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/pnpm start

Restart=always
RestartSec=10
KillSignal=SIGTERM
TimeoutStopSec=20

StandardOutput=append:/opt/agentic-ai/logs/frontend.log
StandardError=append:/opt/agentic-ai/logs/frontend-error.log

[Install]
WantedBy=multi-user.target
```

### 3. 创建日志目录

```bash
# 创建日志目录
sudo mkdir -p /opt/agentic-ai/logs

# 设置权限
sudo chown -R root:root /opt/agentic-ai/logs
# 如果使用 appuser: sudo chown -R appuser:appuser /opt/agentic-ai/logs
```

### 4. 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用并启动后端服务
sudo systemctl enable agentic-backend
sudo systemctl start agentic-backend

# 检查后端状态
sudo systemctl status agentic-backend

# 启用并启动前端服务
sudo systemctl enable agentic-frontend
sudo systemctl start agentic-frontend

# 检查前端状态
sudo systemctl status agentic-frontend
```

### 5. 查看日志

```bash
# 查看后端日志
sudo journalctl -u agentic-backend -f

# 查看前端日志
sudo journalctl -u agentic-frontend -f

# 查看文件日志
tail -f /opt/agentic-ai/logs/backend.log
tail -f /opt/agentic-ai/logs/frontend.log
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
# 检查后端
curl http://localhost:8000/health
# 应该返回: {"status":"healthy",...}

# 检查前端
curl http://localhost:3000
# 应该返回 HTML 内容
```

### 2. 浏览器访问

- **前端**: http://你的服务器IP:3000
- **后端 API 文档**: http://你的服务器IP:8000/docs
- **后端健康检查**: http://你的服务器IP:8000/health

### 3. 测试研究功能

1. 打开前端页面
2. 登录或注册账号
3. 发送消息："研究一下量子计算"
4. 点击"开始研究"按钮
5. 观察实时进度更新
6. 查看最终研究报告

---

## 🔄 日常运维

### 更新代码

```bash
# 进入项目目录
cd /opt/agentic-ai

# 拉取最新代码
git pull origin main

# 更新后端依赖
source venv/bin/activate
pip install -r requirements.txt

# 更新前端依赖
cd ai-chatbot-main
pnpm install
pnpm build

# 重启服务
sudo systemctl restart agentic-backend
sudo systemctl restart agentic-frontend
```

### 查看日志

```bash
# 实时查看后端日志
sudo journalctl -u agentic-backend -f --lines=100

# 实时查看前端日志
sudo journalctl -u agentic-frontend -f --lines=100

# 查看错误日志
tail -f /opt/agentic-ai/logs/backend-error.log
tail -f /opt/agentic-ai/logs/frontend-error.log
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart agentic-backend

# 重启前端
sudo systemctl restart agentic-frontend

# 重启所有服务
sudo systemctl restart agentic-backend agentic-frontend
```

### 停止服务

```bash
# 停止后端
sudo systemctl stop agentic-backend

# 停止前端
sudo systemctl stop agentic-frontend
```

---

## 🐛 故障排查

### 问题 1: 后端无法启动

**检查步骤**：

```bash
# 1. 检查环境变量
cat /opt/agentic-ai/.env | grep -v "^#" | grep -v "^$"

# 2. 检查数据库连接
cd /opt/agentic-ai
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"

# 3. 手动启动查看错误
cd /opt/agentic-ai
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 4. 查看详细日志
sudo journalctl -u agentic-backend -n 100 --no-pager
```

**常见原因**：
- ❌ API 密钥未配置或无效
- ❌ 数据库连接字符串错误
- ❌ 端口 8000 被占用
- ❌ Python 依赖未安装完整

### 问题 2: 前端无法访问后端

**检查步骤**：

```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查 CORS 配置
grep ALLOWED_ORIGINS /opt/agentic-ai/.env

# 3. 检查前端环境变量
grep NEXT_PUBLIC_API_URL /opt/agentic-ai/ai-chatbot-main/.env.local

# 4. 测试网络连接
curl -v http://你的服务器IP:8000/health
```

**解决方案**：
- ✅ 确保 `.env` 中的 `ALLOWED_ORIGINS` 包含前端地址
- ✅ 确保 `.env.local` 中的 `NEXT_PUBLIC_API_URL` 使用正确的服务器 IP
- ✅ 检查腾讯云安全组是否开放 8000 端口

### 问题 3: 前端构建失败

**检查步骤**：

```bash
# 1. 清除缓存
cd /opt/agentic-ai/ai-chatbot-main
rm -rf .next node_modules

# 2. 重新安装依赖
pnpm install

# 3. 检查 Node.js 版本
node --version  # 应该 >= 18.0.0

# 4. 重新构建
pnpm build
```

### 问题 4: 数据库连接失败

**检查步骤**：

```bash
# 1. 测试数据库连接
psql "postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require"

# 2. 检查 SSL 参数
# 确保连接字符串包含 ?sslmode=require

# 3. 检查 Neon 数据库状态
# 登录 Neon 控制台查看数据库是否暂停（免费版会自动暂停）
```

### 问题 5: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000
sudo lsof -i :3000

# 杀死占用进程
sudo kill -9 <PID>

# 或者修改端口
# 编辑 .env 修改 PORT=8001
# 编辑 .env.local 修改对应的 API URL
```

---

## 🔒 安全加固（可选）

### 1. 配置防火墙

```bash
# 安装 ufw
sudo apt install ufw

# 允许 SSH
sudo ufw allow 22/tcp

# 允许前端
sudo ufw allow 3000/tcp

# 允许后端
sudo ufw allow 8000/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 限制 SSH 访问

```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 修改以下配置
PermitRootLogin no  # 禁止 root 直接登录
PasswordAuthentication no  # 禁用密码登录，仅允许密钥
Port 22  # 或改为其他端口

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 3. 配置 Fail2ban

```bash
# 安装 Fail2ban
sudo apt install fail2ban

# 启用服务
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📈 性能优化（可选）

### 1. 增加 Uvicorn Workers

根据服务器 CPU 核心数调整：

```bash
# 编辑后端服务
sudo nano /etc/systemd/system/agentic-backend.service

# 修改 workers 数量
--workers 8  # 建议设置为 CPU 核心数 * 2

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart agentic-backend
```

### 2. 启用 PM2 管理前端（替代 systemd）

```bash
# 安装 PM2
npm install -g pm2

# 启动前端
cd /opt/agentic-ai/ai-chatbot-main
pm2 start pnpm --name "agentic-frontend" -- start

# 设置开机自启
pm2 startup
pm2 save

# 查看状态
pm2 status
pm2 logs agentic-frontend
```

---

## 🎉 部署完成

恭喜！你已经成功在腾讯云服务器上部署了 AI DeepResearch Agent。

**访问地址**：
- 🌐 前端: http://你的服务器IP:3000
- 📡 后端 API: http://你的服务器IP:8000/docs

**下一步建议**：
1. 配置域名和 HTTPS（使用 Nginx + Certbot）
2. 设置定期备份
3. 配置监控告警
4. 优化数据库性能

如需帮助，请参考：
- [GitHub Issues](https://github.com/ameureka/ai-deepresearch-agent/issues)
- [项目文档](https://github.com/ameureka/ai-deepresearch-agent/tree/main/docs)

---

**部署教程版本**: v1.0.0  
**最后更新**: 2025-11-03  
**适用版本**: v3.2.0+
