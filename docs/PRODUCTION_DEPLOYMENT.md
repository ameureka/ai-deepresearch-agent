# 生产环境部署指南

## 概述

本指南详细说明如何将 AI DeepResearch Agent 部署到生产环境。我们采用现代化的微服务架构，使用行业领先的 SaaS 平台。

## 🏗️ 生产架构

```
┌──────────────────────────────────────┐
│ 前端：Vercel                          │
│ - Next.js 15 自动部署                 │
│ - 全球 Edge CDN                       │
│ - 自动 HTTPS                          │
│ - URL: your-app.vercel.app           │
└──────────────┬───────────────────────┘
               │ HTTPS
               ▼
┌──────────────────────────────────────┐
│ 后端：Render 或独立服务器              │
│ - Python uvicorn 部署                 │
│ - 或 Docker 容器（可选）               │
│ - URL: your-backend.onrender.com    │
└──────────────┬───────────────────────┘
               │ SSL/TLS
               ▼
┌──────────────────────────────────────┐
│ 数据库：Neon PostgreSQL               │
│ - Serverless PostgreSQL               │
│ - 自动备份和扩展                       │
│ - URL: ep-xxx.neon.tech              │
└──────────────────────────────────────┘
```

## 📋 部署清单

### 前置准备

- [ ] GitHub 账号并推送代码
- [ ] Vercel 账号
- [ ] Render 账号（或独立服务器）
- [ ] Neon 账号
- [ ] 所有必需的 API Keys

### 部署顺序

1. [ ] 数据库（Neon）
2. [ ] 后端（Render/服务器）
3. [ ] 前端（Vercel）
4. [ ] 验证和测试

---

## 第一步：部署数据库（Neon）

### 1.1 创建生产数据库

1. 访问 https://neon.tech
2. 登录账号
3. 点击 "New Project"
4. 配置：
   - **项目名称**: `ai-research-prod`
   - **区域**: 选择距离用户最近的区域（如 US East）
   - **PostgreSQL 版本**: 15（默认）

### 1.2 获取连接字符串

1. 项目创建后，点击 "Connection Details"
2. 复制连接字符串（Pooled connection）:
   ```
   postgresql://user:password@ep-xxx-prod.neon.tech/neondb?sslmode=require
   ```

### 1.3 初始化数据库

```bash
# 使用 psql 连接
psql "postgresql://user:password@ep-xxx-prod.neon.tech/neondb?sslmode=require"

# 验证连接
SELECT version();

# 创建必要的表（后端会自动创建，这里仅验证）
\dt
```

### 1.4 配置自动备份

1. 在 Neon Dashboard → Settings
2. 启用 "Point-in-time restore"
3. 设置备份保留期（推荐 7 天）

---

## 第二步：部署后端

### 方式 A：Render 部署（推荐）

#### 2.1 创建 Render Web Service

1. 访问 https://render.com
2. 登录并连接 GitHub
3. 点击 "New +" → "Web Service"
4. 选择你的 GitHub 仓库

#### 2.2 配置 Service

**基本设置：**
- **Name**: `ai-research-backend`
- **Region**: 选择距离 Neon 最近的区域
- **Branch**: `main`
- **Root Directory**: 留空（或项目根目录）
- **Runtime**: `Python 3`

**构建和部署：**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2`

#### 2.3 配置环境变量

在 Render Dashboard → Environment:

```bash
# 数据库
DATABASE_URL=postgresql://user:password@ep-xxx-prod.neon.tech/neondb?sslmode=require

# API Keys
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key
SERPER_API_KEY=your-serper-key

# 服务器配置
HOST=0.0.0.0
PORT=10000
WORKERS=2
LOG_LEVEL=INFO

# CORS（添加 Vercel 域名）
ALLOWED_ORIGINS=https://your-app.vercel.app

# 生产环境
ENV=production
ENABLE_COST_TRACKING=true
ENABLE_FALLBACK=true
```

#### 2.4 部署

1. 点击 "Create Web Service"
2. Render 会自动：
   - 克隆代码
   - 安装依赖
   - 启动服务
3. 等待部署完成（约 3-5 分钟）

#### 2.5 获取后端 URL

部署成功后，获取 URL:
```
https://ai-research-backend.onrender.com
```

#### 2.6 验证部署

```bash
# 测试健康检查
curl https://ai-research-backend.onrender.com/health

# 测试 API 文档
# 访问: https://ai-research-backend.onrender.com/docs
```

### 方式 B：独立服务器部署

#### 2.1 准备服务器

```bash
# SSH 登录服务器
ssh user@your-server.com

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装 Nginx（可选，用于反向代理）
sudo apt install nginx -y
```

#### 2.2 克隆代码

```bash
# 克隆仓库
cd /var/www
sudo git clone https://github.com/your/repo.git ai-research
cd ai-research

# 设置权限
sudo chown -R $USER:$USER /var/www/ai-research
```

#### 2.3 配置环境

```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑环境变量
```

#### 2.4 使用 systemd 管理服务

创建 systemd 服务文件:

```bash
sudo nano /etc/systemd/system/ai-research-backend.service
```

内容:

```ini
[Unit]
Description=AI Research Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ai-research
Environment="PATH=/var/www/ai-research/venv/bin"
EnvironmentFile=/var/www/ai-research/.env
ExecStart=/var/www/ai-research/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-research-backend
sudo systemctl start ai-research-backend

# 检查状态
sudo systemctl status ai-research-backend
```

#### 2.5 配置 Nginx 反向代理（可选）

```bash
sudo nano /etc/nginx/sites-available/ai-research
```

内容:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置:

```bash
sudo ln -s /etc/nginx/sites-available/ai-research /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 2.6 配置 SSL（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 第三步：部署前端（Vercel）

详细步骤请参考 [Vercel 部署指南](./VERCEL_DEPLOYMENT.md)

### 快速步骤

1. **登录 Vercel**
   ```bash
   cd ai-chatbot-main
   vercel login
   ```

2. **链接项目**
   ```bash
   vercel link
   ```

3. **配置环境变量**

   在 Vercel Dashboard → Environment Variables:

   ```bash
   # 数据库（同后端）
   POSTGRES_URL=postgresql://user:password@ep-xxx-prod.neon.tech/neondb?sslmode=require

   # 后端 API
   RESEARCH_API_URL=https://ai-research-backend.onrender.com
   NEXT_PUBLIC_API_URL=https://ai-research-backend.onrender.com

   # 认证
   AUTH_SECRET=your-production-secret-min-32-chars
   AUTH_URL=https://your-app.vercel.app/api/auth

   # Vercel 服务（可选）
   BLOB_READ_WRITE_TOKEN=vercel_blob_xxx
   AI_GATEWAY_API_KEY=vercel_ag_xxx

   # 生产环境
   NODE_ENV=production
   ```

4. **部署**
   ```bash
   vercel --prod
   ```

5. **获取 URL**
   ```
   https://your-app.vercel.app
   ```

---

## 第四步：验证部署

### 4.1 健康检查

```bash
# 后端健康检查
curl https://ai-research-backend.onrender.com/health

# 前端检查（浏览器访问）
# https://your-app.vercel.app
```

### 4.2 数据库连接测试

```bash
# 从后端测试
curl https://ai-research-backend.onrender.com/api/health

# 应返回 {"status": "healthy", "database": "connected"}
```

### 4.3 完整流程测试

1. 访问前端: https://your-app.vercel.app
2. 注册/登录账号
3. 发起研究任务
4. 验证 SSE 实时更新
5. 检查研究报告生成

### 4.4 性能测试

```bash
# 测试前端响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://your-app.vercel.app

# 测试后端 API 响应
curl -w "@curl-format.txt" -o /dev/null -s https://ai-research-backend.onrender.com/api/models
```

---

## 生产环境监控

### Vercel 监控

1. **Analytics**
   - 访问 Dashboard → Analytics
   - 查看访问量、性能指标

2. **Speed Insights**
   - 查看 Core Web Vitals
   - 优化页面加载时间

3. **Logs**
   ```bash
   vercel logs --follow
   ```

### Render 监控

1. **Metrics**
   - CPU/Memory 使用率
   - 响应时间
   - 错误率

2. **Logs**
   - 访问 Dashboard → Logs
   - 查看应用日志和错误

3. **Alerts**
   - 配置邮件/Slack 告警
   - 监控服务状态

### Neon 监控

1. **Usage**
   - 存储使用量
   - 计算时间
   - 连接数

2. **Metrics**
   - 查询性能
   - 慢查询分析

3. **Backups**
   - 验证自动备份
   - 测试恢复流程

---

## 安全配置

### 1. 环境变量安全

- ✅ 使用平台提供的环境变量功能
- ✅ 不要在代码中硬编码密钥
- ✅ 定期轮换 API Keys
- ✅ 最小权限原则

### 2. 数据库安全

- ✅ 使用 SSL 连接（`?sslmode=require`）
- ✅ 强密码策略
- ✅ 启用 IP 白名单（Neon）
- ✅ 定期备份验证

### 3. API 安全

- ✅ 配置 CORS 白名单
- ✅ 实现速率限制
- ✅ 使用 HTTPS only
- ✅ 启用请求日志

### 4. 认证安全

- ✅ 使用强 AUTH_SECRET（32+ 字符）
- ✅ 启用 CSRF 保护
- ✅ 实现会话超时
- ✅ 定期审计用户权限

---

## 成本估算

### 免费层（个人/小项目）

| 服务 | 免费额度 | 超出费用 |
|------|----------|----------|
| **Vercel** | 100GB 带宽/月<br/>无限部署 | $20/月起 |
| **Render** | 750 小时/月<br/>512MB RAM | $7/月起 |
| **Neon** | 0.5GB 存储<br/>191 小时计算 | $0.16/GB存储<br/>$0.16/小时 |
| **总计** | **$0/月**（免费层内） | 按需付费 |

### 生产环境（中小团队）

| 服务 | 配置 | 月费用 |
|------|------|--------|
| **Vercel** | Pro 计划 | $20 |
| **Render** | Standard 计划（1GB RAM） | $25 |
| **Neon** | Pro 计划（5GB存储） | $19 |
| **总计** | | **$64/月** |

---

## 故障排查

### 前端部署失败

参考 [Vercel 部署指南 - 故障排查](./VERCEL_DEPLOYMENT.md#故障排查)

### 后端部署失败

**问题**: Render 构建失败

**解决**:
1. 检查 `requirements.txt` 格式
2. 验证 Python 版本兼容性
3. 查看 Render 构建日志

### 数据库连接失败

**问题**: Connection timeout

**解决**:
1. 检查 `DATABASE_URL` 包含 `?sslmode=require`
2. 验证 Neon 数据库状态（未暂停）
3. 检查 IP 白名单配置

### CORS 错误

**问题**: CORS policy blocked

**解决**:
1. 更新后端 `ALLOWED_ORIGINS`
   ```bash
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
2. 重启后端服务
3. 清除浏览器缓存

---

## 维护和更新

### 更新部署

#### 前端更新

```bash
git add .
git commit -m "Update frontend"
git push origin main  # Vercel 自动部署
```

#### 后端更新

**Render**:
```bash
git push origin main  # Render 自动部署
```

**独立服务器**:
```bash
ssh user@your-server.com
cd /var/www/ai-research
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ai-research-backend
```

### 回滚部署

#### Vercel

```bash
vercel rollback <deployment-url>
```

#### Render

1. 访问 Dashboard → Deployments
2. 选择之前的部署
3. 点击 "Redeploy"

---

## 最佳实践

### 1. 分环境部署

- 开发环境: 本地 Vercel Dev + Python
- 预览环境: Vercel Preview Deployments
- 生产环境: Vercel Production + Render/服务器

### 2. 自动化 CI/CD

- 使用 GitHub Actions（可选）
- 自动化测试
- 自动部署到预览环境

### 3. 监控和告警

- 设置 uptime 监控
- 配置错误告警
- 定期性能审计

### 4. 备份策略

- 数据库: 每日自动备份
- 代码: Git 版本控制
- 环境变量: 安全存储

---

## 相关文档

- [Vercel 部署指南](./VERCEL_DEPLOYMENT.md)
- [环境变量配置](./ENVIRONMENT_VARIABLES.md)
- [数据库配置](./DATABASE_CONFIGURATION.md)
- [本地开发指南](./LOCAL_DEVELOPMENT.md)

---

**生产部署完成！访问你的应用: https://your-app.vercel.app 🚀**
