# ⚡ 快速启动指南

## 🎯 5 分钟启动项目

### 步骤 1: 配置 API Keys

编辑 `.env` 文件：

```bash
nano .env
```

替换以下内容：
```env
OPENAI_API_KEY=sk-proj-xxxxx  # 你的 OpenAI API Key
TAVILY_API_KEY=tvly-xxxxx     # 你的 Tavily API Key
```

**获取 API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://tavily.com/

### 步骤 2: 启动服务

```bash
./start.sh
```

这个脚本会自动：
1. ✅ 检查 Docker 是否安装和运行
2. ✅ 检查 API Keys 是否配置
3. ✅ 构建 Docker 镜像（首次需要 3-5 分钟）
4. ✅ 启动服务

### 步骤 3: 访问应用

打开浏览器访问：
- **主页**: http://localhost:8000/
- **API 文档**: http://localhost:8000/docs

---

## 🛠️ 常用命令

### 启动服务
```bash
./start.sh
```

### 停止服务
```bash
./stop.sh
```

### 检查状态
```bash
./check.sh
```

### 查看日志
```bash
docker logs -f fpsvc
```

### 重新构建
```bash
docker build -t fastapi-postgres-service .
```

---

## 📝 使用示例

### 1. Web 界面使用

1. 访问 http://localhost:8000/
2. 输入研究主题，例如：
   ```
   Transformer architecture in natural language processing
   ```
3. 点击提交
4. 实时查看进度和最终报告

### 2. API 使用

```bash
# 提交研究任务
curl -X POST http://localhost:8000/generate_report \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quantum computing applications"}'

# 返回: {"task_id": "uuid-here"}

# 查看进度
curl http://localhost:8000/task_progress/uuid-here

# 查看结果
curl http://localhost:8000/task_status/uuid-here
```

### 3. Python 使用

```python
import requests
import time

# 提交任务
response = requests.post(
    "http://localhost:8000/generate_report",
    json={"prompt": "AI in healthcare"}
)
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# 轮询进度
while True:
    progress = requests.get(f"http://localhost:8000/task_progress/{task_id}")
    steps = progress.json()["steps"]
    
    # 检查是否完成
    all_done = all(s["status"] in ["done", "error"] for s in steps)
    if all_done:
        break
    
    time.sleep(2)

# 获取最终结果
result = requests.get(f"http://localhost:8000/task_status/{task_id}")
print(result.json())
```

---

## 🐛 常见问题

### Q1: Docker 未安装？

**macOS:**
```bash
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### Q2: 端口被占用？

```bash
# 查看占用端口的进程
lsof -ti:8000 | xargs kill -9

# 或使用不同端口
docker run --rm -it -p 8001:8000 -p 5433:5432 --name fpsvc --env-file .env fastapi-postgres-service
```

### Q3: API Key 无效？

1. 检查 `.env` 文件格式
2. 确保没有多余空格
3. 重新启动容器

### Q4: 构建失败？

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker build --no-cache -t fastapi-postgres-service .
```

---

## 📚 更多资源

- [完整设置指南](./SETUP.md)
- [项目文档](./docs/README.md)
- [工具调用指南](./docs/TOOL_CALLING_SUMMARY.md)
- [API 文档](http://localhost:8000/docs) (启动后访问)

---

## 🎉 开始使用

现在你可以：

1. ✅ 提交研究主题
2. ✅ 查看实时进度
3. ✅ 获取完整的学术报告
4. ✅ 通过 API 集成到你的应用

**祝你使用愉快！**
