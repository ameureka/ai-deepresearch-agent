# Environment Variables Configuration Guide

## Overview

This document provides a comprehensive guide to configuring environment variables for the AI DeepResearch Agent project across different environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Backend Variables](#backend-variables)
- [Frontend Variables](#frontend-variables)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Backend Configuration

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env

# Or use the detailed template
cp .env.backend .env
```

### 2. Frontend Configuration

```bash
# Navigate to frontend
cd ai-chatbot-main

# Copy example file
cp .env.local.example .env.local

# Edit with your values
nano .env.local
```

### 3. Validate Configuration

```bash
# Run validation script
./scripts/check-env.sh
```

---

## Backend Variables

**适用场景：** Python 直接运行（推荐）或 Docker 运行（可选）

### Required Variables

These variables MUST be configured for the application to function:

#### API Keys

| Variable | Description | Where to Get | Example |
|----------|-------------|--------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek AI API key | [DeepSeek Platform](https://platform.deepseek.com/) | `sk-xxxxxxxx` |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | [OpenAI Platform](https://platform.openai.com/) | `sk-proj-xxxxxxxx` |
| `TAVILY_API_KEY` | Tavily Search API key | [Tavily](https://tavily.com/) | `tvly-xxxxxxxx` |

#### Database

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (推荐使用 Neon) | `postgresql://user:pass@host:5432/dbname` |

### Optional Variables

These variables have default values but can be customized:

#### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `WORKERS` | `1` | Number of uvicorn workers |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |

#### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed origins |

#### Model Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PLANNER_MODEL` | `deepseek:deepseek-reasoner` | Planner agent model |
| `RESEARCHER_MODEL` | `deepseek:deepseek-chat` | Researcher agent model |
| `WRITER_MODEL` | `deepseek:deepseek-chat` | Writer agent model |
| `EDITOR_MODEL` | `deepseek:deepseek-chat` | Editor agent model |
| `FALLBACK_MODEL` | `openai:gpt-4o-mini` | Fallback model on error |

#### Context Management (Phase 1.5)

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CHUNKING` | `true` | Enable text chunking for long documents |
| `CHUNKING_THRESHOLD` | `0.8` | Trigger chunking at 80% of context window |
| `MAX_CHUNK_SIZE` | `6000` | Maximum tokens per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks for context |

#### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_COST_TRACKING` | `true` | Track API costs |
| `ENABLE_FALLBACK` | `true` | Enable fallback mechanism |

---

## Vercel 环境变量配置

**适用场景：** 前端部署到 Vercel（本地 `npm run dev` 和生产环境）

### 本地开发（Vercel Dev）

配置文件位置：`ai-chatbot-main/.env.local`

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_URL` | PostgreSQL connection string（推荐使用 Neon 开发数据库） | `postgresql://user:pass@ep-xxx-dev.neon.tech/dev_db?sslmode=require` |
| `AUTH_SECRET` | Random secret key for auth | Generate: `openssl rand -base64 32` |

#### Backend API Connection

| Variable | Default | Description |
|----------|---------|-------------|
| `RESEARCH_API_URL` | `http://localhost:8000` | FastAPI backend URL (server-side) |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Public API URL (browser-side) |

#### Optional Features

| Variable | Description |
|----------|-------------|
| `NODE_ENV` | Node environment (development) |
| `NEXTAUTH_URL` | Auth callback URL (http://localhost:3000) |

**示例配置文件 `ai-chatbot-main/.env.local`：**

```bash
# Database (Neon - 开发数据库)
POSTGRES_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/dev_db?sslmode=require

# Auth
AUTH_SECRET=your-generated-secret-here
NEXTAUTH_URL=http://localhost:3000

# Backend API (本地 Python 后端)
RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Development
NODE_ENV=development
```

**重要说明：**
- 本地开发和生产环境都使用 Neon 数据库
- 使用不同的 Neon 数据库：开发环境和生产环境分开
- 后端 API 本地开发时指向 `http://localhost:8000`（Python 直接运行）

### Vercel 生产环境配置

在 Vercel Dashboard 中配置环境变量：
**Vercel Dashboard → Project → Settings → Environment Variables**

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_URL` | PostgreSQL connection string（使用 Neon 生产数据库） | `postgresql://user:pass@ep-xxx-prod.neon.tech/prod_db?sslmode=require` |
| `AUTH_SECRET` | Random secret key for auth（与开发环境不同） | Generate new: `openssl rand -base64 32` |
| `AUTH_URL` | Auth callback URL | `https://your-app.vercel.app/api/auth` |

#### Backend API Connection

| Variable | Description | Example |
|----------|-------------|---------|
| `RESEARCH_API_URL` | FastAPI backend URL (server-side) | `https://your-backend.onrender.com` |
| `NEXT_PUBLIC_API_URL` | Public API URL (browser-side) | `https://your-backend.onrender.com` |

#### Optional Vercel Services

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob storage token | [Vercel Dashboard](https://vercel.com/docs/storage/vercel-blob) |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway key | [Vercel Dashboard](https://vercel.com/ai-gateway) |

#### Optional Features

| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Redis connection string for rate limiting |
| `OPENAI_API_KEY` | OpenAI key for frontend AI features |
| `NODE_ENV` | Node environment (production) |

**配置步骤：**

1. 登录 Vercel Dashboard
2. 选择项目 → Settings → Environment Variables
3. 添加以下环境变量（每个环境都需要配置）：
   - Production
   - Preview (可选)
   - Development (可选，通常使用本地 .env.local)

**重要说明：**
- 生产环境使用 Neon 生产数据库（与开发环境分开）
- 后端 API 指向 Render 或其他云服务部署的 Python 后端
- 所有敏感信息都通过 Vercel Dashboard 配置，不要提交到代码库

---

## Environment-Specific Configuration

### Local Development

**推荐架构：**
- Frontend: Vercel (本地 `npm run dev`)
- Backend: Python 直接运行（推荐）
- Database: Neon SaaS（开发数据库）

#### Terminal 1: Backend (.env)

```bash
# API Keys
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key

# Database (推荐使用 Neon 开发数据库)
DATABASE_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/dev_db?sslmode=require

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Development settings
LOG_LEVEL=DEBUG
ENV=development
```

#### Terminal 2: Frontend (ai-chatbot-main/.env.local)

```bash
# Database (推荐使用 Neon 开发数据库，与后端相同)
POSTGRES_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/dev_db?sslmode=require

# Auth
AUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://localhost:3000

# Research API (连接到本地 Python 后端)
RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional Vercel services (leave empty for local dev)
# BLOB_READ_WRITE_TOKEN=
# AI_GATEWAY_API_KEY=

# Development
NODE_ENV=development
```

**重要说明：**
- 本地和生产环境都使用 Neon 数据库（不同数据库实例）
- Backend 推荐 Python 直接运行，Docker 为可选方式
- 前后端使用相同的 Neon 开发数据库连接字符串

### Docker Compose（可选）

**注意：** Docker 部署为可选方式，推荐使用 Python 直接运行后端

Environment variables are defined in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      # 可以使用 Neon 或本地 PostgreSQL
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/ai_research
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      TAVILY_API_KEY: ${TAVILY_API_KEY}

  frontend:
    environment:
      POSTGRES_URL: postgresql://postgres:postgres@postgres:5432/ai_research
      AUTH_SECRET: ${AUTH_SECRET}
      RESEARCH_API_URL: http://backend:8000
```

### Production (Render + Vercel + Neon)

**推荐架构：**
- Frontend: Vercel (生产部署)
- Backend: Python on Render（推荐）或 Docker（可选）
- Database: Neon SaaS（生产数据库，与开发数据库分离）

#### Render (Backend)

Set in Render dashboard → Environment:

```bash
# API Keys
DEEPSEEK_API_KEY=sk-your-key
OPENAI_API_KEY=sk-your-key
TAVILY_API_KEY=tvly-your-key

# Database (Neon 生产数据库)
DATABASE_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/prod_db?sslmode=require

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=2

# CORS (allow your Vercel frontend)
ALLOWED_ORIGINS=https://your-app.vercel.app

# Production settings
ENV=production
LOG_LEVEL=INFO
```

**重要说明：**
- 使用 Neon 生产数据库（与开发环境分离）
- Backend 推荐 Python 直接运行，Docker 为可选方式
- CORS 必须配置 Vercel 前端域名

#### Vercel (Frontend)

Set in Vercel project → Settings → Environment Variables:

```bash
# Database (Neon 生产数据库，与后端相同)
POSTGRES_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/prod_db?sslmode=require

# Auth
AUTH_SECRET=<your-random-secret>
AUTH_URL=https://your-app.vercel.app/api/auth

# Research API (Render backend)
RESEARCH_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# Vercel services
BLOB_READ_WRITE_TOKEN=<from-vercel>
AI_GATEWAY_API_KEY=<from-vercel>

# Production
NODE_ENV=production
```

**重要说明：**
- 前后端使用相同的 Neon 生产数据库
- 必须使用不同的 AUTH_SECRET（与开发环境分离）
- Research API URLs 指向 Render 部署的后端

---

## Validation

### Automatic Validation

Run the validation script to check all environment variables:

```bash
./scripts/check-env.sh
```

Output:
```
🔍 Checking environment variables configuration...

📦 Checking backend environment variables...
✅ Configured: DEEPSEEK_API_KEY = sk-xxxxx...
✅ Configured: OPENAI_API_KEY = sk-xxxxx...
✅ Configured: TAVILY_API_KEY = tvly-xxxx...
✅ Configured: DATABASE_URL = postgresql...

🎨 Checking frontend environment variables...
✅ Configured: POSTGRES_URL = postgresql...
✅ Configured: AUTH_SECRET = xxxxxxxxx...

📊 Summary:
   - Configured: 15
   - Missing: 0

✨ All required environment variables are configured!
```

### Manual Validation

#### Test Backend

```bash
python -c "
from src.config import get_config
config = get_config()
print(f'✅ Backend config loaded')
print(f'   - DeepSeek Key: {config.deepseek_api_key[:10]}...')
print(f'   - Database: {config.database_url.split('@')[1]}')
"
```

#### Test Frontend

```bash
cd ai-chatbot-main
node -e "
console.log('✅ Frontend config loaded');
console.log('   - Database:', process.env.POSTGRES_URL?.split('@')[1]);
console.log('   - API URL:', process.env.RESEARCH_API_URL);
"
```

---

## Troubleshooting

### Problem: "Missing environment variable"

**Solution:**
1. Check if `.env` (backend) or `.env.local` (frontend) exists
2. Verify the variable name matches exactly
3. Ensure no extra spaces around `=`
4. Reload environment: `source .env`

### Problem: "Connection refused" (Database)

**Solution:**
1. Check DATABASE_URL format: `postgresql://user:pass@host:port/dbname`
2. For Neon, add `?sslmode=require`
3. Test connection:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

### Problem: "Invalid API key"

**Solution:**
1. Verify key format:
   - DeepSeek: starts with `sk-`
   - OpenAI: starts with `sk-` or `sk-proj-`
   - Tavily: starts with `tvly-`
2. Check for extra quotes or spaces
3. Regenerate key if needed

### Problem: "CORS error"

**Solution:**
1. Add frontend URL to `ALLOWED_ORIGINS`:
   ```bash
   ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app
   ```
2. Restart backend server
3. Clear browser cache

### Problem: Variables not loading in Docker

**Solution:**
1. Use `.env` file in project root for docker-compose
2. Pass variables with `--env-file .env`
3. Check docker-compose.yml for `${VARIABLE}` syntax

---

## Best Practices

1. **Never commit `.env` or `.env.local`** - They are in `.gitignore`
2. **Use `.env.example` for documentation** - Show what variables are needed
3. **Rotate secrets regularly** - Especially API keys and AUTH_SECRET
4. **Use different keys for dev/prod** - Don't mix environments
5. **Enable SSL for production databases** - Always use `?sslmode=require` with Neon
6. **Validate before deployment** - Run `check-env.sh`
7. **Document custom variables** - Add to this guide
8. **Use environment-specific files** - `.env.development`, `.env.production`

---

## References

- [DeepSeek API Docs](https://platform.deepseek.com/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Tavily API Docs](https://docs.tavily.com/)
- [Neon Database Docs](https://neon.tech/docs)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
- [Render Environment Variables](https://render.com/docs/environment-variables)
