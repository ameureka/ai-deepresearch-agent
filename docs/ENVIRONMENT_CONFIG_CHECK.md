# 环境配置检查清单

> 本地开发环境 vs 生产环境配置对比和检查

## 📋 目录

- [环境对比](#环境对比)
- [配置检查清单](#配置检查清单)
- [潜在冲突分析](#潜在冲突分析)
- [部署前检查](#部署前检查)
- [配置文件说明](#配置文件说明)

---

## 🔍 环境对比

### 架构对比

| 组件 | 本地开发 | 生产环境 |
|------|---------|---------|
| **前端** | `localhost:3000` | `https://your-app.vercel.app` |
| **后端** | `localhost:8000` | `https://api.ameureka.com` |
| **数据库** | 本地 PostgreSQL 或 Neon | Neon PostgreSQL |
| **HTTPS** | HTTP | HTTPS |
| **域名** | localhost | 真实域名 |

### 环境变量对比

#### 前端环境变量

| 变量名 | 本地开发 | 生产环境（Vercel） |
|--------|---------|-------------------|
| `POSTGRES_URL` | `postgresql://postgres:postgres@localhost:5432/ai_research` | `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require` |
| `RESEARCH_API_URL` | `http://localhost:8000` | `https://api.ameureka.com` |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | `https://api.ameureka.com` |
| `AUTH_SECRET` | 本地随机密钥 | 生产随机密钥（不同） |
| `AUTH_URL` | `http://localhost:3000/api/auth` | 自动设置（Vercel） |
| `NODE_ENV` | `development` | `production` |

#### 后端环境变量

| 变量名 | 本地开发 | 生产环境（腾讯云） |
|--------|---------|-------------------|
| `DATABASE_URL` | 本地 PostgreSQL 或 Neon | Neon PostgreSQL |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | `https://your-app.vercel.app,https://*.vercel.app` |
| `HOST` | `0.0.0.0` | `0.0.0.0` |
| `PORT` | `8000` | `8000` |
| `ENV` | `development` | `production` |

---

## ✅ 配置检查清单

### 1. 前端配置检查

#### ✅ next.config.ts

**当前配置**：
```typescript
const nextConfig: NextConfig = {
  experimental: {
    ppr: true,
  },
  images: {
    remotePatterns: [
      {
        hostname: "avatar.vercel.sh",
      },
    ],
  },
};
```

**检查项**：
- ✅ **没有** `output: "standalone"`（Vercel 不需要）
- ✅ 使用 `experimental.ppr`（Vercel 支持）
- ✅ 图片优化配置正确

**结论**：✅ 配置正确，无需修改

---

#### ✅ package.json

**构建命令**：
```json
{
  "scripts": {
    "build": "tsx lib/db/migrate && next build"
  }
}
```

**检查项**：
- ✅ 构建前会运行数据库迁移
- ✅ 使用标准的 `next build`
- ✅ Vercel 会自动识别

**结论**：✅ 配置正确，无需修改

---

#### ⚠️ 环境变量

**本地开发（.env.local）**：
```bash
RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/ai_research
```

**生产环境（Vercel）**：
```bash
RESEARCH_API_URL=https://api.ameureka.com
NEXT_PUBLIC_API_URL=https://api.ameureka.com
POSTGRES_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
```

**检查项**：
- ⚠️ 本地和生产环境的 API URL 不同
- ⚠️ 本地和生产环境的数据库不同
- ✅ 代码中有默认值处理

**代码检查**：
```typescript
// app/(chat)/api/research/stream/route.ts
const researchApiUrl =
  process.env.RESEARCH_API_URL || "http://localhost:8000";
```

**结论**：✅ 代码有默认值，但 Vercel 必须配置正确的环境变量

---

### 2. 后端配置检查

#### ✅ CORS 配置

**代码位置**：`main.py`

```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://*.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**检查项**：
- ✅ 默认包含 `http://localhost:3000`（本地开发）
- ✅ 默认包含 `https://*.vercel.app`（Vercel 预览）
- ⚠️ 需要添加生产域名

**需要更新**：
```bash
# 在服务器上
nano /opt/agentic-ai/.env

# 添加 Vercel 生产域名
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000
```

**结论**：⚠️ 部署后需要更新 CORS 配置

---

### 3. 数据库配置检查

#### ✅ 数据库迁移

**构建命令**：
```json
"build": "tsx lib/db/migrate && next build"
```

**检查项**：
- ✅ Vercel 构建时会自动运行迁移
- ✅ 使用 Drizzle ORM
- ✅ 迁移文件在 `lib/db/migrations/`

**结论**：✅ 配置正确，Vercel 会自动处理

---

## ⚠️ 潜在冲突分析

### 冲突 1: API URL 硬编码

**风险等级**：🟢 低

**分析**：
- 代码中使用环境变量 `RESEARCH_API_URL` 和 `NEXT_PUBLIC_API_URL`
- 有默认值 `http://localhost:8000`
- Vercel 会使用配置的环境变量

**解决方案**：
- ✅ 在 Vercel 正确配置环境变量即可
- ✅ 无需修改代码

---

### 冲突 2: CORS 配置

**风险等级**：🟡 中

**分析**：
- 后端默认 CORS 包含 `https://*.vercel.app`
- 但不包含具体的生产域名
- 部署后可能出现 CORS 错误

**解决方案**：
- ⚠️ 部署 Vercel 后，立即更新后端 CORS 配置
- ⚠️ 添加 Vercel 生产域名到 `ALLOWED_ORIGINS`

**操作步骤**：
```bash
# 1. 部署 Vercel，获取域名
# 例如：https://ai-deepresearch-agent-xxx.vercel.app

# 2. SSH 登录服务器
ssh root@43.163.110.53

# 3. 更新 CORS 配置
nano /opt/agentic-ai/.env

# 4. 添加域名
ALLOWED_ORIGINS=https://ai-deepresearch-agent-xxx.vercel.app,https://*.vercel.app,http://localhost:3000

# 5. 重启服务
sudo systemctl restart agentic-backend
```

---

### 冲突 3: 数据库连接

**风险等级**：🟢 低

**分析**：
- 本地可能使用本地 PostgreSQL
- 生产使用 Neon PostgreSQL
- 通过环境变量区分

**解决方案**：
- ✅ 在 Vercel 配置正确的 `POSTGRES_URL`
- ✅ 确保包含 `?sslmode=require`

---

### 冲突 4: HTTPS vs HTTP

**风险等级**：🟢 低

**分析**：
- 本地开发使用 HTTP
- 生产环境使用 HTTPS
- 浏览器可能阻止混合内容

**解决方案**：
- ✅ 后端已配置 Cloudflare Tunnel（HTTPS）
- ✅ 前端部署在 Vercel（HTTPS）
- ✅ 全程 HTTPS，无混合内容问题

---

## 📝 部署前检查

### 检查清单

#### 前端（Vercel）

- [ ] **代码已推送到 GitHub**
  ```bash
  git status
  git push origin main
  ```

- [ ] **环境变量已准备**
  - [ ] `POSTGRES_URL`（Neon 连接字符串）
  - [ ] `RESEARCH_API_URL`（`https://api.ameureka.com`）
  - [ ] `NEXT_PUBLIC_API_URL`（`https://api.ameureka.com`）
  - [ ] `AUTH_SECRET`（已生成随机密钥）
  - [ ] `NODE_ENV=production`

- [ ] **配置文件检查**
  - [ ] `next.config.ts` 无 `output: "standalone"`
  - [ ] `package.json` 构建命令正确
  - [ ] 无硬编码的 localhost 地址

#### 后端（腾讯云）

- [ ] **服务正常运行**
  ```bash
  sudo systemctl status agentic-backend
  curl http://localhost:8000/health
  ```

- [ ] **Cloudflare Tunnel 正常**
  ```bash
  sudo systemctl status cloudflared
  curl https://api.ameureka.com/health
  ```

- [ ] **CORS 配置准备**
  - [ ] 知道如何更新 CORS 配置
  - [ ] 准备好 Vercel 域名（部署后获取）

#### 数据库（Neon）

- [ ] **数据库可访问**
  ```bash
  psql "postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require"
  ```

- [ ] **连接字符串包含 SSL**
  - [ ] 包含 `?sslmode=require`

---

## 📚 配置文件说明

### 1. next.config.ts

**作用**：Next.js 配置文件

**关键配置**：
- `experimental.ppr`：启用部分预渲染
- `images.remotePatterns`：允许的图片域名

**Vercel 特殊说明**：
- ❌ 不要使用 `output: "standalone"`
- ✅ Vercel 会自动优化构建

---

### 2. package.json

**作用**：项目依赖和脚本

**关键脚本**：
- `build`：构建命令（Vercel 会自动调用）
- `start`：启动命令（Vercel 不使用）
- `dev`：本地开发命令

**Vercel 特殊说明**：
- ✅ Vercel 会自动检测 `build` 脚本
- ✅ 会自动运行数据库迁移

---

### 3. .env.local (本地)

**作用**：本地开发环境变量

**特点**：
- ✅ 不会提交到 Git
- ✅ 仅本地使用
- ✅ 不影响生产环境

---

### 4. Vercel 环境变量

**作用**：生产环境配置

**特点**：
- ✅ 在 Vercel 控制台配置
- ✅ 构建时注入
- ✅ 可以区分 Production/Preview/Development

---

## 🎯 部署流程建议

### 推荐流程

1. **检查本地代码**
   ```bash
   # 确保代码最新
   git status
   git pull origin main
   
   # 检查构建
   cd ai-chatbot-main
   pnpm build
   ```

2. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "准备部署到 Vercel"
   git push origin main
   ```

3. **部署到 Vercel**
   - 按照 [Vercel 部署指南](./VERCEL_DEPLOYMENT_GUIDE.md) 操作
   - 配置所有环境变量
   - 点击 Deploy

4. **获取 Vercel 域名**
   - 例如：`https://ai-deepresearch-agent-xxx.vercel.app`

5. **更新后端 CORS**
   ```bash
   ssh root@43.163.110.53
   nano /opt/agentic-ai/.env
   # 添加 Vercel 域名到 ALLOWED_ORIGINS
   sudo systemctl restart agentic-backend
   ```

6. **测试完整流程**
   - 访问 Vercel 域名
   - 注册/登录
   - 测试研究功能

---

## 🔧 快速命令

### 检查本地配置

```bash
# 检查环境变量
cat ai-chatbot-main/.env.local

# 检查 Next.js 配置
cat ai-chatbot-main/next.config.ts

# 检查构建
cd ai-chatbot-main && pnpm build
```

### 检查服务器配置

```bash
# SSH 登录
ssh root@43.163.110.53

# 检查后端环境变量
cat /opt/agentic-ai/.env | grep ALLOWED_ORIGINS

# 检查服务状态
sudo systemctl status agentic-backend
sudo systemctl status cloudflared

# 测试 API
curl http://localhost:8000/health
curl https://api.ameureka.com/health
```

---

## 📖 相关文档

- [Vercel 部署指南](./VERCEL_DEPLOYMENT_GUIDE.md)
- [腾讯云部署指南](./TENCENT_CLOUD_DEPLOYMENT.md)
- [Cloudflare Tunnel 配置](./CLOUDFLARE_TUNNEL_SETUP.md)
- [环境变量配置](./ENVIRONMENT_VARIABLES.md)

---

**文档版本**: v1.0.0  
**最后更新**: 2025-11-03  
**适用版本**: v3.2.0+

---

**Made with ❤️ by the AI DeepResearch Team**
