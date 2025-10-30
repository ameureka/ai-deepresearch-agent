# 🚀 免费/低成本部署方案完整指南

## 📋 目标架构

将智能研究助手部署到云端：
- **前端**: Next.js（用户界面）
- **后端**: FastAPI + Python Agents（研究引擎）
- **数据库**: PostgreSQL（数据存储）

---

## 🆓 免费部署方案对比

### 1. Render.com ⭐⭐⭐⭐⭐ **最推荐**

**免费额度**:
- 750 小时/月免费（够用）
- 512MB RAM
- 自动休眠（15分钟无活动）
- 支持 Docker
- 免费 PostgreSQL（90天后删除数据）

**优点**:
- ✅ 完全免费
- ✅ 支持 Python/FastAPI
- ✅ 自动 HTTPS
- ✅ 简单易用
- ✅ GitHub 自动部署

**缺点**:
- ❌ 冷启动慢（30-60秒）
- ❌ 免费版会休眠

**适用场景**: 开发测试、小规模使用

---

### 2. Fly.io ⭐⭐⭐⭐⭐ **性能最好**

**免费额度**:
- 3个共享 CPU VM
- 256MB RAM × 3
- 160GB 出站流量/月
- 3GB 持久化存储
- 免费 PostgreSQL

**优点**:
- ✅ 不会自动休眠
- ✅ 全球边缘部署
- ✅ 启动快
- ✅ 支持 Docker

**缺点**:
- ❌ 需要信用卡验证
- ❌ 配置稍复杂

**适用场景**: 生产环境、需要稳定性

---

### 3. Vercel ⭐⭐⭐⭐⭐ **前端首选**

**免费额度**:
- 100GB 带宽/月
- 无限请求
- 自动 HTTPS
- 全球 CDN

**优点**:
- ✅ 部署 Next.js 最简单
- ✅ 自动 CI/CD
- ✅ 零配置
- ✅ 国内访问快

**缺点**:
- ❌ 不能部署 FastAPI（Serverless 函数有 10 秒限制）

**适用场景**: Next.js 前端部署

---

### 4. Cloudflare Pages ⭐⭐⭐⭐ **国内访问快**

**免费额度**:
- 无限带宽
- 无限请求
- 全球 CDN

**优点**:
- ✅ 完全免费
- ✅ 国内访问快
- ✅ 支持 Next.js

**缺点**:
- ❌ Workers 不支持长时间运行
- ❌ 不支持 Python

**适用场景**: Next.js 前端部署（国内用户）

---

### 5. Koyeb ⭐⭐⭐⭐

**免费额度**:
- 512MB RAM
- 2GB 存储
- 不休眠

**优点**:
- ✅ 免费且不休眠
- ✅ 支持 Docker
- ✅ 自动 HTTPS

**缺点**:
- ❌ 需要信用卡验证

**适用场景**: 替代 Render 的选择

---

### 6. Hugging Face Spaces ⭐⭐⭐

**免费额度**:
- 2 vCPU
- 16GB RAM
- 永久运行（不休眠）

**优点**:
- ✅ 完全免费
- ✅ 不休眠
- ✅ 适合 AI 应用

**缺点**:
- ❌ 主要面向 Gradio/Streamlit
- ❌ 需要适配

**适用场景**: AI 演示项目

---

### 7. Railway 💰 **付费但便宜**

**价格**:
- $5/月起
- 按使用量计费

**优点**:
- ✅ 最简单
- ✅ 不休眠
- ✅ 性能好
- ✅ 支持所有技术栈

**缺点**:
- ❌ 需要付费

**适用场景**: 愿意花钱省心

---

### 8. 阿里云/腾讯云 ⚠️ **不推荐**

**为什么不推荐**:
- ❌ 配置复杂
- ❌ 文档不友好
- ❌ 冷启动慢
- ❌ 研究任务太长会超时
- ❌ 需要实名认证

**适用场景**: 企业用户、国内合规要求

---

## 📊 详细对比表

| 服务 | 免费额度 | 休眠 | 国内访问 | 难度 | 推荐度 |
|------|---------|------|---------|------|--------|
| **Render** | 750h/月 | ✅ 会 | 慢 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Fly.io** | 3 VM | ❌ 不会 | 慢 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Vercel** | 100GB | ❌ 不会 | 快 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Cloudflare** | 无限 | ❌ 不会 | 快 | ⭐⭐ | ⭐⭐⭐⭐ |
| **Railway** | $5/月 | ❌ 不会 | 慢 | ⭐ | ⭐⭐⭐⭐ |
| **Koyeb** | 512MB | ❌ 不会 | 慢 | ⭐⭐ | ⭐⭐⭐⭐ |
| **HF Spaces** | 16GB | ❌ 不会 | 慢 | ⭐⭐⭐ | ⭐⭐⭐ |
| **阿里云** | 有限 | ✅ 会 | 快 | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 推荐部署方案

### 方案 A: 完全免费 ✅ **最推荐**

```
Next.js 前端 → Vercel (免费)
FastAPI 后端 → Render.com (免费)
PostgreSQL → Neon (免费)
```

**优点**:
- ✅ 完全免费
- ✅ 简单易用
- ✅ 自动部署

**缺点**:
- ❌ Render 会休眠（首次访问慢 30-60 秒）

**月成本**: $0

---

### 方案 B: 性能最优 ✅

```
Next.js 前端 → Vercel (免费)
FastAPI 后端 → Fly.io (免费，不休眠)
PostgreSQL → Neon (免费)
```

**优点**:
- ✅ 不休眠
- ✅ 启动快
- ✅ 全球部署

**缺点**:
- ❌ 需要信用卡验证

**月成本**: $0

---

### 方案 C: 国内访问优化 🇨🇳

```
Next.js 前端 → Cloudflare Pages (免费，国内快)
FastAPI 后端 → Render.com (免费)
PostgreSQL → Neon (免费)
```

**优点**:
- ✅ 国内访问快
- ✅ 完全免费

**缺点**:
- ❌ 后端会休眠

**月成本**: $0

---

### 方案 D: 付费稳定 💰

```
Next.js 前端 → Vercel (免费)
FastAPI 后端 → Railway ($5/月)
PostgreSQL → Neon (免费)
```

**优点**:
- ✅ 最省心
- ✅ 不休眠
- ✅ 性能好

**缺点**:
- ❌ 需要付费

**月成本**: $5

---

## 🚀 详细部署步骤

### 方案 A 实施：Vercel + Render + Neon

#### 步骤 1: 部署 Next.js 到 Vercel

1. **安装 Vercel CLI**:
```bash
npm i -g vercel
```

2. **部署**:
```bash
cd achive/ai-chatbot-main
vercel
```

3. **配置环境变量**:
```bash
vercel env add DATABASE_URL
vercel env add RESEARCH_API_URL
vercel env add NEXTAUTH_SECRET
```

4. **获得 URL**: `https://your-app.vercel.app`

---

#### 步骤 2: 部署 FastAPI 到 Render

1. **创建 `render.yaml`**:
```yaml
services:
  - type: web
    name: research-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
```

2. **在 Render 网站操作**:
   - 访问 https://render.com
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 选择项目根目录
   - Render 自动检测 Python
   - 添加环境变量
   - 点击 "Create Web Service"

3. **获得 URL**: `https://your-api.onrender.com`

---

#### 步骤 3: 创建 Neon 数据库

1. **访问 Neon**:
   - 打开 https://neon.tech
   - 注册免费账号
   - 点击 "Create Project"

2. **获取连接字符串**:
```
postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
```

3. **配置到两个服务**:
   - Vercel: `vercel env add DATABASE_URL`
   - Render: 在网站上添加环境变量

---

#### 步骤 4: 配置 Next.js 调用后端

在 Next.js 项目中创建 API 路由：

```typescript
// app/api/research/route.ts
export async function POST(req: Request) {
  const { prompt } = await req.json();
  
  const res = await fetch(process.env.RESEARCH_API_URL + '/generate_report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  
  return res.json();
}
```

---

#### 步骤 5: 避免 Render 休眠

**方法 1: 使用 Cron Job**

1. 访问 https://cron-job.org
2. 注册免费账号
3. 创建新任务:
   - URL: `https://your-api.onrender.com/health`
   - 间隔: 每 10 分钟
   - 方法: GET

**方法 2: 使用 Uptime Robot**

1. 访问 https://uptimerobot.com
2. 注册免费账号
3. 添加监控:
   - URL: `https://your-api.onrender.com/health`
   - 间隔: 5 分钟

**方法 3: 在 Next.js 中自动 ping**

```typescript
// app/api/keep-alive/route.ts
export async function GET() {
  await fetch(process.env.RESEARCH_API_URL + '/health');
  return Response.json({ ok: true });
}

// 在前端定期调用
useEffect(() => {
  const interval = setInterval(() => {
    fetch('/api/keep-alive');
  }, 5 * 60 * 1000); // 每 5 分钟
  
  return () => clearInterval(interval);
}, []);
```

---

### 方案 B 实施：Vercel + Fly.io + Neon

#### 步骤 1: 部署到 Fly.io

1. **安装 Fly CLI**:
```bash
curl -L https://fly.io/install.sh | sh
```

2. **登录**:
```bash
fly auth login
```

3. **初始化项目**:
```bash
cd /path/to/your/fastapi/project
fly launch
```

4. **配置 `fly.toml`**:
```toml
app = "research-api"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

5. **设置环境变量**:
```bash
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set OPENAI_API_KEY="sk-..."
fly secrets set TAVILY_API_KEY="tvly-..."
```

6. **部署**:
```bash
fly deploy
```

7. **获得 URL**: `https://research-api.fly.dev`

---

## 💰 成本对比

### 完全免费方案
```
Vercel: $0
Render: $0
Neon: $0
Cron Job: $0
---
总计: $0/月
```

### 付费稳定方案
```
Vercel: $0
Railway: $5
Neon: $0
---
总计: $5/月
```

### 企业方案
```
Vercel Pro: $20
Railway: $20
Neon Pro: $19
---
总计: $59/月
```

---

## 🔧 环境变量配置

### Next.js (Vercel)
```bash
DATABASE_URL=postgresql://...
RESEARCH_API_URL=https://your-api.onrender.com
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=https://your-app.vercel.app
```

### FastAPI (Render/Fly.io)
```bash
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
DEEPSEEK_API_KEY=sk-...  # 如果使用 DeepSeek
```

---

## 📋 部署检查清单

### 前端部署
- [ ] Next.js 项目推送到 GitHub
- [ ] Vercel 连接 GitHub 仓库
- [ ] 配置环境变量
- [ ] 部署成功
- [ ] 访问 URL 正常

### 后端部署
- [ ] FastAPI 项目推送到 GitHub
- [ ] Render/Fly.io 连接仓库
- [ ] 配置环境变量
- [ ] 部署成功
- [ ] API 端点正常响应

### 数据库配置
- [ ] Neon 数据库创建
- [ ] 获取连接字符串
- [ ] 配置到前后端
- [ ] 运行数据库迁移
- [ ] 测试连接

### 防休眠配置（如使用 Render）
- [ ] 设置 Cron Job 或 Uptime Robot
- [ ] 测试定期 ping
- [ ] 验证不再休眠

---

## 🐛 常见问题

### Q1: Render 部署失败？
**A**: 检查 `requirements.txt` 是否完整，确保包含所有依赖。

### Q2: Vercel 部署超时？
**A**: Next.js 构建时间过长，尝试优化依赖或升级到 Pro 计划。

### Q3: 数据库连接失败？
**A**: 检查连接字符串格式，确保包含 `?sslmode=require`。

### Q4: API 调用跨域错误？
**A**: 在 FastAPI 中添加 CORS 中间件：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q5: Render 冷启动太慢？
**A**: 使用 Cron Job 保持唤醒，或升级到付费计划。

---

## 🎯 最终推荐

**如果你在国内**:
```
前端: Cloudflare Pages
后端: Render.com + Cron Job
数据库: Neon
```

**如果你在海外**:
```
前端: Vercel
后端: Fly.io
数据库: Neon
```

**如果你愿意花 $5/月**:
```
前端: Vercel
后端: Railway
数据库: Neon
```

**我个人最推荐**: Vercel + Render + Neon + Cron Job
- 完全免费
- 简单易用
- 够用稳定

---

**创建日期**: 2025-01-XX  
**版本**: 1.0  
**状态**: ✅ 已完成
