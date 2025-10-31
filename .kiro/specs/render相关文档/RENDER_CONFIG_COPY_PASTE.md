# Render 配置清单 - 直接复制粘贴

## 📋 基本配置

### Name（服务名称）
```
ai-deepresearch-agent
```

### Language（语言环境）
```
Python 3
```

### Branch（分支）
```
main
```

### Region（区域）
```
Oregon (US West)
```

---

## 🔧 构建和启动命令

### Build Command（构建命令）
```bash
pip install -r requirements.txt
```

### Start Command（启动命令）⚠️ 重要
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

---

## 🔐 环境变量（Environment Variables）

### 必需的环境变量

#### DATABASE_URL
```
从你的 .env 文件复制 DATABASE_URL
格式：postgresql://user:password@host/database?sslmode=require
```

#### OPENAI_API_KEY
```
从你的 .env 文件复制 OPENAI_API_KEY
格式：sk-proj-xxx...
```

#### DEEPSEEK_API_KEY
```
从你的 .env 文件复制 DEEPSEEK_API_KEY
格式：sk-xxx...
```

#### TAVILY_API_KEY
```
从你的 .env 文件复制 TAVILY_API_KEY
格式：tvly-dev-xxx...
```

#### ENV
```
production
```

#### LOG_LEVEL
```
INFO
```

#### ALLOWED_ORIGINS
```
*
```

---

## 🏥 高级设置（Advanced Settings）

### Health Check Path（健康检查路径）
```
/api/health
```

### Auto-Deploy（自动部署）
```
Yes
```

---

## 📝 在 Render Dashboard 中的操作步骤

### 1. 基本信息
- **Name**: 复制上面的服务名称
- **Language**: 选择 `Python 3`
- **Branch**: 选择 `main`
- **Region**: 选择 `Oregon (US West)`

### 2. 构建配置
- **Build Command**: 复制上面的构建命令
- **Start Command**: ⚠️ 复制上面的完整启动命令（不是 `gunicorn app:app`）

### 3. 环境变量
点击 "Add Environment Variable"，逐个添加：

| Key | Value |
|-----|-------|
| DATABASE_URL | 复制上面的完整 URL |
| OPENAI_API_KEY | 复制上面的 Key |
| DEEPSEEK_API_KEY | 复制上面的 Key |
| TAVILY_API_KEY | 复制上面的 Key |
| ENV | production |
| LOG_LEVEL | INFO |
| ALLOWED_ORIGINS | * |

### 4. 高级设置（可选但推荐）
- 展开 "Advanced" 部分
- **Health Check Path**: `/api/health`
- **Auto-Deploy**: 选择 `Yes`

### 5. 实例类型
- **Free**: 免费层（会休眠）
- **Starter ($7/月)**: 推荐，不休眠

---

## ✅ 配置检查清单

部署前请确认：

- [ ] Start Command 使用的是 `main:app`（不是 `app:app`）
- [ ] Start Command 包含 `--worker-class uvicorn.workers.UvicornWorker`
- [ ] Start Command 包含 `--bind 0.0.0.0:$PORT`
- [ ] 所有 7 个环境变量都已添加
- [ ] DATABASE_URL 包含 `?sslmode=require`
- [ ] Health Check Path 设置为 `/api/health`

---

## 🚀 部署后验证

部署完成后，访问以下 URL 验证：

### 1. 健康检查
```
https://ai-deepresearch-agent.onrender.com/api/health
```

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

### 2. 首页
```
https://ai-deepresearch-agent.onrender.com/
```

**预期结果**：看到研究助手的 UI 界面

### 3. 模型列表
```
https://ai-deepresearch-agent.onrender.com/api/models
```

**预期响应**：返回可用模型列表

---

## 🔧 常见问题

### 问题 1：启动失败 - "Application failed to respond"

**检查**：
- Start Command 是否正确（使用 `main:app`）
- 环境变量是否都已添加
- 查看 Logs 标签页的错误信息

### 问题 2：数据库连接失败

**检查**：
- DATABASE_URL 是否包含 `?sslmode=require`
- DATABASE_URL 是否完整（没有换行）
- Neon 数据库是否正在运行

### 问题 3：API Key 错误

**检查**：
- 环境变量名称是否正确（大小写敏感）
- API Key 是否有效
- API Key 是否有余额

---

## 📞 需要帮助？

如果遇到问题：

1. **查看日志**：Render Dashboard → Logs 标签页
2. **检查环境变量**：Environment 标签页
3. **重新部署**：Manual Deploy → Deploy latest commit

---

## 🎉 部署成功后

记得：

1. **更新 ALLOWED_ORIGINS**
   - 将 `*` 改为实际域名
   - 例如：`https://ai-deepresearch-agent.onrender.com`

2. **设置防休眠**（如果使用免费层）
   - 使用 cron-job.org
   - 每 10 分钟 ping `/api/health`

3. **测试所有功能**
   - 提交研究任务
   - 测试 SSE 流式接口
   - 检查数据库存储

---

**创建时间**: 2025-10-31  
**用途**: Render 部署配置快速参考
