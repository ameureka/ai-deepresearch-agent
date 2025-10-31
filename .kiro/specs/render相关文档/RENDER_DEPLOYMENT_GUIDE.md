# Render 部署指南

本指南将帮助你将 AI Research Assistant 部署到 Render。

## 📋 前置准备

### 1. 确保你有以下账号和 API Keys

- ✅ GitHub 账号（用于连接仓库）
- ✅ Render 账号（https://render.com）
- ✅ Neon 数据库（已配置）
- ✅ OpenAI API Key
- ✅ DeepSeek API Key
- ✅ Tavily API Key

### 2. 确认代码已推送到 GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

---

## 🚀 部署步骤

### 第一步：创建 Render Web Service

1. **登录 Render Dashboard**
   - 访问：https://dashboard.render.com/

2. **创建新的 Web Service**
   - 点击 "New +" → "Web Service"

3. **连接 GitHub 仓库**
   - 选择你的仓库：`agentic-ai-public-main`
   - 如果看不到仓库，点击 "Configure account" 授权

4. **配置 Web Service**
   
   **基本信息**：
   - Name: `ai-research-assistant`（或你喜欢的名字）
   - Region: `Oregon (US West)` 或离你更近的区域
   - Branch: `main`
   
   **构建配置**：
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
   
   **计划**：
   - 选择 `Free` 或 `Starter ($7/月)`
   
   **高级设置**：
   - Health Check Path: `/api/health`
   - Auto-Deploy: `Yes`（推荐，代码推送后自动部署）

5. **点击 "Create Web Service"**

---

### 第二步：配置环境变量

在 Render Dashboard 的 "Environment" 标签页添加以下环境变量：

#### 必需的环境变量

```bash
# 数据库
DATABASE_URL=postgresql://neondb_owner:npg_xxx@ep-xxx.aws.neon.tech/neondb?sslmode=require

# API Keys
OPENAI_API_KEY=sk-proj-xxx
DEEPSEEK_API_KEY=sk-xxx
TAVILY_API_KEY=tvly-dev-xxx

# 环境配置
ENV=production
LOG_LEVEL=INFO
```

#### 可选的环境变量

```bash
# CORS 配置（部署后更新为实际域名）
ALLOWED_ORIGINS=https://your-app.onrender.com

# 上下文优化配置
ENABLE_CHUNKING=true
CHUNKING_THRESHOLD=0.8
MAX_CHUNK_SIZE=6000
CHUNK_OVERLAP=200
```

**重要提示**：
- 从你的 `.env` 文件复制实际的值
- 不要包含引号
- DATABASE_URL 直接从 Neon 控制台复制

---

### 第三步：等待部署完成

1. **查看部署日志**
   - 在 "Logs" 标签页查看实时日志
   - 等待看到 "✅ 数据库表初始化完成"

2. **检查部署状态**
   - 状态变为 "Live" 表示部署成功
   - 记录你的应用 URL：`https://your-app.onrender.com`

---

### 第四步：验证部署

#### 4.1 健康检查

访问：`https://your-app.onrender.com/api/health`

**预期响应**：
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "timestamp": "2025-10-31T...",
    "version": "2.0.0"
  }
}
```

#### 4.2 测试首页

访问：`https://your-app.onrender.com/`

**预期结果**：
- ✅ 看到研究助手的 UI
- ✅ 静态资源（图片）正常加载
- ✅ 可以输入研究主题

#### 4.3 测试研究功能

1. 在首页输入一个简单的研究主题：
   ```
   Research the latest developments in AI agents
   ```

2. 点击 "Generate Report"

3. 观察进度：
   - ✅ 看到执行步骤
   - ✅ 每个步骤显示进度
   - ✅ 最终生成报告

#### 4.4 测试 SSE 流式接口

使用 curl 测试：
```bash
curl -X POST https://your-app.onrender.com/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Research AI applications"}' \
  -N
```

**预期输出**：
```
event: start
data: {"prompt":"Research AI applications"}

event: plan
data: {"steps":["Step 1","Step 2",...]}

event: progress
data: {"step":1,"total":5,"message":"..."}

...

event: done
data: {"report":"# Research Report\n..."}
```

---

## 🔧 常见问题排查

### 问题 1：部署失败 - "Build failed"

**可能原因**：
- requirements.txt 中的依赖安装失败

**解决方案**：
1. 查看构建日志，找到失败的依赖
2. 检查 requirements.txt 是否有拼写错误
3. 尝试在本地运行 `pip install -r requirements.txt`

---

### 问题 2：应用启动失败 - "Application failed to respond"

**可能原因**：
- 环境变量配置错误
- 数据库连接失败

**解决方案**：
1. 检查 "Logs" 标签页的错误信息
2. 确认 DATABASE_URL 正确
3. 确认所有 API Keys 已配置

---

### 问题 3：数据库连接错误

**错误信息**：
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**：
1. 检查 DATABASE_URL 格式：
   ```
   postgresql://user:password@host/database?sslmode=require
   ```
2. 确认 Neon 数据库正在运行
3. 检查 Neon 的 IP 白名单设置（如果有）

---

### 问题 4：应用频繁休眠（免费层）

**现象**：
- 15 分钟无请求后应用休眠
- 下次访问需要等待 30-60 秒冷启动

**解决方案 A：使用 Cron Job 防止休眠**

1. 注册 cron-job.org（免费）
2. 创建新任务：
   - URL: `https://your-app.onrender.com/api/health`
   - 间隔: 每 10 分钟
   - 方法: GET

**解决方案 B：升级到 Starter 计划**
- $7/月
- 不休眠
- 更好的性能

---

### 问题 5：内存不足（OOM）

**错误信息**：
```
Process killed (out of memory)
```

**解决方案**：
1. 减少 Gunicorn workers：
   ```bash
   gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```
2. 升级到 Starter 计划（1GB RAM）

---

### 问题 6：CORS 错误

**错误信息**（浏览器控制台）：
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**解决方案**：
1. 更新 ALLOWED_ORIGINS 环境变量：
   ```
   ALLOWED_ORIGINS=https://your-app.onrender.com,https://your-frontend.vercel.app
   ```
2. 重新部署应用

---

## 📊 性能优化建议

### 1. 启用 CDN（可选）

Render 自动提供 CDN，但你可以：
- 使用 Cloudflare 作为额外的 CDN 层
- 将静态文件上传到 Vercel/Netlify

### 2. 数据库连接池

当前配置已经使用了 SQLAlchemy 的连接池，默认设置：
- pool_size: 5
- max_overflow: 10

如果需要调整，在 main.py 中修改：
```python
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20
)
```

### 3. 日志优化

生产环境建议：
- 设置 LOG_LEVEL=WARNING（减少日志量）
- 使用结构化日志（JSON 格式）

---

## 🔄 更新部署

### 自动部署（推荐）

如果启用了 Auto-Deploy：
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render 会自动检测到推送并重新部署。

### 手动部署

在 Render Dashboard：
1. 进入你的 Web Service
2. 点击 "Manual Deploy" → "Deploy latest commit"

---

## 📈 监控和维护

### 1. 查看日志

在 Render Dashboard 的 "Logs" 标签页：
- 实时查看应用日志
- 搜索错误信息
- 下载日志文件

### 2. 监控指标

在 "Metrics" 标签页查看：
- CPU 使用率
- 内存使用率
- 请求数量
- 响应时间

### 3. 设置告警（付费功能）

Render 的 Starter 计划及以上支持：
- 邮件告警
- Slack 集成
- Webhook 通知

---

## 🎉 部署成功检查清单

- [ ] 应用可以访问（https://your-app.onrender.com）
- [ ] 健康检查返回 200（/api/health）
- [ ] 首页正常显示（/）
- [ ] 可以提交研究任务
- [ ] 静态文件正常加载
- [ ] SSE 流式接口工作正常
- [ ] 数据库连接正常
- [ ] 日志没有错误信息
- [ ] 已配置防休眠（如果使用免费层）
- [ ] 已更新 ALLOWED_ORIGINS

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**：Render Dashboard → Logs
2. **查看文档**：https://render.com/docs
3. **社区支持**：https://community.render.com
4. **GitHub Issues**：在项目仓库提交 issue

---

## 🔗 相关链接

- Render Dashboard: https://dashboard.render.com
- Render 文档: https://render.com/docs
- Neon 控制台: https://console.neon.tech
- Cron-job.org: https://cron-job.org

---

**祝部署顺利！🚀**
