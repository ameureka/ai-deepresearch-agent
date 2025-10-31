# 🚀 Render 部署快速参考

## 一分钟速查

### 部署命令（Render Dashboard 配置）

```bash
# 构建命令
pip install -r requirements.txt

# 启动命令
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120

# 健康检查路径
/api/health
```

### 必需环境变量

```bash
DATABASE_URL=postgresql://neondb_owner:npg_xxx@ep-xxx.aws.neon.tech/neondb?sslmode=require
OPENAI_API_KEY=sk-proj-xxx
DEEPSEEK_API_KEY=sk-xxx
TAVILY_API_KEY=tvly-dev-xxx
ENV=production
LOG_LEVEL=INFO
```

### 验证端点

```bash
# 健康检查
curl https://your-app.onrender.com/api/health

# 首页
open https://your-app.onrender.com/

# 模型列表
curl https://your-app.onrender.com/api/models
```

---

## 部署流程（5 步）

1. **提交代码**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **创建 Web Service**
   - 登录 https://dashboard.render.com
   - New + → Web Service
   - 连接 GitHub 仓库

3. **配置服务**
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: 见上方
   - Plan: Free 或 Starter

4. **添加环境变量**
   - 在 Environment 标签页添加
   - 从 .env 复制值

5. **部署并验证**
   - 等待部署完成
   - 访问 /api/health
   - 测试功能

---

## 常见问题速查

| 问题 | 解决方案 |
|------|---------|
| 构建失败 | 检查 requirements.txt |
| 启动失败 | 检查环境变量和日志 |
| 数据库连接失败 | 检查 DATABASE_URL 格式 |
| 应用休眠 | 使用 cron-job.org 或升级 |
| 内存不足 | 减少 workers 或升级 |
| CORS 错误 | 更新 ALLOWED_ORIGINS |

---

## 文档索引

- 📘 **完整指南**: [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)
- ✅ **检查清单**: [PRE_DEPLOYMENT_CHECKLIST.md](./PRE_DEPLOYMENT_CHECKLIST.md)
- 📊 **总结**: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
- ⚙️ **配置**: [render.yaml](./render.yaml)

---

## 本地测试

```bash
# 生产模式启动
./start_production.sh

# 访问
open http://localhost:8000
```

---

**需要详细说明？查看 RENDER_DEPLOYMENT_GUIDE.md**
