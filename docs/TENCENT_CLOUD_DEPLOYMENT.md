# 腾讯云后端部署教程（Cloudflare Tunnel 方案）

> FastAPI 后端部署到腾讯云服务器，使用 Cloudflare Tunnel 实现 HTTPS 访问

## 📋 目录

- [部署架构](#部署架构)
- [方案对比](#方案对比)
- [前置条件](#前置条件)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [验证部署](#验证部署)
- [日常运维](#日常运维)
- [故障排查](#故障排查)

---

## 🏗️ 部署架构

### 最终架构图

```
┌─────────────────────────────────────────────────────────────┐
│                  用户浏览器                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Vercel CDN (全球加速)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  前端 (Next.js)                                       │  │
│  │  URL: https://your-app.vercel.app                    │  │
│  │  - 自动 HTTPS                                         │  │
│  │  - 全球 CDN                                           │  │
│  │  - Git push 自动部署                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS API 调用
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Cloudflare Network (全球 CDN)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cloudflare Tunnel                                    │  │
│  │  URL: https://api.yourdomain.com                     │  │
│  │  - 自动 HTTPS (Let's Encrypt)                        │  │
│  │  - DDoS 防护                                          │  │
│  │  - CDN 加速                                           │  │
│  │  - 隐藏服务器真实 IP                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ 加密隧道
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              腾讯云 CVM (Ubuntu)                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  cloudflared (隧道客户端)                             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │ localhost                            │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │  FastAPI Backend                                      │  │
│  │  端口: 8000 (仅本地访问)                              │  │
│  │  - Uvicorn 服务器                                     │  │
│  │  - 多智能体系统                                        │  │
│  │  - SSE 实时推送                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ PostgreSQL 连接
                         ▼
              ┌────────────────────────┐
              │   Neon PostgreSQL      │
              │   (云端托管数据库)      │
              │   - 自动备份            │
              │   - 自动扩展            │
              └────────────────────────┘
```

### 架构特点

✅ **安全性**
- 服务器真实 IP 被隐藏
- 自动 HTTPS 加密
- DDoS 防护
- 无需开放 8000 端口

✅ **性能**
- 全球 CDN 加速
- 智能路由
- 自动缓存

✅ **简单性**
- 无需配置 Nginx
- 无需手动申请证书
- 自动续期

✅ **成本**
- 完全免费
- 无流量限制
- 无带宽限制

---

## 📊 方案对比

### 三种 HTTPS 部署方案对比

| 特性 | Cloudflare Tunnel | Nginx + Certbot | 直接暴露 IP |
|------|-------------------|-----------------|------------|
| **配置难度** | ⭐⭐ 简单 | ⭐⭐⭐ 中等 | ⭐ 最简单 |
| **HTTPS 支持** | ✅ 自动 | ✅ 需配置 | ❌ 不支持 |
| **安装大小** | ~20 MB | ~10 MB | 0 MB |
| **隐藏真实 IP** | ✅ 是 | ❌ 否 | ❌ 否 |
| **DDoS 防护** | ✅ 免费 | ❌ 无 | ❌ 无 |
| **CDN 加速** | ✅ 全球 | ❌ 无 | ❌ 无 |
| **证书管理** | ✅ 自动 | ⚠️ 手动续期 | ❌ 无 |
| **依赖性** | 依赖 Cloudflare | 完全自主 | 无 |
| **可用性** | 99.9%+ | 取决于服务器 | 取决于服务器 |
| **适用场景** | 中小型项目 | 大型项目 | 仅测试 |
| **推荐度** | 🟢 推荐 | 🟢 推荐 | 🔴 不推荐 |

### 为什么选择 Cloudflare Tunnel？

#### ✅ 优势

1. **配置简单**
   - 5-10 分钟完成配置
   - 无需学习 Nginx 配置
   - 无需手动管理证书

2. **安全性高**
   - 隐藏服务器真实 IP
   - 免费 DDoS 防护
   - 自动 HTTPS 加密

3. **性能优秀**
   - 全球 300+ 数据中心
   - 智能路由优化
   - 自动 CDN 缓存

4. **完全免费**
   - 无流量限制
   - 无带宽限制
   - 无隐藏费用

5. **维护简单**
   - 自动更新
   - 自动续期
   - 无需手动干预

#### ⚠️ 注意事项

1. **依赖第三方**
   - 依赖 Cloudflare 服务
   - 如果 Cloudflare 中断，服务也会中断
   - 但 Cloudflare 可用性 > 99.9%

2. **网络延迟**
   - 请求需经过 Cloudflare 网络
   - 但通常因 CDN 加速反而更快

3. **流量监控**
   - 所有流量经过 Cloudflare
   - 隐私敏感项目需考虑

#### 🎯 适用场景

✅ **推荐使用**：
- 个人项目
- 中小型应用
- 快速上线需求
- 预算有限
- 需要 DDoS 防护

❌ **不推荐使用**：
- 大型企业应用（需完全自主控制）
- 极低延迟要求（< 10ms）
- 严格合规要求
- 特殊协议需求

---

## 📝 前置条件

### ✅ 必须具备

- [x] **腾讯云 CVM 服务器**
  - 操作系统：Ubuntu 20.04+ / 22.04
  - 配置：最低 1 核 2GB（推荐 2 核 4GB）
  - 网络：有公网 IP
  
- [x] **域名**
  - 已购买域名（任何服务商）
  - 可以修改 Nameservers
  
- [x] **Cloudflare 账号**
  - 免费注册：https://dash.cloudflare.com/sign-up
  
- [x] **API 密钥**
  - DeepSeek API Key
  - OpenAI API Key
  - Tavily API Key
  
- [x] **Neon 数据库**
  - 已创建数据库
  - 已获取连接字符串

### 📋 需要准备的信息

在开始部署前，请准备好以下信息：

```bash
# 1. 服务器信息
服务器 IP: ___________________
SSH 端口: 22（默认）
登录用户: root

# 2. 域名信息
域名: ___________________
API 子域名: api.___________________

# 3. API 密钥
DEEPSEEK_API_KEY: sk-___________________
OPENAI_API_KEY: sk-___________________
TAVILY_API_KEY: tvly-___________________

# 4. 数据库连接
DATABASE_URL: postgresql://___________________

# 5. Vercel 域名（稍后获取）
VERCEL_URL: https://___________________.vercel.app
```

---

## 🚀 快速部署

### 一键部署脚本

如果你熟悉 Linux，可以使用以下一键脚本快速部署：

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/ameureka/ai-deepresearch-agent/main/scripts/deploy-cloudflare.sh

# 赋予执行权限
chmod +x deploy-cloudflare.sh

# 运行脚本
./deploy-cloudflare.sh
```

脚本会自动完成：
- ✅ 安装系统依赖
- ✅ 克隆项目代码
- ✅ 配置 Python 环境
- ✅ 安装 cloudflared
- ✅ 配置 Systemd 服务

> ⚠️ **注意**：脚本会提示你输入必要的配置信息（API 密钥、数据库连接等）

### 手动部署步骤概览

如果你想了解每一步的细节，请按照以下步骤：

1. [配置 Cloudflare 账号](#步骤-1-配置-cloudflare-账号)
2. [安装系统依赖](#步骤-2-安装系统依赖)
3. [部署后端应用](#步骤-3-部署后端应用)
4. [安装 Cloudflare Tunnel](#步骤-4-安装-cloudflare-tunnel)
5. [配置隧道](#步骤-5-配置隧道)
6. [启动服务](#步骤-6-启动服务)
7. [验证部署](#验证部署)

---

## 📖 详细步骤

### 步骤 1: 配置 Cloudflare 账号

#### 1.1 注册 Cloudflare 账号

1. 访问 https://dash.cloudflare.com/sign-up
2. 使用邮箱注册免费账号
3. 验证邮箱

#### 1.2 添加域名到 Cloudflare

1. 登录 Cloudflare 控制台
2. 点击 "Add a Site"
3. 输入你的域名（例如：`yourdomain.com`）
4. 选择 "Free" 计划
5. Cloudflare 会扫描你的 DNS 记录

#### 1.3 修改 Nameservers

Cloudflare 会提供两个 Nameservers，例如：
```
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

**在你的域名服务商处修改 Nameservers**：

**腾讯云 DNSPod**：
1. 登录腾讯云控制台
2. 进入"域名注册" → 选择域名 → "DNS 管理"
3. 修改 DNS 服务器为 Cloudflare 提供的地址
4. 保存

**阿里云**：
1. 登录阿里云控制台
2. 进入"域名" → 选择域名 → "DNS 修改"
3. 修改 DNS 服务器为 Cloudflare 提供的地址
4. 保存

**GoDaddy**：
1. 登录 GoDaddy 账号
2. 进入"我的产品" → 选择域名 → "管理 DNS"
3. 点击"更改" → "自定义"
4. 输入 Cloudflare 的 Nameservers
5. 保存

#### 1.4 等待 DNS 生效

- ⏱️ 通常需要 5-30 分钟
- 🔍 在 Cloudflare 控制台查看状态
- ✅ 状态变为 "Active" 后即可继续

**验证 DNS 是否生效**：
```bash
# 在本地电脑运行
nslookup yourdomain.com

# 应该看到 Cloudflare 的 IP 地址
```

---

### 步骤 2: 安装系统依赖

SSH 登录你的腾讯云服务器：

```bash
ssh root@你的服务器IP
```

#### 2.1 更新系统

```bash
# 更新软件包列表
sudo apt update

# 升级已安装的软件包
sudo apt upgrade -y
```

#### 2.2 安装基础工具

```bash
# 安装必要的工具
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    build-essential \
    libpq-dev \
    software-properties-common
```

#### 2.3 安装 Python 3.11

```bash
# 添加 deadsnakes PPA（如果系统没有 Python 3.11）
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# 验证安装
python3.11 --version
# 应该显示: Python 3.11.x
```

#### 2.4 配置防火墙（可选但推荐）

```bash
# 安装 ufw
sudo apt install -y ufw

# 允许 SSH（重要！否则会断开连接）
sudo ufw allow 22/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

> ⚠️ **重要**：使用 Cloudflare Tunnel 后，**不需要**开放 8000 端口，服务器更安全！

---

### 步骤 3: 部署后端应用

#### 3.1 克隆项目代码

```bash
# 进入部署目录
cd /opt

# 克隆仓库
sudo git clone https://github.com/ameureka/ai-deepresearch-agent.git agentic-ai

# 进入项目目录
cd /opt/agentic-ai

# 查看项目结构
ls -la
```

#### 3.2 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 验证虚拟环境
which python
# 应该显示: /opt/agentic-ai/venv/bin/python
```

#### 3.3 安装 Python 依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import fastapi; import aisuite; print('Dependencies OK')"
```

#### 3.4 配置环境变量

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
# CORS Configuration (关键！)
# ============================================================================
# 允许 Vercel 前端访问
# 注意：稍后部署 Vercel 后需要更新这里
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000

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

> 💡 **提示**：
> - 将所有 `your-xxx-key-here` 替换为实际的 API 密钥
> - 将 `DATABASE_URL` 替换为 Neon 数据库连接字符串
> - `ALLOWED_ORIGINS` 稍后部署 Vercel 后需要更新

保存文件：`Ctrl+O` → `Enter` → `Ctrl+X`

#### 3.5 测试后端服务

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 启动后端（测试模式）
uvicorn main:app --host 0.0.0.0 --port 8000

# 在另一个终端测试
curl http://localhost:8000/health
# 应该返回: {"status":"healthy","version":"..."}
```

如果测试成功，按 `Ctrl+C` 停止服务。

#### 3.6 配置 Systemd 服务

```bash
# 创建服务文件
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

保存文件。

```bash
# 创建日志目录
sudo mkdir -p /opt/agentic-ai/logs

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable agentic-backend

# 启动服务
sudo systemctl start agentic-backend

# 检查状态
sudo systemctl status agentic-backend
```

应该看到 `Active: active (running)`。

---

### 步骤 4: 安装 Cloudflare Tunnel

#### 4.1 下载 cloudflared

```bash
# 下载最新版本
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 安装
sudo dpkg -i cloudflared-linux-amd64.deb

# 验证安装
cloudflared --version
# 应该显示版本号，例如: cloudflared version 2024.x.x
```

#### 4.2 登录 Cloudflare

```bash
# 登录（会打开浏览器）
cloudflared tunnel login
```

**操作步骤**：
1. 命令会输出一个 URL
2. 复制 URL 到浏览器打开
3. 登录你的 Cloudflare 账号
4. 选择你的域名
5. 点击 "Authorize"
6. 返回终端，应该看到 "You have successfully logged in"

证书会保存到 `~/.cloudflared/cert.pem`

---

### 步骤 5: 配置隧道

#### 5.1 创建隧道

```bash
# 创建隧道（替换为你的项目名）
cloudflared tunnel create agentic-backend
```

**输出示例**：
```
Created tunnel agentic-backend with id 12345678-1234-1234-1234-123456789abc
```

> 📝 **重要**：记下隧道 ID，后面会用到！

#### 5.2 创建配置文件

```bash
# 创建配置目录（如果不存在）
mkdir -p ~/.cloudflared

# 创建配置文件
nano ~/.cloudflared/config.yml
```

**写入以下内容**（替换隧道 ID 和域名）：

```yaml
# 隧道 ID（替换为你的隧道 ID）
tunnel: 12345678-1234-1234-1234-123456789abc

# 凭证文件路径（替换隧道 ID）
credentials-file: /root/.cloudflared/12345678-1234-1234-1234-123456789abc.json

# 入口规则
ingress:
  # API 域名（替换为你的域名）
  - hostname: api.yourdomain.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  
  # 默认规则（必须保留）
  - service: http_status:404
```

> 💡 **配置说明**：
> - `tunnel`: 你的隧道 ID
> - `credentials-file`: 凭证文件路径（自动生成）
> - `hostname`: 你的 API 域名（例如：`api.yourdomain.com`）
> - `service`: 后端服务地址（`http://localhost:8000`）

保存文件。

#### 5.3 配置 DNS

```bash
# 自动创建 DNS 记录（替换隧道名和域名）
cloudflared tunnel route dns agentic-backend api.yourdomain.com
```

**输出示例**：
```
Created CNAME record for api.yourdomain.com
```

这会在 Cloudflare 自动创建一条 CNAME 记录：
```
api.yourdomain.com → 12345678-1234-1234-1234-123456789abc.cfargotunnel.com
```

**验证 DNS 记录**：
1. 登录 Cloudflare 控制台
2. 选择你的域名
3. 进入 "DNS" → "Records"
4. 应该看到新创建的 CNAME 记录

---

### 步骤 6: 启动服务

#### 6.1 测试隧道

```bash
# 前台运行隧道（测试）
cloudflared tunnel run agentic-backend
```

**应该看到**：
```
INF Connection registered connIndex=0
INF Connection registered connIndex=1
INF Connection registered connIndex=2
INF Connection registered connIndex=3
```

**在另一个终端或本地电脑测试**：
```bash
curl https://api.yourdomain.com/health
```

如果返回 `{"status":"healthy",...}`，说明成功！

按 `Ctrl+C` 停止测试。

#### 6.2 配置为系统服务

```bash
# 安装为系统服务
sudo cloudflared service install

# 启动服务
sudo systemctl start cloudflared

# 设置开机自启
sudo systemctl enable cloudflared

# 查看状态
sudo systemctl status cloudflared
```

应该看到 `Active: active (running)`。

#### 6.3 查看日志

```bash
# 实时查看隧道日志
sudo journalctl -u cloudflared -f

# 查看最近 50 行日志
sudo journalctl -u cloudflared -n 50

# 查看后端日志
sudo journalctl -u agentic-backend -f
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
# 检查后端服务
sudo systemctl status agentic-backend

# 检查隧道服务
sudo systemctl status cloudflared

# 应该都显示: Active: active (running)
```

### 2. 测试本地访问

```bash
# 测试后端
curl http://localhost:8000/health

# 应该返回
# {"status":"healthy","version":"3.2.0",...}
```

### 3. 测试 HTTPS 访问

```bash
# 从服务器测试
curl https://api.yourdomain.com/health

# 从本地电脑测试
curl https://api.yourdomain.com/health

# 应该都返回相同的结果
```

### 4. 浏览器访问

打开浏览器，访问：
- **API 文档**: https://api.yourdomain.com/docs
- **健康检查**: https://api.yourdomain.com/health

应该能看到 Swagger UI 文档页面。

### 5. 测试 CORS 配置

```bash
# 测试 CORS 预检请求
curl -X OPTIONS https://api.yourdomain.com/api/research/stream \
  -H "Origin: https://your-app.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 应该看到响应头包含：
# Access-Control-Allow-Origin: https://your-app.vercel.app
```

### 6. 检查隧道连接

```bash
# 查看隧道状态
cloudflared tunnel info agentic-backend

# 查看隧道连接
sudo journalctl -u cloudflared -n 20 | grep "Connection registered"

# 应该看到 4 个连接（默认）
```

---

## 🚀 部署 Vercel 前端

后端部署完成后，现在部署前端到 Vercel。

### 步骤 1: 登录 Vercel

1. 访问 https://vercel.com/signup
2. 使用 GitHub 账号登录
3. 授权 Vercel 访问你的 GitHub 仓库

### 步骤 2: 导入项目

1. 点击 "Add New Project"
2. 选择 `ameureka/ai-deepresearch-agent` 仓库
3. 点击 "Import"

### 步骤 3: 配置项目

**Root Directory**（重要！）：
- 设置为 `ai-chatbot-main`
- 因为前端代码在子目录中

**Framework Preset**：
- 自动检测为 `Next.js`

**Build Command**：
- 保持默认：`pnpm build`

**Output Directory**：
- 保持默认：`.next`

### 步骤 4: 配置环境变量

在 Vercel 项目设置中添加以下环境变量：

```bash
# Database (Neon PostgreSQL)
POSTGRES_URL=postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require

# Backend API (使用你的 Cloudflare Tunnel 域名)
RESEARCH_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Authentication
# 生成: openssl rand -base64 32
AUTH_SECRET=your-random-secret-min-32-chars-here

# Node Environment
NODE_ENV=production
```

### 步骤 5: 部署

1. 点击 "Deploy" 按钮
2. 等待构建完成（约 2-3 分钟）
3. 部署成功后，Vercel 会提供一个域名：`https://your-app.vercel.app`

### 步骤 6: 更新后端 CORS 配置

部署成功后，需要更新后端的 CORS 配置：

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 编辑环境变量
nano /opt/agentic-ai/.env

# 更新 ALLOWED_ORIGINS，添加你的 Vercel 域名
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000

# 保存后重启后端服务
sudo systemctl restart agentic-backend

# 验证配置
sudo journalctl -u agentic-backend -n 20 | grep CORS
```

### 步骤 7: 测试完整流程

1. 访问你的 Vercel 域名：`https://your-app.vercel.app`
2. 注册或登录账号
3. 发送消息："研究一下量子计算"
4. 点击"开始研究"按钮
5. 观察实时进度更新
6. 查看最终研究报告

如果一切正常，恭喜你完成部署！🎉

---

## 🔄 日常运维

### 更新后端代码

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 进入项目目录
cd /opt/agentic-ai

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启后端服务
sudo systemctl restart agentic-backend

# 查看启动日志
sudo journalctl -u agentic-backend -f
```

### 更新前端（Vercel 自动部署）

前端部署在 Vercel，无需手动更新：

1. 推送代码到 GitHub：`git push origin main`
2. Vercel 自动检测并部署
3. 约 2-3 分钟后自动上线

> 💡 **提示**：可以在 Vercel 控制台查看部署状态和日志

### 查看日志

```bash
# 查看后端日志
sudo journalctl -u agentic-backend -f --lines=100

# 查看隧道日志
sudo journalctl -u cloudflared -f --lines=100

# 查看最近的错误
sudo journalctl -u agentic-backend -p err -n 50

# 查看文件日志
tail -f /opt/agentic-ai/logs/backend.log
tail -f /opt/agentic-ai/logs/backend-error.log
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart agentic-backend

# 重启隧道
sudo systemctl restart cloudflared

# 重启所有服务
sudo systemctl restart agentic-backend cloudflared

# 检查状态
sudo systemctl status agentic-backend cloudflared
```

### 停止服务

```bash
# 停止后端
sudo systemctl stop agentic-backend

# 停止隧道
sudo systemctl stop cloudflared

# 禁用开机自启（如果需要）
sudo systemctl disable agentic-backend
sudo systemctl disable cloudflared
```

### 更新 cloudflared

```bash
# 下载最新版本
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 安装更新
sudo dpkg -i cloudflared-linux-amd64.deb

# 重启服务
sudo systemctl restart cloudflared

# 验证版本
cloudflared --version
```

### 监控服务健康

```bash
# 创建健康检查脚本
nano /opt/agentic-ai/health-check.sh
```

**写入以下内容**：

```bash
#!/bin/bash

# 检查后端健康
BACKEND_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$BACKEND_STATUS" != "healthy" ]; then
    echo "Backend unhealthy, restarting..."
    sudo systemctl restart agentic-backend
fi

# 检查隧道状态
TUNNEL_STATUS=$(sudo systemctl is-active cloudflared)
if [ "$TUNNEL_STATUS" != "active" ]; then
    echo "Tunnel down, restarting..."
    sudo systemctl restart cloudflared
fi

echo "Health check completed at $(date)"
```

```bash
# 赋予执行权限
chmod +x /opt/agentic-ai/health-check.sh

# 添加到 crontab（每 5 分钟检查一次）
crontab -e

# 添加以下行
*/5 * * * * /opt/agentic-ai/health-check.sh >> /opt/agentic-ai/logs/health-check.log 2>&1
```

---

## 🐛 故障排查

### 问题 1: 后端无法启动

**症状**：
- `systemctl status agentic-backend` 显示 `failed`
- 无法访问 `http://localhost:8000/health`

**检查步骤**：

```bash
# 1. 查看详细日志
sudo journalctl -u agentic-backend -n 100 --no-pager

# 2. 检查环境变量
cat /opt/agentic-ai/.env | grep -v "^#" | grep -v "^$"

# 3. 测试数据库连接
cd /opt/agentic-ai
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"

# 4. 手动启动查看错误
cd /opt/agentic-ai
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**常见原因**：
- ❌ API 密钥未配置或无效
- ❌ 数据库连接字符串错误
- ❌ 端口 8000 被占用
- ❌ Python 依赖未安装完整

**解决方案**：
```bash
# 检查端口占用
sudo lsof -i :8000

# 如果被占用，杀死进程
sudo kill -9 <PID>

# 重新安装依赖
cd /opt/agentic-ai
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# 重启服务
sudo systemctl restart agentic-backend
```

---

### 问题 2: Cloudflare Tunnel 无法连接

**症状**：
- `systemctl status cloudflared` 显示 `failed`
- 无法访问 `https://api.yourdomain.com`

**检查步骤**：

```bash
# 1. 查看隧道日志
sudo journalctl -u cloudflared -n 100 --no-pager

# 2. 检查配置文件
cat ~/.cloudflared/config.yml

# 3. 检查凭证文件
ls -la ~/.cloudflared/*.json

# 4. 测试隧道连接
cloudflared tunnel info agentic-backend

# 5. 手动运行隧道
cloudflared tunnel run agentic-backend
```

**常见原因**：
- ❌ 配置文件路径错误
- ❌ 隧道 ID 不匹配
- ❌ 凭证文件丢失
- ❌ DNS 记录未配置

**解决方案**：

```bash
# 重新配置 DNS
cloudflared tunnel route dns agentic-backend api.yourdomain.com

# 重新安装服务
sudo cloudflared service uninstall
sudo cloudflared service install

# 重启服务
sudo systemctl restart cloudflared
```

---

### 问题 3: Vercel 前端无法访问后端

**症状**：
- 前端页面正常显示
- 点击"开始研究"后无响应
- 浏览器控制台显示 CORS 错误或网络错误

**检查步骤**：

```bash
# 1. 测试后端 HTTPS 访问
curl https://api.yourdomain.com/health

# 2. 检查 CORS 配置
grep ALLOWED_ORIGINS /opt/agentic-ai/.env

# 3. 测试 CORS
curl -X OPTIONS https://api.yourdomain.com/api/research/stream \
  -H "Origin: https://your-app.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**解决方案**：

1. **更新 CORS 配置**：
   ```bash
   nano /opt/agentic-ai/.env
   
   # 确保包含你的 Vercel 域名
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000
   
   # 重启服务
   sudo systemctl restart agentic-backend
   ```

2. **检查 Vercel 环境变量**：
   - 登录 Vercel 控制台
   - 检查 `NEXT_PUBLIC_API_URL` 是否正确
   - 格式：`https://api.yourdomain.com`

3. **重新部署 Vercel**：
   - 在 Vercel 控制台点击 "Redeploy"

---

### 问题 4: DNS 解析失败

**症状**：
- `ping api.yourdomain.com` 无响应
- `nslookup api.yourdomain.com` 找不到记录

**检查步骤**：

```bash
# 1. 检查 Nameservers 是否已更新
nslookup yourdomain.com

# 2. 检查 DNS 记录
dig api.yourdomain.com

# 3. 在 Cloudflare 控制台检查
# DNS → Records → 查找 api.yourdomain.com
```

**解决方案**：

1. **等待 DNS 生效**（最多 48 小时，通常 5-30 分钟）

2. **重新创建 DNS 记录**：
   ```bash
   cloudflared tunnel route dns agentic-backend api.yourdomain.com
   ```

3. **手动添加 DNS 记录**：
   - 登录 Cloudflare 控制台
   - DNS → Add Record
   - Type: CNAME
   - Name: api
   - Target: `<隧道ID>.cfargotunnel.com`
   - Proxy status: Proxied (橙色云朵)

---

### 问题 5: 数据库连接失败

**症状**：
- 后端日志显示数据库连接错误
- 前端无法加载数据

**检查步骤**：

```bash
# 1. 测试数据库连接
psql "postgresql://user:password@ep-xxx.neon.tech/dbname?sslmode=require"

# 2. 检查连接字符串
grep DATABASE_URL /opt/agentic-ai/.env

# 3. 检查 Neon 数据库状态
# 登录 Neon 控制台查看数据库是否暂停（免费版会自动暂停）
```

**解决方案**：

1. **确保连接字符串包含 SSL 参数**：
   ```bash
   DATABASE_URL=postgresql://...?sslmode=require
   ```

2. **唤醒 Neon 数据库**（如果已暂停）：
   - 登录 Neon 控制台
   - 点击数据库
   - 等待自动唤醒

3. **检查 IP 白名单**（如果配置了）：
   - 在 Neon 控制台添加服务器 IP

---

### 问题 6: 隧道连接不稳定

**症状**：
- 间歇性无法访问
- 隧道日志显示频繁重连

**检查步骤**：

```bash
# 查看隧道日志
sudo journalctl -u cloudflared -n 200 | grep -E "error|disconnect|reconnect"

# 检查网络连接
ping 1.1.1.1

# 检查服务器负载
top
```

**解决方案**：

1. **增加隧道连接数**：
   ```bash
   nano ~/.cloudflared/config.yml
   
   # 添加配置
   protocol: quic
   no-autoupdate: true
   ```

2. **重启隧道**：
   ```bash
   sudo systemctl restart cloudflared
   ```

3. **检查服务器资源**：
   - 如果 CPU/内存不足，考虑升级配置

---

## 🔐 安全加固

### 1. 配置 SSH 密钥登录

```bash
# 在本地电脑生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 复制公钥到服务器
ssh-copy-id root@你的服务器IP

# 测试密钥登录
ssh root@你的服务器IP

# 禁用密码登录
sudo nano /etc/ssh/sshd_config

# 修改以下配置
PasswordAuthentication no
PermitRootLogin prohibit-password

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 2. 配置 Fail2ban

```bash
# 安装 Fail2ban
sudo apt install -y fail2ban

# 创建配置文件
sudo nano /etc/fail2ban/jail.local
```

**写入以下内容**：

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
```

```bash
# 启动服务
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 查看状态
sudo fail2ban-client status sshd
```

### 3. 定期更新系统

```bash
# 创建自动更新脚本
sudo nano /opt/agentic-ai/auto-update.sh
```

**写入以下内容**：

```bash
#!/bin/bash

# 更新系统
apt update && apt upgrade -y

# 清理旧包
apt autoremove -y
apt autoclean

# 记录日志
echo "System updated at $(date)" >> /opt/agentic-ai/logs/auto-update.log
```

```bash
# 赋予执行权限
chmod +x /opt/agentic-ai/auto-update.sh

# 添加到 crontab（每周日凌晨 3 点执行）
crontab -e

# 添加以下行
0 3 * * 0 /opt/agentic-ai/auto-update.sh
```

### 4. 配置日志轮转

```bash
# 创建日志轮转配置
sudo nano /etc/logrotate.d/agentic-backend
```

**写入以下内容**：

```
/opt/agentic-ai/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    postrotate
        systemctl reload agentic-backend > /dev/null 2>&1 || true
    endscript
}
```

---

## 📊 性能优化

### 1. 调整 Uvicorn Workers

根据服务器 CPU 核心数调整：

```bash
# 查看 CPU 核心数
nproc

# 编辑服务配置
sudo nano /etc/systemd/system/agentic-backend.service

# 修改 workers 数量（建议：CPU 核心数 * 2）
--workers 8

# 重新加载并重启
sudo systemctl daemon-reload
sudo systemctl restart agentic-backend
```

### 2. 启用 Cloudflare 缓存

登录 Cloudflare 控制台：

1. 选择你的域名
2. 进入 "Caching" → "Configuration"
3. 设置 "Browser Cache TTL": 4 hours
4. 启用 "Always Online"

### 3. 配置 Cloudflare Page Rules

1. 进入 "Rules" → "Page Rules"
2. 创建规则：`api.yourdomain.com/docs*`
3. 设置：Cache Level = Cache Everything
4. 保存

---

## 🎉 部署完成

恭喜！你已经成功部署了 AI DeepResearch Agent！

### 📍 访问地址

- 🌐 **前端**: https://your-app.vercel.app
- 📡 **后端 API**: https://api.yourdomain.com
- 📚 **API 文档**: https://api.yourdomain.com/docs
- ❤️ **健康检查**: https://api.yourdomain.com/health

### ✅ 部署清单

- [x] 腾讯云服务器配置完成
- [x] Python 环境安装完成
- [x] 后端应用部署完成
- [x] Cloudflare Tunnel 配置完成
- [x] DNS 解析配置完成
- [x] HTTPS 访问正常
- [x] Vercel 前端部署完成
- [x] CORS 配置正确
- [x] 研究功能测试通过

### 🚀 下一步建议

1. **监控和日志**
   - 配置日志轮转
   - 设置告警通知
   - 监控服务器资源

2. **性能优化**
   - 根据负载调整 workers
   - 启用 Cloudflare 缓存
   - 配置 CDN 规则

3. **安全加固**
   - 配置 SSH 密钥登录
   - 安装 Fail2ban
   - 定期更新系统

4. **备份策略**
   - Neon 自动备份数据库
   - 定期备份服务器配置
   - 保存环境变量副本

### 📚 相关文档

- [Vercel 部署指南](./VERCEL_DEPLOYMENT.md)
- [环境变量配置](./ENVIRONMENT_VARIABLES.md)
- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [GitHub Issues](https://github.com/ameureka/ai-deepresearch-agent/issues)

### 💬 获取帮助

如果遇到问题：

1. 查看本文档的"故障排查"部分
2. 检查后端日志：`sudo journalctl -u agentic-backend -f`
3. 检查隧道日志：`sudo journalctl -u cloudflared -f`
4. 在 GitHub 提交 Issue

---

**部署教程版本**: v3.0.0  
**最后更新**: 2025-11-03  
**适用版本**: v3.2.0+  
**架构**: Vercel 前端 + 腾讯云后端 + Cloudflare Tunnel + Neon 数据库

---

**Made with ❤️ by the AI DeepResearch Team**
