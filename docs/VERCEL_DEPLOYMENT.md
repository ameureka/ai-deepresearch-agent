# Vercel 前端部署指南

## 概述

本指南详细说明如何将 AI DeepResearch Agent 前端部署到 Vercel 平台。Vercel 是 Next.js 的官方部署平台，提供零配置部署、全球 CDN 和自动 HTTPS。

## 📋 目录

- [为什么选择 Vercel](#为什么选择-vercel)
- [前置要求](#前置要求)
- [本地开发](#本地开发)
- [生产部署](#生产部署)
- [环境变量配置](#环境变量配置)
- [故障排查](#故障排查)

---

## 为什么选择 Vercel？

### ✅ 推荐理由

1. **零配置部署**
   - Next.js 原生支持
   - 自动检测构建配置
   - 无需 Dockerfile

2. **全球性能**
   - Edge Network CDN
   - 自动优化静态资源
   - 智能缓存策略

3. **开发体验**
   - GitHub 集成
   - 自动预览部署
   - 实时协作评论

4. **慷慨的免费层**
   - 无限部署次数
   - 100GB 带宽/月
   - 足够个人和小团队使用

### ❌ 不适用场景

- **后端 API 部署**
  - Serverless 函数有 10 秒超时限制
  - 不适合 FastAPI 长时间运行的任务
  - 后端应部署到 Render 或独立服务器

---

## 前置要求

### 必需

- **GitHub 账号** - 用于代码托管
- **Vercel 账号** - [注册](https://vercel.com/signup)
- **Next.js 项目** - ai-chatbot-main/

### 准备工作

1. **确保代码在 GitHub 上**
   ```bash
   git remote -v  # 检查远程仓库
   ```

2. **确认 next.config.ts 配置正确**
   ```typescript
   // ✅ 正确 - Vercel 不需要 standalone 输出
   const nextConfig: NextConfig = {
     experimental: {
       ppr: true,
     },
     // ❌ 不要添加 output: "standalone"
   };
   ```

3. **准备环境变量**
   - Neon 数据库连接字符串
   - 后端 API URL
   - AUTH_SECRET

---

## 本地开发

### 使用 Vercel Dev（推荐）

Vercel Dev 可以在本地模拟 Vercel 生产环境：

#### 1. 安装 Vercel CLI

```bash
npm i -g vercel
```

#### 2. 登录 Vercel

```bash
vercel login
```

#### 3. 链接项目

```bash
cd ai-chatbot-main
vercel link
```

按提示选择：
- 作用域（个人账号或团队）
- 是否链接到现有项目
- 项目名称

#### 4. 拉取环境变量（可选）

```bash
vercel env pull .env.local
```

这会从 Vercel 项目下载环境变量到本地 `.env.local`

#### 5. 启动开发服务器

```bash
# 方式 1: 使用 Next.js 开发服务器（推荐，更快）
npm run dev

# 方式 2: 使用 Vercel Dev（模拟生产环境）
vercel dev
```

访问: http://localhost:3000

### 配置本地环境变量

编辑 `ai-chatbot-main/.env.local`:

```bash
# 数据库（Neon 开发环境）
POSTGRES_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/dbname?sslmode=require

# 后端 API（本地 Python 运行）
RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# 认证
AUTH_SECRET=your-local-dev-secret-min-32-chars
AUTH_URL=http://localhost:3000/api/auth

# Vercel 服务（本地开发可选）
# BLOB_READ_WRITE_TOKEN=
# AI_GATEWAY_API_KEY=

# Node 环境
NODE_ENV=development
```

---

## 生产部署

### 方式一：通过 Vercel Dashboard（推荐新手）

#### 1. 登录 Vercel

访问 https://vercel.com/login

#### 2. 导入项目

1. 点击 "New Project"
2. 选择 GitHub 仓库
3. 选择 `ai-chatbot-main` 目录作为根目录

**重要设置：**
- **Framework Preset**: Next.js（自动检测）
- **Root Directory**: `ai-chatbot-main`
- **Build Command**: `npm run build`（默认）
- **Output Directory**: `.next`（默认）

#### 3. 配置环境变量

在部署前，点击 "Environment Variables" 添加：

```bash
# 必需变量
POSTGRES_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/dbname?sslmode=require
AUTH_SECRET=your-production-secret-min-32-chars
RESEARCH_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# 可选变量
BLOB_READ_WRITE_TOKEN=vercel_blob_xxx
AI_GATEWAY_API_KEY=vercel_ag_xxx
OPENAI_API_KEY=sk-proj-xxx
```

**注意**: 为每个环境设置变量：
- ✅ Production
- ✅ Preview
- ✅ Development

#### 4. 部署

点击 "Deploy" 开始首次部署

等待几分钟，Vercel 会：
- 克隆代码
- 安装依赖
- 构建 Next.js
- 部署到全球 CDN

#### 5. 访问应用

部署完成后，会得到：
- **生产 URL**: `https://your-app.vercel.app`
- **预览 URL**: `https://your-app-git-xxx.vercel.app`

### 方式二：通过 Vercel CLI（推荐开发者）

#### 1. 安装并登录

```bash
npm i -g vercel
vercel login
```

#### 2. 部署到预览环境

```bash
cd ai-chatbot-main
vercel
```

这会创建一个预览部署，用于测试

#### 3. 部署到生产环境

```bash
vercel --prod
```

#### 4. 查看部署状态

```bash
vercel ls
vercel inspect <deployment-url>
```

### 方式三：GitHub 集成（推荐团队）

#### 1. 连接 GitHub

在 Vercel Dashboard → Settings → Git：
- 连接 GitHub 账号
- 授权访问仓库

#### 2. 自动部署规则

Vercel 会自动：
- **生产部署**: 当推送到 `main` 分支
- **预览部署**: 当创建 Pull Request

#### 3. 推送代码

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel 会自动检测并部署

---

## 环境变量配置

### 必需环境变量

| 变量名 | 用途 | 示例 |
|--------|------|------|
| `POSTGRES_URL` | Neon 数据库连接 | `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require` |
| `AUTH_SECRET` | NextAuth 加密密钥 | 32+ 字符随机字符串 |
| `RESEARCH_API_URL` | 后端 API 地址（服务端） | `https://your-backend.com` |
| `NEXT_PUBLIC_API_URL` | 后端 API 地址（浏览器） | `https://your-backend.com` |

### 可选环境变量

| 变量名 | 用途 | 何时需要 |
|--------|------|----------|
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob 存储 | 如果使用文件上传功能 |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway | 如果使用 AI SDK |
| `OPENAI_API_KEY` | OpenAI API | 如果前端直接调用 OpenAI |
| `AUTH_URL` | 认证回调 URL | 生产环境会自动设置 |

### 设置环境变量

#### 通过 Dashboard

1. 访问项目 Settings → Environment Variables
2. 点击 "Add"
3. 输入变量名和值
4. 选择环境（Production / Preview / Development）
5. 点击 "Save"

#### 通过 CLI

```bash
# 添加生产环境变量
vercel env add POSTGRES_URL production

# 添加所有环境变量
vercel env add AUTH_SECRET

# 拉取到本地
vercel env pull .env.local
```

### 环境变量最佳实践

1. **使用不同的值**
   - 开发: `dev.neon.tech`
   - 生产: `prod.neon.tech`

2. **定期轮换密钥**
   - AUTH_SECRET 每 90 天更换
   - API Keys 定期检查权限

3. **不要提交到 Git**
   - `.env.local` 已在 .gitignore
   - 使用 .env.example 作为模板

---

## 部署后配置

### 1. 配置自定义域名

```bash
# 通过 CLI
vercel domains add your-domain.com

# 或在 Dashboard → Domains 添加
```

### 2. 更新后端 CORS

在后端 `.env` 中更新：

```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-domain.com
```

### 3. 配置 Vercel Analytics（可选）

在 Dashboard → Analytics 启用：
- Web Analytics
- Speed Insights

### 4. 启用预览评论（可选）

在 Dashboard → Settings → Comments：
- 启用 "Enable Comments on Preview Deployments"

---

## 故障排查

### 问题 1: 构建失败

**症状**: Build failed with error

**排查步骤**:

1. 检查构建日志
   ```bash
   vercel logs <deployment-url>
   ```

2. 常见原因:
   - ❌ 依赖安装失败 → 检查 package.json
   - ❌ TypeScript 错误 → 运行 `npm run build` 本地测试
   - ❌ 环境变量缺失 → 检查 Vercel Dashboard

3. 解决方法:
   ```bash
   # 本地测试构建
   npm run build

   # 检查 TypeScript
   npx tsc --noEmit
   ```

### 问题 2: API 请求失败 (CORS)

**症状**: CORS policy blocked

**解决方法**:

1. 更新后端 ALLOWED_ORIGINS
   ```bash
   # 后端 .env
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

2. 重启后端服务

3. 清除 Vercel 缓存
   ```bash
   vercel --force
   ```

### 问题 3: 环境变量未生效

**症状**: env variable is undefined

**解决方法**:

1. 检查变量名前缀
   ```bash
   # ✅ 浏览器可访问
   NEXT_PUBLIC_API_URL=xxx

   # ❌ 浏览器不可访问
   API_URL=xxx
   ```

2. 重新部署
   ```bash
   vercel --force --prod
   ```

3. 检查变量作用域
   - Production / Preview / Development

### 问题 4: 数据库连接失败

**症状**: database connection timeout

**解决方法**:

1. 检查 POSTGRES_URL 格式
   ```bash
   # ✅ 正确（包含 ?sslmode=require）
   postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

   # ❌ 错误（缺少 SSL）
   postgresql://user:pass@ep-xxx.neon.tech/db
   ```

2. 测试连接
   ```bash
   psql "$POSTGRES_URL" -c "SELECT 1"
   ```

3. 检查 Neon 数据库状态
   - 访问 Neon Dashboard
   - 确认数据库未暂停

### 问题 5: 部署很慢

**症状**: Build takes > 5 minutes

**优化方法**:

1. 启用缓存
   ```json
   // package.json
   {
     "scripts": {
       "build": "next build --experimental-build-cache"
     }
   }
   ```

2. 减少依赖
   - 移除未使用的包
   - 使用动态导入

3. 优化图片
   - 使用 Next.js Image 组件
   - 启用图片优化

---

## 监控和维护

### 查看部署日志

```bash
# 实时日志
vercel logs --follow

# 特定部署
vercel logs <deployment-url>
```

### 回滚部署

```bash
# 查看历史部署
vercel ls

# 回滚到特定版本
vercel rollback <deployment-url>
```

### 性能监控

1. 访问 Dashboard → Speed Insights
2. 查看：
   - Core Web Vitals
   - 页面加载时间
   - 用户体验得分

---

## 最佳实践

### 1. 分支策略

- `main` → 生产环境
- `dev` → 预览环境
- `feature/*` → 功能测试

### 2. 环境分离

- 开发: `.env.local`
- 预览: Vercel Preview
- 生产: Vercel Production

### 3. 安全检查

- ✅ 使用环境变量存储密钥
- ✅ 启用 HTTPS（Vercel 自动）
- ✅ 配置 CSP 头
- ✅ 定期更新依赖

### 4. 性能优化

- ✅ 使用 Image 组件
- ✅ 启用 ISR（增量静态再生）
- ✅ 实现代码分割
- ✅ 优化字体加载

---

## 相关资源

- [Vercel 官方文档](https://vercel.com/docs)
- [Next.js 部署指南](https://nextjs.org/docs/deployment)
- [环境变量指南](./ENVIRONMENT_VARIABLES.md)
- [数据库配置](./DATABASE_CONFIGURATION.md)
- [生产部署检查清单](./PRODUCTION_DEPLOYMENT.md)

---

**部署成功后，访问你的 Vercel 应用: `https://your-app.vercel.app` 🎉**
