# Database Configuration Guide

## Overview

This guide explains how to configure the PostgreSQL database for different environments in the AI DeepResearch Agent project.

## 推荐配置：Neon（本地和生产统一）

**强烈推荐使用 Neon 作为主要数据库方案**

### 为什么选择 Neon？

1. **环境一致性**
   - 本地开发和生产环境使用相同的数据库类型
   - 避免本地 PostgreSQL 和云端 PostgreSQL 的配置差异
   - 减少环境不一致导致的问题

2. **零本地配置**
   - 无需安装和配置本地 PostgreSQL
   - 无需管理 Docker 容器
   - 开箱即用，专注于开发

3. **免费额度充足**
   - 0.5GB 存储空间
   - 191 小时/月的计算时间
   - 对于开发和小型项目完全够用

4. **生产级功能**
   - 自动备份和恢复
   - 高可用性
   - 自动扩展
   - 内置监控

5. **开发体验优秀**
   - Web 控制台管理
   - 一键创建多个数据库（dev/staging/prod）
   - 实时查询编辑器
   - 连接池管理

### Neon 配置步骤

#### 1. 注册 Neon 账号

访问 [https://neon.tech](https://neon.tech) 并注册账号

#### 2. 创建开发数据库

1. 登录 Neon Console
2. 点击 "Create Project"
3. 配置项目：
   - **Project Name**: `ai-research-dev` (开发环境)
   - **Region**: 选择最近的区域（如 AWS US East）
   - **PostgreSQL Version**: 15 或更高
4. 创建完成后，复制连接字符串

**开发数据库配置示例：**

```bash
# .env (Backend)
DATABASE_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/neondb?sslmode=require

# ai-chatbot-main/.env.local (Frontend)
POSTGRES_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/neondb?sslmode=require
```

#### 3. 创建生产数据库

1. 在 Neon Console 中创建新项目
2. 配置项目：
   - **Project Name**: `ai-research-prod` (生产环境)
   - **Region**: 选择与部署服务器最近的区域
   - **PostgreSQL Version**: 15 或更高
3. 创建完成后，复制连接字符串

**生产数据库配置示例：**

```bash
# Render Backend Environment Variables
DATABASE_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/neondb?sslmode=require

# Vercel Frontend Environment Variables
POSTGRES_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/neondb?sslmode=require
```

#### 4. 数据库初始化

**后端表初始化（FastAPI）：**

后端会在启动时自动创建表：

```bash
# 启动后端会自动初始化表
python -m uvicorn main:app --reload
```

**前端表初始化（Next.js）：**

```bash
cd ai-chatbot-main

# 推送 schema 到数据库（开发环境）
npm run db:push

# 或使用迁移（生产环境推荐）
npm run db:generate
npm run db:migrate
```

#### 5. 验证连接

**测试后端连接：**

```bash
python -c "
import psycopg2
from os import getenv
conn = psycopg2.connect(getenv('DATABASE_URL'))
print('✅ Backend database connection successful!')
conn.close()
"
```

**测试前端连接：**

```bash
cd ai-chatbot-main
node -e "
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.POSTGRES_URL });
pool.query('SELECT NOW()', (err, res) => {
  if (err) console.error('❌ Failed:', err);
  else console.log('✅ Frontend database connection successful!');
  pool.end();
});
"
```

### Neon 最佳实践

1. **使用独立数据库实例**
   - 开发环境：`ai-research-dev`
   - 生产环境：`ai-research-prod`
   - 测试环境（可选）：`ai-research-test`

2. **启用自动备份**
   - 在 Neon Console → Settings → Backups
   - 生产环境建议启用

3. **监控使用量**
   - 定期检查存储和计算时间使用情况
   - 接近限额时考虑升级计划

4. **连接池配置**
   - Neon 自动管理连接池
   - 对于高并发应用，考虑使用连接池代理

5. **SSL 连接**
   - 始终使用 `?sslmode=require`
   - 保证数据传输安全

---

## Database Options

**注意：** 以下选项不推荐用于日常开发，仅作为参考

### Option 1: Local PostgreSQL (Development) - 不推荐

**注意：** 不推荐使用本地 PostgreSQL，推荐使用 Neon 以保持环境一致性

**Pros:**
- ✅ Fast and offline
- ✅ No external dependencies
- ✅ Free

**Cons:**
- ❌ Requires local installation
- ❌ Manual setup needed
- ❌ 与生产环境配置不一致
- ❌ 需要额外的维护和管理

**Setup:**

```bash
# macOS (Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
psql postgres -c "CREATE DATABASE ai_research;"
psql postgres -c "CREATE USER postgres WITH PASSWORD 'postgres';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_research TO postgres;"

# Connection string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
```

### Option 2: Docker PostgreSQL (Development) - 不推荐

**注意：** 不推荐使用 Docker PostgreSQL，推荐使用 Neon 以简化配置

**Pros:**
- ✅ Easy setup
- ✅ Consistent environment
- ✅ No local installation needed

**Cons:**
- ❌ Requires Docker
- ❌ Resource overhead
- ❌ 与生产环境配置不一致
- ❌ 需要管理 Docker 容器

**Setup:**

```bash
# Using docker-compose (recommended)
docker-compose up -d postgres

# Or standalone container
docker run -d \
  --name ai-research-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_research \
  -p 5432:5432 \
  postgres:15

# Connection string
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
```

### Option 3: Neon PostgreSQL - 推荐 ⭐

**这是推荐的主要方案，详细配置请参考本文档开头的"推荐配置：Neon（本地和生产统一）"章节**

**Pros:**
- ✅ Serverless (auto-scale)
- ✅ Free tier available (0.5GB storage, 191 compute hours/month)
- ✅ Built-in backups
- ✅ No maintenance
- ✅ 本地和生产环境一致
- ✅ 零本地配置
- ✅ 生产级功能

**Cons:**
- ❌ Requires internet connection
- ❌ Cold start latency (~1s for first query after idle)

**快速配置：**

1. Sign up at https://neon.tech
2. Create development project: `ai-research-dev`
3. Create production project: `ai-research-prod`
4. Copy connection strings to environment variables

```bash
# Development
DATABASE_URL=postgresql://user:password@ep-xxx-dev.neon.tech/neondb?sslmode=require

# Production
DATABASE_URL=postgresql://user:password@ep-xxx-prod.neon.tech/neondb?sslmode=require
```

**详细步骤请参考本文档开头的完整 Neon 配置指南**

## Environment-Specific Configuration

### Local Development (.env)

**推荐配置（使用 Neon）：**

```bash
# 推荐：使用 Neon 开发数据库
DATABASE_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/neondb?sslmode=require
```

**其他选项（不推荐）：**

```bash
# Option 1: Local PostgreSQL（不推荐）
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research

# Option 2: Docker PostgreSQL（不推荐）
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
```

### Docker Compose (docker-compose.yml) - 可选

**注意：** Docker 部署为可选方式，推荐使用 Python 直接运行后端

The backend service automatically uses the `postgres` service hostname:

```yaml
environment:
  # 可以使用 Docker PostgreSQL 或 Neon
  DATABASE_URL: postgresql://postgres:postgres@postgres:5432/ai_research

  # 或使用 Neon（推荐）
  DATABASE_URL: postgresql://user:pass@ep-xxx-dev.neon.tech/neondb?sslmode=require
```

### Production (Render Backend)

**推荐：使用 Neon 生产数据库**

Set as environment variable in Render dashboard:

```bash
# Neon 生产数据库（推荐）
DATABASE_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/neondb?sslmode=require
```

### Production (Vercel Frontend)

**推荐：使用 Neon 生产数据库（与后端相同）**

Set in Vercel project settings (Settings → Environment Variables):

```bash
# Neon 生产数据库（推荐，与后端相同）
POSTGRES_URL=postgresql://user:pass@ep-xxx-prod.neon.tech/neondb?sslmode=require
```

## Database Schema

The application uses the following tables:

### Backend (FastAPI)

- `tasks` - Research task tracking
- `task_progress` - Progress events
- `cost_records` - API cost tracking

### Frontend (Next.js)

- `User` - User accounts (via Auth.js)
- `Chat` - Chat conversations
- `Message` - Chat messages
- `Vote` - Message votes
- `Document` - Saved documents

## Migration & Initialization

### Backend Initialization

The FastAPI backend automatically creates tables on startup via SQLAlchemy:

```python
# In main.py
@app.on_event("startup")
async def startup():
    await init_database()  # Creates tables if not exist
```

### Frontend Initialization

The Next.js frontend uses Drizzle ORM with migrations:

```bash
cd ai-chatbot-main

# Generate migration
npm run db:generate

# Apply migration
npm run db:migrate

# Push schema (development)
npm run db:push
```

## Connection Testing

### Test Backend Connection

```bash
# Using Python
python -c "
import psycopg2
from os import getenv

conn = psycopg2.connect(getenv('DATABASE_URL'))
print('✅ Backend database connection successful!')
conn.close()
"
```

### Test Frontend Connection

```bash
cd ai-chatbot-main

# Using Node.js
node -e "
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.POSTGRES_URL });

pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('❌ Frontend database connection failed:', err);
  } else {
    console.log('✅ Frontend database connection successful!', res.rows[0]);
  }
  pool.end();
});
"
```

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check Docker container
docker ps | grep postgres

# Check Neon project status
# Visit https://console.neon.tech
```

### SSL Mode Issues

For Neon and other cloud providers, always use `?sslmode=require`:

```bash
# Correct
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Incorrect (will fail)
DATABASE_URL=postgresql://user:pass@host/db
```

### Permission Denied

```bash
# Grant permissions
psql DATABASE_URL -c "GRANT ALL PRIVILEGES ON DATABASE ai_research TO postgres;"
```

### Database Does Not Exist

```bash
# Create database
psql postgres -c "CREATE DATABASE ai_research;"
```

## Best Practices

1. **推荐使用 Neon** - 本地开发和生产环境都使用 Neon，保持环境一致性
2. **Never commit real credentials** - Use `.env` and `.env.local`, add to `.gitignore`
3. **Use different databases** - Separate dev/staging/prod databases (create separate Neon projects)
4. **Enable SSL in production** - Always use `sslmode=require` with Neon
5. **Regular backups** - Neon provides automatic backups, enable for production
6. **Monitor connection pool** - Watch for connection leaks in production
7. **使用独立数据库实例** - 开发环境和生产环境使用不同的 Neon 项目
8. **监控使用量** - 定期检查 Neon 的存储和计算时间使用情况

## References

- [Neon Documentation](https://neon.tech/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
