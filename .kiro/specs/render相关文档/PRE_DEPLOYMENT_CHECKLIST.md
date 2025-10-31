# 部署前检查清单

在部署到 Render 之前，请确认以下所有项目：

## ✅ 代码准备

- [x] 移除了危险的 `Base.metadata.drop_all()`
- [x] 添加了 `gunicorn` 到 requirements.txt
- [x] 创建了 render.yaml 配置文件
- [x] 更新了 .env.example
- [x] 创建了部署指南文档

## ✅ 环境变量准备

请确认你有以下信息（从 .env 文件获取）：

### 必需的环境变量

```bash
# 数据库（从 Neon 控制台获取）
DATABASE_URL=postgresql://neondb_owner:npg_xxx@ep-xxx.aws.neon.tech/neondb?sslmode=require

# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxx

# DeepSeek API Key
DEEPSEEK_API_KEY=sk-xxx

# Tavily API Key
TAVILY_API_KEY=tvly-dev-xxx
```

### 可选的环境变量

```bash
ENV=production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*  # 部署后更新为实际域名
```

## ✅ 本地测试

### 1. 语法检查
```bash
python -c "import main; print('✅ 语法检查通过')"
```

**预期输出**：
```
✅ 数据库表初始化完成
✅ CORS 配置完成
✅ 语法检查通过
```

### 2. 启动测试（可选）
```bash
./start_production.sh
```

然后访问：
- http://localhost:8000/api/health
- http://localhost:8000/

### 3. 依赖检查
```bash
pip install -r requirements.txt
```

**确认所有依赖都能成功安装**

## ✅ Git 提交

### 1. 查看修改
```bash
git status
```

**应该看到**：
```
modified:   main.py
modified:   requirements.txt
modified:   .env.example
new file:   render.yaml
new file:   RENDER_DEPLOYMENT_GUIDE.md
new file:   start_production.sh
new file:   PRE_DEPLOYMENT_CHECKLIST.md
```

### 2. 提交修改
```bash
git add .
git commit -m "Prepare for Render deployment

- Remove dangerous drop_all() in database initialization
- Add gunicorn for production deployment
- Create render.yaml configuration
- Add deployment guide and checklist
- Update .env.example with production settings"
```

### 3. 推送到 GitHub
```bash
git push origin main
```

## ✅ Render 账号准备

- [ ] 已注册 Render 账号（https://render.com）
- [ ] 已连接 GitHub 账号
- [ ] 已授权访问仓库

## ✅ 数据库准备

- [ ] Neon 数据库正在运行
- [ ] 已获取 DATABASE_URL
- [ ] 数据库可以从外部访问（Neon 默认允许）

## ✅ API Keys 准备

- [ ] OpenAI API Key 有效且有余额
- [ ] DeepSeek API Key 有效且有余额
- [ ] Tavily API Key 有效且有余额

## 🚀 准备部署

如果以上所有项目都已确认，你可以开始部署了！

### 下一步：

1. **阅读部署指南**
   ```bash
   cat RENDER_DEPLOYMENT_GUIDE.md
   ```

2. **登录 Render Dashboard**
   - 访问：https://dashboard.render.com

3. **创建 Web Service**
   - 按照 RENDER_DEPLOYMENT_GUIDE.md 的步骤操作

4. **配置环境变量**
   - 从上面的清单复制环境变量

5. **等待部署完成**
   - 查看日志确认成功

6. **验证部署**
   - 访问 /api/health
   - 测试首页
   - 提交研究任务

---

## 📝 部署后任务

部署成功后，记得：

- [ ] 更新 ALLOWED_ORIGINS 为实际域名
- [ ] 设置 cron-job.org 防止休眠（免费层）
- [ ] 测试所有功能
- [ ] 记录应用 URL
- [ ] 更新项目 README

---

## 🆘 遇到问题？

参考 RENDER_DEPLOYMENT_GUIDE.md 的"常见问题排查"部分。

---

**准备好了吗？开始部署吧！🚀**
