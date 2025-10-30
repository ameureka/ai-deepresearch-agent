# 🚀 项目启动指南

## 📋 前置要求

1. **Docker Desktop** (推荐) 或 Docker Engine
   - macOS: [下载 Docker Desktop](https://www.docker.com/products/docker-desktop)
   - 确保 Docker 正在运行

2. **API Keys**
   - OpenAI API Key: [获取地址](https://platform.openai.com/api-keys)
   - Tavily API Key: [获取地址](https://tavily.com/)

---

## ⚙️ 配置步骤

### 1. 配置 API Keys

编辑项目根目录的 `.env` 文件：

```bash
# 使用你喜欢的编辑器打开
nano .env
# 或
code .env
```

替换以下内容：
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
TAVILY_API_KEY=tvly-your-actual-tavily-key-here
```

### 2. 构建 Docker 镜像

```bash
docker build -t fastapi-postgres-service .
```

这个过程会：
- 安装 Python 3.11
- 安装 PostgreSQL
- 安装所有 Python 依赖
- 复制项目文件

预计时间：3-5 分钟

### 3. 启动服务

```bash
docker run --rm -it \
  -p 8000:8000 \
  -p 5432:5432 \
  --name fpsvc \
  --env-file .env \
  fastapi-postgres-service
```

参数说明：
- `--rm`: 容器停止后自动删除
- `-it`: 交互模式，可以看到日志
- `-p 8000:8000`: 映射 FastAPI 端口
- `-p 5432:5432`: 映射 PostgreSQL 端口
- `--name fpsvc`: 容器名称
- `--env-file .env`: 加载环境变量

### 4. 验证启动

看到以下日志表示启动成功：

```
🚀 Starting Postgres cluster 17/main...
✅ Postgres is ready
CREATE ROLE
CREATE DATABASE
🔗 DATABASE_URL=postgresql://app:local@127.0.0.1:5432/appdb
INFO:     Started server process [XX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🌐 访问应用

### Web 界面
打开浏览器访问：
- **主页**: http://localhost:8000/
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api

### 使用示例

1. 在主页输入研究主题，例如：
   ```
   Large Language Models for scientific discovery
   ```

2. 点击提交，系统会：
   - 生成研究计划（7个步骤）
   - 使用 Tavily 搜索网络
   - 使用 arXiv 搜索学术论文
   - 使用 Wikipedia 查找背景信息
   - 撰写完整的学术报告
   - 编辑和优化报告

3. 实时查看进度和最终报告

---

## 🔧 开发模式

### 方式 1: 使用 Docker（推荐）

后台运行：
```bash
docker run -d \
  -p 8000:8000 \
  -p 5432:5432 \
  --name fpsvc \
  --env-file .env \
  fastapi-postgres-service
```

查看日志：
```bash
docker logs -f fpsvc
```

停止服务：
```bash
docker stop fpsvc
```

### 方式 2: 本地开发（需要本地 PostgreSQL）

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动 PostgreSQL（需要单独安装）

3. 设置环境变量：
```bash
export DATABASE_URL="postgresql://app:local@localhost:5432/appdb"
export OPENAI_API_KEY="your-key"
export TAVILY_API_KEY="your-key"
```

4. 运行应用：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 测试 API

### 使用 curl

```bash
# 提交研究任务
curl -X POST http://localhost:8000/generate_report \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quantum computing applications in cryptography"}'

# 返回: {"task_id": "uuid-here"}

# 查看进度
curl http://localhost:8000/task_progress/uuid-here

# 查看最终结果
curl http://localhost:8000/task_status/uuid-here
```

### 使用 Python

```python
import requests

# 提交任务
response = requests.post(
    "http://localhost:8000/generate_report",
    json={"prompt": "AI in healthcare"}
)
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# 查看进度
progress = requests.get(f"http://localhost:8000/task_progress/{task_id}")
print(progress.json())

# 查看结果
result = requests.get(f"http://localhost:8000/task_status/{task_id}")
print(result.json())
```

---

## 🐛 故障排除

### 问题 1: Docker 构建失败

**错误**: `Cannot connect to the Docker daemon`

**解决**:
```bash
# 确保 Docker Desktop 正在运行
# macOS: 检查菜单栏是否有 Docker 图标
```

### 问题 2: 端口被占用

**错误**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**解决**:
```bash
# 方式 1: 停止占用端口的进程
lsof -ti:8000 | xargs kill -9

# 方式 2: 使用不同端口
docker run --rm -it -p 8001:8000 -p 5433:5432 --name fpsvc --env-file .env fastapi-postgres-service
# 然后访问 http://localhost:8001
```

### 问题 3: API Key 无效

**错误**: 日志中出现 `401 Unauthorized` 或 `Invalid API key`

**解决**:
1. 检查 `.env` 文件中的 API keys 是否正确
2. 确保没有多余的空格或引号
3. 重新启动容器

### 问题 4: 数据库连接失败

**错误**: `could not connect to server`

**解决**:
```bash
# 检查 PostgreSQL 是否启动
docker exec -it fpsvc pg_isready -h 127.0.0.1 -p 5432

# 查看数据库日志
docker exec -it fpsvc tail -f /var/log/postgresql/postgresql-*-main.log
```

### 问题 5: 容器启动后立即退出

**解决**:
```bash
# 查看容器日志
docker logs fpsvc

# 以交互模式启动查看详细错误
docker run --rm -it --name fpsvc --env-file .env fastapi-postgres-service
```

---

## 📊 性能优化

### 调整模型参数

编辑 `src/planning_agent.py` 和 `src/agents.py`：

```python
# 使用更快的模型
model="openai:gpt-4o-mini"  # 快速、便宜

# 或使用更强大的模型
model="openai:gpt-4o"  # 更好的质量

# 或使用 Claude
model="anthropic:claude-3-5-sonnet-20241022"  # 强大的工具调用
```

### 调整并发

编辑 `main.py`，修改 `max_turns` 参数：

```python
# 减少工具调用轮次（更快）
max_turns=3

# 增加工具调用轮次（更全面）
max_turns=10
```

---

## 🔒 安全建议

1. **不要提交 .env 文件到 Git**
   - 已在 `.gitignore` 中配置

2. **生产环境使用强密码**
   ```env
   POSTGRES_PASSWORD=your-strong-password-here
   ```

3. **限制 API 访问**
   - 添加认证中间件
   - 使用 API Gateway

---

## 📚 下一步

- 阅读 [完整文档](./docs/README.md)
- 查看 [工具调用指南](./docs/TOOL_CALLING_SUMMARY.md)
- 了解 [生产架构](./docs/production_architecture.md)
- 运行 [代码示例](./docs/tool_calling_examples.py)

---

## 💬 获取帮助

- 查看 [README.md](./README.md)
- 查看 [故障排除](#-故障排除)
- 查看项目文档 `docs/` 目录

---

**祝你使用愉快！🎉**
