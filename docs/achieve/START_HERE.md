# 🚀 从这里开始

欢迎使用 **Reflective Research Agent** - 一个智能的多代理研究报告生成系统！

---

## ⚡ 快速启动（5 分钟）

### 1️⃣ 配置 API Keys

编辑 `.env` 文件，填入你的 API Keys：

```bash
OPENAI_API_KEY=sk-proj-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

**获取 API Keys:**
- 🔑 OpenAI: https://platform.openai.com/api-keys
- 🔑 Tavily: https://tavily.com/

### 2️⃣ 启动服务

```bash
./start.sh
```

### 3️⃣ 访问应用

打开浏览器：http://localhost:8000/

---

## 📖 详细文档

| 文档 | 说明 | 阅读时间 |
|------|------|----------|
| [QUICKSTART.md](./QUICKSTART.md) | 快速启动指南 | 5 分钟 |
| [SETUP.md](./SETUP.md) | 完整设置指南 | 15 分钟 |
| [README.md](./README.md) | 项目介绍 | 10 分钟 |
| [docs/](./docs/) | 完整技术文档 | 2 小时 |

---

## 🛠️ 常用命令

```bash
./start.sh    # 启动服务
./stop.sh     # 停止服务
./check.sh    # 检查状态
```

---

## 🎯 这个项目能做什么？

输入一个研究主题，系统会：

1. 📋 **自动规划** - 生成 7 步研究计划
2. 🔍 **智能搜索** - 使用 Tavily、arXiv、Wikipedia
3. ✍️ **撰写报告** - 生成完整的学术报告
4. 🧠 **审阅优化** - 自动编辑和改进

**示例主题:**
- "Large Language Models for scientific discovery"
- "Quantum computing applications in cryptography"
- "AI in healthcare: current trends and future directions"

---

## 🏗️ 技术架构

```
FastAPI + PostgreSQL + Docker
    ↓
多智能体系统 (aisuite)
    ├─ 规划代理 (Planning Agent)
    ├─ 研究代理 (Research Agent)
    ├─ 写作代理 (Writer Agent)
    └─ 编辑代理 (Editor Agent)
    ↓
工具调用 (Function Calling)
    ├─ Tavily (网络搜索)
    ├─ arXiv (学术论文)
    └─ Wikipedia (百科知识)
```

---

## 💡 核心特性

- ✅ **多智能体协作** - 4 个专业代理分工合作
- ✅ **自动工具调用** - 智能选择和使用搜索工具
- ✅ **实时进度跟踪** - 查看每个步骤的执行状态
- ✅ **完整学术报告** - 包含引用、参考文献的专业报告
- ✅ **Docker 一键部署** - 无需复杂配置

---

## 🎓 学习资源

### 快速了解（15 分钟）
1. [快速参考](./docs/research-summary/QUICK_REFERENCE.md)
2. [工具调用指南](./docs/TOOL_CALLING_SUMMARY.md)

### 深入学习（2 小时）
1. [完整调研报告](./docs/research-summary/requirements.md)
2. [生产架构设计](./docs/production_architecture.md)
3. [代码示例](./docs/tool_calling_examples.py)

---

## 🐛 遇到问题？

### 检查系统状态
```bash
./check.sh
```

### 查看日志
```bash
docker logs -f fpsvc
```

### 常见问题
- Docker 未安装？→ 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 端口被占用？→ 运行 `lsof -ti:8000 | xargs kill -9`
- API Key 无效？→ 检查 `.env` 文件格式

更多帮助：[SETUP.md](./SETUP.md#-故障排除)

---

## 📊 项目亮点

### 代码简洁
使用 aisuite 框架，工具调用只需 10 行代码：

```python
response = client.chat.completions.create(
    model="openai:gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    tools=[tavily_search_tool, arxiv_search_tool, wikipedia_search_tool],
    max_turns=5,  # 自动多轮工具调用
    temperature=0
)
```

### 文档完善
- 📚 50,000+ 字的技术文档
- 📊 完整的架构分析
- 💰 详细的成本效益分析
- 🚀 生产环境部署方案

### 可扩展性
- 支持多个 LLM 模型（OpenAI、Anthropic）
- 易于添加新的搜索工具
- 清晰的代理架构

---

## 🎯 下一步

1. ✅ 配置 `.env` 文件
2. ✅ 运行 `./start.sh`
3. ✅ 访问 http://localhost:8000/
4. ✅ 提交你的第一个研究主题！

---

## 📞 获取帮助

- 📖 查看 [完整文档](./docs/README.md)
- 🐛 查看 [故障排除](./SETUP.md#-故障排除)
- 💬 查看 [API 文档](http://localhost:8000/docs)

---

**准备好了吗？开始你的研究之旅！🚀**

```bash
./start.sh
```
