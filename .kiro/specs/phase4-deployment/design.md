# Phase 4: 整合部署 - 设计文档

## 文档信息

- **项目**: AI 研究助手
- **阶段**: Phase 4 - 整合部署
- **版本**: 1.0
- **创建日期**: 2025-10-30
- **状态**: 待实施

---

## 概述

Phase 4 的目标是完成项目整合，实现本地联调和生产部署。本文档描述了项目结构、环境配置、部署架构和实施策略。

### 核心目标

1. 整合前后端代码到统一的 monorepo
2. 配置本地开发环境（直接运行 + Docker）
3. 部署到生产环境（Render + Vercel + Neon）
4. 配置防休眠、监控和日志
5. 完成端到端测试和验收

### 设计原则

- **简单优先**: 直接运行优于 Docker，免费层优于付费
- **渐进式**: 先本地联调，再部署生产
- **可回滚**: 保持 Git 历史，支持快速回滚
- **文档化**: 每个步骤都有详细文档

---

## 架构设计

### 1. 项目结构设计

#### 最终目录结构

```
agentic-ai-public-main/
├── src/                    # FastAPI 后端源码
│   ├── agents.py
│   ├── planning_agent.py
│   ├── research_tools.py
│   └── config.py
├── main.py                 # FastAPI 应用入口
├── requirements.txt        # Python 依赖
├── .env.example           # 后端环境变量示例
│
├── ai-chatbot-main/        # Next.js 前端应用
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── .env.example       # 前端环境变量示例
│   └── package.json
│
├── docker-compose.yml      # 本地开发（可选）
├── Dockerfile.backend      # 后端 Docker 镜像
├── .env.local             # 本地环境变量（不提交）
├── .gitignore
└── README.md              # 统一文档
```

#### 设计决策

**决策 1: 前后端平级**
- 理由: 符合 monorepo 最佳实践，地位平等
- 优点: 结构清晰，便于 CI/CD
- 缺点: 无

**决策 2: 移动 achive/ai-chatbot-main → ai-chatbot-main**
- 理由: 去掉 achive 层级，简化结构
- 优点: 更专业，更清晰
- 缺点: 需要移动文件（但很简单）

**决策 3: 保持 src/ 和 main.py 在根目录**
- 理由: 不破坏现有结构
- 优点: 不需要重构，Git 历史清晰
- 缺点: 无


### 2. 环境变量设计

#### 环境变量映射

| 环境 | FastAPI | Next.js | 数据库 |
|------|---------|---------|--------|
| 开发 | localhost:8000 | localhost:3000 | localhost:5432 或 Neon |
| 生产 | Render | Vercel | Neon |

#### 配置文件设计

**根目录 .env.example (FastAPI)**
```bash
# API Keys
DEEPSEEK_API_KEY=your-deepseek-key-here
OPENAI_API_KEY=your-openai-key-here
TAVILY_API_KEY=your-tavily-key-here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/research

# Server
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# Model Configuration
PLANNER_MODEL=openai:o1-mini
RESEARCHER_MODEL=deepseek:deepseek-chat
WRITER_MODEL=openai:gpt-4o-mini
EDITOR_MODEL=deepseek:deepseek-chat
```

**ai-chatbot-main/.env.example (Next.js)**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/research

# Research API
RESEARCH_API_URL=http://localhost:8000

# Auth
AUTH_SECRET=your-auth-secret-here
NEXTAUTH_URL=http://localhost:3000

# Optional: Direct API Keys (if needed)
# DEEPSEEK_API_KEY=your-deepseek-key-here
# OPENAI_API_KEY=your-openai-key-here
```

**根目录 .env.local (本地开发统一)**
```bash
# 这个文件包含所有环境变量，供本地开发使用
# 不提交到 Git

# API Keys
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
TAVILY_API_KEY=tvly-xxx

# Database (本地 PostgreSQL 或 Neon)
DATABASE_URL=postgresql://postgres:local@localhost:5432/research

# URLs
RESEARCH_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000

# Auth
AUTH_SECRET=local-dev-secret-123
```

#### 环境变量验证脚本

**scripts/check-env.sh**
```bash
#!/bin/bash

echo "🔍 检查环境变量配置..."

# 检查后端环境变量
echo "📦 检查后端环境变量..."
required_backend=(
  "DEEPSEEK_API_KEY"
  "OPENAI_API_KEY"
  "TAVILY_API_KEY"
  "DATABASE_URL"
)

for var in "${required_backend[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ 缺少: $var"
  else
    echo "✅ 已配置: $var"
  fi
done

# 检查前端环境变量
echo "🎨 检查前端环境变量..."
cd ai-chatbot-main
required_frontend=(
  "DATABASE_URL"
  "RESEARCH_API_URL"
  "AUTH_SECRET"
)

for var in "${required_frontend[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ 缺少: $var"
  else
    echo "✅ 已配置: $var"
  fi
done

echo "✨ 环境变量检查完成！"
```

### 3. 本地开发环境设计

#### 方案 A: 直接运行（推荐）

**优点**:
- ✅ 更简单，不需要 Docker
- ✅ 开发方便，代码热重载
- ✅ 调试容易
- ✅ 资源占用少

**缺点**:
- 🟡 需要手动启动多个终端
- 🟡 需要本地安装 Python、Node.js、PostgreSQL

**启动步骤**:
```bash
# Terminal 1: 启动 PostgreSQL（可选，或用 Neon）
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=local \
  -p 5432:5432 \
  postgres:15

# Terminal 2: 启动 FastAPI
cd agentic-ai-public-main
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 3: 启动 Next.js
cd ai-chatbot-main
npm install
npm run dev

# 访问
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

#### 方案 B: Docker Compose（可选）

**优点**:
- ✅ 一键启动所有服务
- ✅ 环境统一
- ✅ 便于新人上手

**缺点**:
- 🟡 需要学习 Docker
- 🟡 资源占用多
- 🟡 调试相对复杂

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15
    container_name: research-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: local
      POSTGRES_DB: research
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # FastAPI 后端
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: research-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:local@postgres:5432/research
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - ALLOWED_ORIGINS=http://localhost:3000
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./main.py:/app/main.py
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Next.js 前端
  frontend:
    build:
      context: ./ai-chatbot-main
      dockerfile: Dockerfile
    container_name: research-frontend
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:local@postgres:5432/research
      - RESEARCH_API_URL=http://backend:8000
      - NEXTAUTH_URL=http://localhost:3000
      - AUTH_SECRET=local-dev-secret
    depends_on:
      - backend
    volumes:
      - ./ai-chatbot-main:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev

volumes:
  postgres_data:
```

**启动命令**:
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart backend
```

### 4. Dockerfile 设计

#### Dockerfile.backend (FastAPI)

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**优化点**:
- 使用 slim 镜像减小体积
- 多阶段构建（如需要）
- 健康检查
- 不使用 root 用户（生产环境）

#### Dockerfile (Next.js)

```dockerfile
FROM node:18-alpine AS base

# 安装依赖
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# 构建应用
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# 生产镜像
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

---

## 部署架构

### 1. 生产环境架构

```
┌─────────────────────────────────────────────────────────┐
│                        用户                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Vercel (Next.js 前端)                       │
│  - 静态资源托管                                          │
│  - SSR/SSG                                              │
│  - Edge Functions                                       │
│  - 自动 HTTPS                                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTPS (CORS)
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Render (FastAPI 后端)                       │
│  - Docker 容器                                          │
│  - 健康检查                                             │
│  - 自动 HTTPS                                           │
│  - 防休眠 (cron-job.org)                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ SSL
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Neon (PostgreSQL)                          │
│  - 托管数据库                                           │
│  - 自动备份                                             │
│  - SSL 连接                                             │
└─────────────────────────────────────────────────────────┘
```

### 2. 数据库部署设计

#### Neon 配置步骤

1. **创建项目**
   - 访问 https://neon.tech
   - 创建新项目
   - 选择区域（推荐 US East）

2. **获取连接字符串**
   ```
   postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
   ```

3. **配置环境变量**
   - Render: DATABASE_URL
   - Vercel: DATABASE_URL

4. **运行迁移**
   ```bash
   cd ai-chatbot-main
   npm run db:migrate
   ```

5. **验证**
   ```bash
   npm run db:studio
   ```

#### 数据库 Schema

```sql
-- 用户表（Next.js Auth）
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

-- 聊天表
CREATE TABLE chats (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

-- 消息表
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  chat_id UUID REFERENCES chats(id),
  role VARCHAR(50),
  content TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 研究任务表（Phase 3 新增）
CREATE TABLE research_tasks (
  id UUID PRIMARY KEY,
  chat_id UUID REFERENCES chats(id),
  task_id VARCHAR(255) UNIQUE NOT NULL,
  topic TEXT NOT NULL,
  status VARCHAR(50),
  progress JSONB,
  report TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_research_tasks_chat_id ON research_tasks(chat_id);
CREATE INDEX idx_research_tasks_task_id ON research_tasks(task_id);
```


### 3. 后端部署设计（Render）

#### 部署步骤

1. **创建 Web Service**
   - 登录 Render
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 选择 `agentic-ai-public-main`

2. **配置服务**
   - Name: `research-backend`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - Runtime: `Docker`
   - Dockerfile Path: `Dockerfile.backend`

3. **配置环境变量**
   ```
   DEEPSEEK_API_KEY=sk-xxx
   OPENAI_API_KEY=sk-xxx
   TAVILY_API_KEY=tvly-xxx
   DATABASE_URL=postgresql://...@ep-xxx.neon.tech/db?sslmode=require
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
   ```

4. **配置健康检查**
   - Health Check Path: `/api/health`
   - Health Check Interval: 30s

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（约 5 分钟）
   - 获取 URL: `https://research-backend.onrender.com`

#### 防休眠配置

**问题**: Render 免费层会在 15 分钟无活动后休眠

**解决方案**: 使用 cron-job.org 定期 ping

1. **注册 cron-job.org**
   - 访问 https://cron-job.org
   - 创建免费账号

2. **创建 Cron Job**
   - Title: `Keep Render Alive`
   - URL: `https://research-backend.onrender.com/api/health`
   - Schedule: `*/10 * * * *` (每 10 分钟)
   - Method: `GET`
   - Timeout: 30s

3. **配置告警**
   - 失败通知: Email
   - 连续失败 3 次后通知

4. **验证**
   - 等待 15 分钟
   - 检查服务是否保持活跃
   - 测试冷启动时间 < 60 秒

#### 成本分析

| 计划 | 价格 | 特点 | 推荐 |
|------|------|------|------|
| Free | $0/月 | 15 分钟后休眠，512MB RAM | MVP 阶段 |
| Starter | $7/月 | 不休眠，512MB RAM | 推荐 |
| Standard | $25/月 | 2GB RAM，更好性能 | 有用户后 |

### 4. 前端部署设计（Vercel）

#### 部署步骤

1. **安装 Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **登录**
   ```bash
   vercel login
   ```

3. **进入前端目录**
   ```bash
   cd ai-chatbot-main
   ```

4. **首次部署**
   ```bash
   vercel
   ```
   - 选择项目
   - 确认设置
   - 等待部署完成

5. **配置环境变量**
   ```bash
   # 数据库
   vercel env add DATABASE_URL
   # 输入: postgresql://...@ep-xxx.neon.tech/db?sslmode=require

   # 后端 API
   vercel env add RESEARCH_API_URL
   # 输入: https://research-backend.onrender.com

   # 认证
   vercel env add AUTH_SECRET
   # 输入: 随机字符串（至少 32 字符）

   vercel env add NEXTAUTH_URL
   # 输入: https://your-app.vercel.app
   ```

6. **生产部署**
   ```bash
   vercel --prod
   ```

7. **获取 URL**
   - 生产: `https://your-app.vercel.app`
   - 预览: `https://your-app-xxx.vercel.app`

#### 自动部署配置

Vercel 会自动：
- 监听 GitHub push
- 构建和部署
- 为每个 PR 创建预览环境
- 提供部署状态

#### 自定义域名（可选）

1. 在 Vercel 项目设置中添加域名
2. 配置 DNS 记录
3. 等待 SSL 证书生成

### 5. CORS 配置设计

#### FastAPI CORS 中间件

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 从环境变量读取允许的源
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 环境变量配置

**开发环境**:
```bash
ALLOWED_ORIGINS=http://localhost:3000
```

**生产环境**:
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

#### 验证 CORS

```bash
# 测试 CORS
curl -H "Origin: https://your-app.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://research-backend.onrender.com/api/research/stream

# 应该返回
# Access-Control-Allow-Origin: https://your-app.vercel.app
# Access-Control-Allow-Credentials: true
```

---

## 测试策略

### 1. 本地联调测试

#### 测试清单

- [ ] 后端启动成功
- [ ] 前端启动成功
- [ ] 数据库连接成功
- [ ] 前后端通信正常
- [ ] SSE 连接正常
- [ ] 研究任务正常
- [ ] 报告生成正常

#### 测试脚本

```bash
#!/bin/bash

echo "🧪 开始本地联调测试..."

# 测试后端健康检查
echo "1️⃣ 测试后端健康检查..."
curl http://localhost:8000/api/health
if [ $? -eq 0 ]; then
  echo "✅ 后端健康检查通过"
else
  echo "❌ 后端健康检查失败"
  exit 1
fi

# 测试前端
echo "2️⃣ 测试前端..."
curl http://localhost:3000
if [ $? -eq 0 ]; then
  echo "✅ 前端访问正常"
else
  echo "❌ 前端访问失败"
  exit 1
fi

# 测试数据库连接
echo "3️⃣ 测试数据库连接..."
cd ai-chatbot-main
npm run db:studio &
sleep 5
if pgrep -f "drizzle-kit studio" > /dev/null; then
  echo "✅ 数据库连接正常"
  pkill -f "drizzle-kit studio"
else
  echo "❌ 数据库连接失败"
  exit 1
fi

echo "✨ 本地联调测试完成！"
```

### 2. 端到端测试

#### 测试场景

1. **用户注册和登录**
   - 注册新用户
   - 登录
   - 验证 session

2. **AI 建议研究** ⚠️ (已更新以匹配 Phase 3 新架构)
   - 与 AI 对话（如 "Tell me about quantum computing"）
   - AI 回复包含研究关键词（如 "I can research quantum computing for you"）
   - ResearchButton 在聊天输入框上方显示（sticky 定位在 bottom-[72px]）
   - 验证关键词检测逻辑（detectResearchKeywords 函数）

3. **用户发起研究** ⚠️ (已更新)
   - 用户点击 ResearchButton
   - useResearchProgress Hook 发起 POST SSE 连接
   - 验证 API 路由代理 (/api/research/stream)
   - 验证 prompt 正确传递到后端

4. **实时进度显示** ⚠️ (已更新)
   - SSE 连接建立（使用 fetch-event-source 库，支持 POST）
   - 接收进度事件（start, plan, progress）
   - ResearchProgress 组件在 ResearchPanel 中显示
   - events 数组实时更新
   - 验证进度信息正确渲染（根据 events 动态显示步骤）
   - 验证 status 状态变化（idle → researching → completed）

5. **报告生成** ⚠️ (已更新)
   - 接收 done 事件（包含完整报告）
   - onComplete 回调被触发
   - sendMessage 将报告发送给 AI（格式: "Research completed:\n\n{report}"）
   - AI 收到报告后调用 createDocument 工具
   - 自动创建 Artifact（类型为 "text"）
   - 显示 Markdown 报告
   - ResearchPanel 自动关闭

6. **追问和更新**
   - 用户追问
   - AI 调用 updateDocument 更新报告
   - Artifact 更新
   - 验证报告版本历史

7. **历史记录**
   - 查看历史任务（从数据库读取 research_tasks 表）
   - 点击查看详情
   - 验证数据正确

8. **错误处理**
   - 模拟网络错误
   - 验证错误提示
   - 验证 fetch-event-source 重连机制（最多 3 次）
   - 验证 status 变为 'failed'

9. **断线重连** ⚠️ (已更新)
   - 断开 SSE 连接
   - 验证 fetch-event-source 自动重连（指数退避: 500ms, 1s, 2s）
   - 验证状态恢复
   - 验证最大重试次数限制（3 次）

#### E2E 测试脚本（Playwright）

```typescript
// tests/e2e/research-flow.spec.ts ⚠️ (已更新以匹配 Phase 3 新架构)
import { test, expect } from '@playwright/test';

test.describe('研究流程 (Phase 3 新架构)', () => {
  test('完整研究流程', async ({ page }) => {
    // 1. 访问首页
    await page.goto('http://localhost:3000');

    // 2. 登录（如需要）
    // await page.click('text=登录');
    // ...

    // 3. 与 AI 对话，让 AI 建议研究
    await page.fill('[placeholder="输入消息..."]', 'Tell me about quantum computing');
    await page.click('button[type="submit"]');

    // 4. 等待 AI 响应（包含研究关键词）
    await page.waitForSelector('text=/can.*research/i', { timeout: 30000 });

    // 5. 验证 ResearchButton 显示（sticky 定位在聊天输入框上方）
    await page.waitForSelector('[data-testid="research-button"]');
    const button = page.locator('[data-testid="research-button"]');
    expect(await button.isVisible()).toBe(true);

    // 6. 点击 ResearchButton 发起研究
    await button.click();

    // 7. 验证 ResearchPanel 切换到 ResearchProgress
    await page.waitForSelector('[data-testid="research-progress"]');
    const progress = page.locator('[data-testid="research-progress"]');
    expect(await progress.isVisible()).toBe(true);

    // 8. 验证进度更新（检查 events 数组渲染）
    await page.waitForSelector('text=/Step.*\\/.*:/i');
    const steps = await page.locator('[data-testid="progress-step"]').count();
    expect(steps).toBeGreaterThan(0);

    // 9. 等待研究完成（status 变为 completed）
    await page.waitForSelector('[data-testid="research-completed"]', { timeout: 120000 });

    // 10. 验证 ResearchPanel 关闭
    await expect(progress).not.toBeVisible();

    // 11. 验证 Artifact 自动创建
    await page.waitForSelector('[data-testid="artifact"]');
    const artifact = page.locator('[data-testid="artifact"]');
    expect(await artifact.isVisible()).toBe(true);

    // 12. 验证报告内容
    const report = await artifact.textContent();
    expect(report).toContain('quantum');

    // 13. 追问更新报告
    await page.fill('[placeholder="输入消息..."]', 'Add more details about quantum entanglement');
    await page.click('button[type="submit"]');

    // 14. 验证报告更新
    await page.waitForSelector('text=/updated|entanglement/i', { timeout: 60000 });
  });
  
  test('错误处理', async ({ page }) => {
    // 模拟网络错误
    await page.route('**/api/research/stream', route => route.abort());
    
    await page.goto('http://localhost:3000');
    await page.fill('[placeholder="输入消息..."]', '测试错误');
    await page.click('button[type="submit"]');
    
    // 验证错误提示
    await page.waitForSelector('text=连接失败');
  });
});
```

### 3. 性能测试

#### 测试指标

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| 页面加载时间 | < 3 秒 | Lighthouse |
| API 响应时间 | < 2 秒 | curl + time |
| SSE 连接时间 | < 2 秒 | 浏览器 DevTools |
| 并发用户 | 5-10 人 | Apache Bench |
| 24 小时稳定性 | 无崩溃 | 监控日志 |

#### 性能测试脚本

```bash
#!/bin/bash

echo "⚡ 开始性能测试..."

# 1. 页面加载时间
echo "1️⃣ 测试页面加载时间..."
lighthouse https://your-app.vercel.app \
  --only-categories=performance \
  --output=json \
  --output-path=./lighthouse-report.json

# 2. API 响应时间
echo "2️⃣ 测试 API 响应时间..."
time curl https://research-backend.onrender.com/api/health

# 3. 并发测试
echo "3️⃣ 测试并发用户..."
ab -n 100 -c 10 https://research-backend.onrender.com/api/health

echo "✨ 性能测试完成！"
```

### 4. 兼容性测试

#### 测试矩阵

| 浏览器 | 桌面 | 移动 |
|--------|------|------|
| Chrome | ✅ | ✅ |
| Safari | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Edge | ✅ | - |

#### 测试清单

- [ ] Chrome 桌面版
- [ ] Chrome 移动版
- [ ] Safari 桌面版
- [ ] Safari 移动版（iOS）
- [ ] Firefox 桌面版
- [ ] Edge 桌面版

---

## 监控和日志

### 1. 监控设计

#### Render 监控

- CPU 使用率
- 内存使用率
- 请求数量
- 响应时间
- 错误率

#### Vercel Analytics

- 页面访问量
- 页面加载时间
- Core Web Vitals
- 地理分布

#### Neon 监控

- 连接数
- 查询性能
- 存储使用
- 备份状态

#### UptimeRobot（可选）

- 服务可用性
- 响应时间
- 告警通知

### 2. 日志设计

#### 日志级别

- **DEBUG**: 详细调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

#### 关键日志点

**后端（FastAPI）**:
```python
import logging

logger = logging.getLogger(__name__)

# 研究任务开始
logger.info(f"Research task started: {task_id}, topic: {topic}")

# 研究进度
logger.info(f"Research progress: {task_id}, step: {step}/{total}")

# 研究完成
logger.info(f"Research completed: {task_id}, duration: {duration}s")

# 错误
logger.error(f"Research failed: {task_id}, error: {error}")
```

**前端（Next.js）**:
```typescript
// lib/logger.ts
export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data);
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error);
  },
};

// 使用
logger.info('SSE connected', { taskId });
logger.error('SSE connection failed', error);
```

---

## 安全考虑

### 1. API Key 管理

- ✅ 使用环境变量
- ✅ 不提交到 Git
- ✅ 定期轮换
- ✅ 最小权限原则

### 2. 数据库安全

- ✅ 使用 SSL 连接
- ✅ 强密码
- ✅ 定期备份
- ✅ 访问控制

### 3. CORS 配置

- ✅ 只允许特定域名
- ✅ 不使用通配符 *
- ✅ 验证 Origin 头

### 4. 认证和授权

- ✅ 使用 NextAuth.js
- ✅ 安全的 session 管理
- ✅ CSRF 保护

### 5. 日志安全

- ✅ 不记录敏感信息
- ✅ 不记录完整 API Key
- ✅ 脱敏处理

---

## 成本分析

### 开发成本

| 项目 | 时间 | 成本 |
|------|------|------|
| 项目整理 | 1 天 | $500 |
| 本地联调 | 2 天 | $1,000 |
| 部署配置 | 2 天 | $1,000 |
| 测试验收 | 3 天 | $1,500 |
| **总计** | **8 天** | **$4,000** |

### 运营成本（月）

#### 免费方案

| 服务 | 计划 | 成本 |
|------|------|------|
| Vercel | Hobby | $0 |
| Render | Free | $0 |
| Neon | Free | $0 |
| cron-job.org | Free | $0 |
| DeepSeek API | - | ~$30 |
| OpenAI API | - | ~$20 |
| Tavily API | - | ~$10 |
| **总计** | - | **~$60/月** |

**限制**:
- Render 会休眠（需要防休眠）
- Neon 0.5GB 存储
- Vercel 100GB 带宽

#### 推荐方案

| 服务 | 计划 | 成本 |
|------|------|------|
| Vercel | Hobby | $0 |
| Render | Starter | $7 |
| Neon | Free | $0 |
| cron-job.org | - | $0 |
| API | - | ~$60 |
| **总计** | - | **~$67/月** |

**优点**:
- Render 不休眠
- 更好的性能
- 更稳定

#### 企业方案

| 服务 | 计划 | 成本 |
|------|------|------|
| Vercel | Pro | $20 |
| Render | Standard | $25 |
| Neon | Pro | $19 |
| API | - | ~$60 |
| **总计** | - | **~$124/月** |

---

## 部署检查清单

### 部署前

- [ ] 代码已提交到 GitHub
- [ ] 环境变量已配置
- [ ] 数据库已创建
- [ ] 本地联调测试通过
- [ ] 文档已更新

### 部署中

- [ ] Neon 数据库创建成功
- [ ] 数据库迁移执行成功
- [ ] Render 后端部署成功
- [ ] Vercel 前端部署成功
- [ ] CORS 配置正确
- [ ] 防休眠配置完成

### 部署后

- [ ] 健康检查通过
- [ ] 端到端测试通过
- [ ] 性能测试通过
- [ ] 兼容性测试通过
- [ ] 监控配置完成
- [ ] 文档已更新

---

## 回滚方案

### 代码回滚

```bash
# 1. 查看部署历史
git log --oneline

# 2. 回滚到上一版本
git revert HEAD

# 3. 推送
git push

# Render 和 Vercel 会自动重新部署
```

### 数据库回滚

```bash
# 1. 从 Neon 恢复备份
# 在 Neon 控制台选择备份点恢复

# 2. 或使用 pg_dump 备份
pg_dump $DATABASE_URL > backup.sql

# 3. 恢复
psql $DATABASE_URL < backup.sql
```

### 环境变量回滚

```bash
# 1. 在 Render 控制台恢复环境变量
# 2. 在 Vercel 控制台恢复环境变量
# 3. 重新部署
```

---

## 故障排查

### 常见问题

#### 1. Render 休眠

**症状**: 首次访问很慢（30-60 秒）

**解决**:
- 检查 cron-job.org 配置
- 考虑升级到 Starter 计划

#### 2. CORS 错误

**症状**: 前端无法访问后端 API

**解决**:
```python
# 检查 ALLOWED_ORIGINS 环境变量
# 确保包含 Vercel 域名
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

#### 3. 数据库连接失败

**症状**: 应用无法连接数据库

**解决**:
```bash
# 检查 DATABASE_URL
echo $DATABASE_URL

# 测试连接
psql $DATABASE_URL

# 确保包含 sslmode=require
```

#### 4. SSE 不工作

**症状**: 实时进度不显示

**解决**:
```typescript
// 确保使用 Node.js runtime
export const runtime = 'nodejs';

// 确保响应头正确
headers: {
  'X-Accel-Buffering': 'no',
  'Cache-Control': 'no-cache, no-transform',
}
```

---

**文档版本**: 1.0  
**最后更新**: 2025-10-30  
**状态**: 待实施
