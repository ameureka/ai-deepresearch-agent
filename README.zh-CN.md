# AI 深度研究助手

[English](./README.md) | 简体中文

> 🚀 **智能研究系统** - 集成 Next.js 前端和 FastAPI 后端的全栈 AI 研究平台

一个生产就绪的 AI 研究助手，具有现代化的 Next.js 前端（实时研究进度追踪）和由多个专业智能体（规划器、研究员、写作者、编辑）驱动的 FastAPI 后端。

[![版本](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/ameureka/ai-deepresearch-agent)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-15.3-black.svg)](https://nextjs.org/)
[![许可证](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🎯 功能特性

### ✨ 全栈集成（第 3、4 阶段）
- **现代化 UI**：Next.js 15 配合 App Router 和服务器组件
- **实时更新**：基于 SSE 的研究进度流式传输
- **响应式设计**：移动优先，带有固定研究面板
- **用户触发研究**：无缝的 AI 到研究工作流
- **生产就绪**：Docker Compose 编排所有服务

### 🧠 智能上下文管理（第 1.5 阶段）
- **无限长度**：处理任意长度的文本
- **智能分块**：语义文本分割，保留上下文
- **自动适配**：自动调整模型参数
- **错误恢复**：自动重试并调整参数

### 💰 成本优化（第 1 阶段）
- **DeepSeek 集成**：相比 OpenAI 节省约 45% 成本
- **智能回退**：DeepSeek 失败时自动切换到 OpenAI
- **实时追踪**：监控 API 成本和 token 使用量
- **工具调用**：100% 兼容 OpenAI 函数调用

### 🤖 多智能体协作
- **规划智能体**：使用 deepseek-reasoner 进行任务规划
- **研究智能体**：通过 Tavily、arXiv、Wikipedia 收集信息
- **写作智能体**：结构化报告生成
- **编辑智能体**：质量优化和精炼

---

## 🏗️ 架构

### Monorepo 结构

```
ai-deepresearch-agent/
├── ai-chatbot-main/              # Next.js 前端
│   ├── app/                      # Next.js App Router
│   ├── components/               # React 组件
│   │   ├── chat.tsx             # 主聊天界面
│   │   ├── research-button.tsx  # 研究触发按钮
│   │   ├── research-panel.tsx   # 研究 UI 容器
│   │   └── research-progress.tsx # 实时进度显示
│   ├── hooks/                    # React Hooks
│   │   └── use-research-progress.ts # SSE 研究 hook
│   ├── lib/                      # 工具函数
│   │   └── research-utils.ts    # 关键词检测
│   └── playwright/               # E2E 测试
├── src/                          # FastAPI 后端
│   ├── planning_agent.py         # 任务规划和执行
│   ├── agents.py                 # 研究/写作/编辑智能体
│   ├── research_tools.py         # 搜索工具集成
│   ├── model_adapter.py          # 模型参数适配
│   ├── chunking.py               # 文本分块处理器
│   └── context_manager.py        # 上下文管理
├── main.py                       # FastAPI 入口点
├── Dockerfile.backend            # 后端 Docker 配置
├── docker-compose.yml            # 多服务编排
└── README.md                     # 本文件
```

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Next.js 前端（端口 3000）                    │
│  - 现代化 React UI 配合 App Router                            │
│  - 实时 SSE 流式传输（fetch-event-source）                    │
│  - 带有固定定位的 ResearchPanel                               │
│  - useResearchProgress Hook                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI 后端（端口 8000）                     │
│  - REST API 端点                                             │
│  - SSE 研究流式传输（/api/research/stream）                   │
│  - 后台任务管理                                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    多智能体工作流引擎                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   规划器     │→ │   研究员     │→ │   写作者     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                                      ↓             │
│  ┌──────────────┐                      ┌──────────────┐     │
│  │   编辑器     │                      │  成本追踪器  │     │
│  └──────────────┘                      └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 集成层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DeepSeek    │  │   OpenAI     │  │   Tavily     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL 数据库（端口 5432）                   │
│  - 任务状态管理                                               │
│  - 研究结果存储                                               │
│  - 成本追踪记录                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求

- **Docker Desktop**（Windows/macOS）或 **Docker Engine**（Linux）
- **API 密钥**：
  - [DeepSeek API 密钥](https://platform.deepseek.com/)
  - [OpenAI API 密钥](https://platform.openai.com/)
  - [Tavily API 密钥](https://tavily.com/)

### 方法 A：Docker Compose（推荐）

#### 1. 克隆仓库

```bash
git clone https://github.com/ameureka/ai-deepresearch-agent.git
cd ai-deepresearch-agent
```

#### 2. 配置环境

```bash
# 创建 .env 文件
cp .env.example .env

# 使用你的 API 密钥编辑 .env
nano .env
```

必需的环境变量：

```bash
# API 密钥
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key

# 数据库（Docker 中的 PostgreSQL）
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_research

# 认证
AUTH_SECRET=your-random-secret-key
```

#### 3. 启动所有服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查状态
docker-compose ps
```

#### 4. 访问应用

- **前端**：http://localhost:3000
- **后端 API**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

#### 5. 停止服务

```bash
docker-compose down        # 停止服务
docker-compose down -v     # 停止并删除卷
```

### 方法 B：直接运行（开发模式）

#### 终端 1：PostgreSQL

```bash
# 安装 PostgreSQL（macOS）
brew install postgresql@15
brew services start postgresql@15

# 创建数据库
psql postgres -c "CREATE DATABASE ai_research;"
```

#### 终端 2：FastAPI 后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
export DEEPSEEK_API_KEY=sk-your-key
export TAVILY_API_KEY=tvly-your-key

# 启动后端
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 终端 3：Next.js 前端

```bash
# 安装 Node.js 依赖
cd ai-chatbot-main
npm install

# 配置环境
cp .env.example .env.local
# 使用你的 API 密钥编辑 .env.local

# 启动前端
npm run dev
```

访问：http://localhost:3000

---

## 📖 使用方法

### Web 界面

1. 打开 http://localhost:3000
2. 与 AI 助手聊天
3. 当 AI 建议研究时，点击 **"开始研究"** 按钮
4. 通过 SSE 流式传输观看实时进度
5. 在聊天中查看最终研究报告

### 研究流程（第 3 阶段架构）

```typescript
用户消息："告诉我关于量子计算的信息"
        ↓
AI 响应："我可以为你研究量子计算..."
        ↓
ResearchButton 出现（固定在 bottom-[72px]）
        ↓
用户点击"开始研究"
        ↓
useResearchProgress Hook 发起 POST SSE 到 /api/research/stream
        ↓
ResearchProgress 显示实时事件：
  - start：研究已开始
  - plan：研究计划已生成
  - progress：找到搜索结果
  - done：最终报告已准备好
        ↓
onComplete 回调将报告发送到聊天
        ↓
AI 继续带有研究上下文的对话
```

### API 使用

#### 启动研究任务

```bash
curl -X POST http://localhost:8000/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "量子计算应用"}'
```

#### 健康检查

```bash
curl http://localhost:8000/health
```

---

## 🧪 测试

### 后端测试

```bash
# 运行所有测试
cd /path/to/project
PYTHONPATH=. pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=src --cov-report=html
```

### 前端测试

```bash
cd ai-chatbot-main

# 单元测试
npm test

# E2E 测试（第 3 阶段更新）
npx playwright test

# 交互式 E2E
npx playwright test --ui
```

### E2E 测试覆盖（第 3 阶段）

- ✅ 研究关键词检测
- ✅ ResearchButton 显示和定位
- ✅ ResearchPanel 状态转换
- ✅ useResearchProgress SSE 连接
- ✅ 实时事件流式传输
- ✅ 报告完成流程

---

## 🔧 配置

### 后端配置（.env）

```bash
# API 密钥
DEEPSEEK_API_KEY=sk-your-key
OPENAI_API_KEY=sk-your-key
TAVILY_API_KEY=tvly-your-key
SERPER_API_KEY=your-key（可选）

# 数据库
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_research

# 模型选择
PLANNER_MODEL=deepseek:deepseek-reasoner
RESEARCHER_MODEL=deepseek:deepseek-chat
WRITER_MODEL=deepseek:deepseek-chat
EDITOR_MODEL=deepseek:deepseek-chat
FALLBACK_MODEL=openai:gpt-4o-mini

# 上下文管理
ENABLE_CHUNKING=true
CHUNKING_THRESHOLD=0.8
MAX_CHUNK_SIZE=6000
CHUNK_OVERLAP=200
```

### 前端配置（.env.local）

```bash
# 后端 API
NEXT_PUBLIC_API_URL=http://localhost:8000

# 认证
AUTH_SECRET=your-secret-key
AUTH_URL=http://localhost:3000/api/auth

# AI SDK
OPENAI_API_KEY=sk-your-key

# Node 环境
NODE_ENV=development
```

---

## 📊 性能

### 成本对比

| 任务类型 | OpenAI (gpt-4o-mini) | DeepSeek | 节省 |
|---------|---------------------|----------|------|
| 研究任务 | $0.0238 | $0.0129 | **45.8%** |
| 长文档 | $0.0450 | $0.0247 | **45.1%** |
| 复杂推理 | $0.0320 | $0.0176 | **45.0%** |

### 技术指标

| 指标 | 值 |
|-----|---|
| **后端测试覆盖率** | 83%（64/64 测试通过）|
| **前端单元测试** | 17/17 测试通过 |
| **最大文本长度** | 无限制（通过分块）|
| **API 响应时间** | < 100ms |
| **SSE 延迟** | < 50ms |

---

## 🔄 版本历史

### v0.2.0 - 第 4 阶段部署（2025-10-31）
- ✅ Monorepo 结构（前端 + 后端同级）
- ✅ Docker Compose 多服务编排
- ✅ 生产就绪配置
- ✅ 更新第 4 阶段的 .gitignore
- ✅ 统一 README 文档

### v0.1.5 - 第 3 阶段前端集成（2025-10-31）
- ✅ ResearchButton、ResearchPanel、ResearchProgress 组件
- ✅ 带有 POST SSE 的 useResearchProgress Hook
- ✅ 在 Chat 组件中集成
- ✅ 研究工具函数
- ✅ 所有组件的 17 个单元测试

### v0.1.2 - 第 2 阶段 API 标准化（2025-10-31）
- ✅ 统一 API 响应格式（ApiResponse）
- ✅ SSE 流式接口（/api/research/stream）
- ✅ 5 种 SSE 事件类型（START、PLAN、PROGRESS、DONE、ERROR）
- ✅ 全局错误处理（3 层异常处理器）
- ✅ 健康检查端点（/api/health）
- ✅ 模型列表端点（/api/models）
- ✅ 带环境变量的 CORS 配置
- ✅ 完整的 SSE 工作流集成
- ✅ 实时进度流式传输
- ✅ 完全向后兼容

### v0.1.0 - 第 1 和 1.5 阶段（2025-10-31）
- ✅ DeepSeek API 集成
- ✅ 智能上下文管理
- ✅ 成本优化（节省约 45%）
- ✅ 64 个后端单元测试

---

## 📚 文档

### 核心文档
- 🚀 [快速开始指南](./QUICK_START.md)
- 📖 [第 4 阶段部署任务](./.kiro/specs/phase4-deployment/tasks.md)
- 📊 [第 3 阶段实施报告](./.kiro/specs/phase3-nextjs-frontend/PHASE3_IMPLEMENTATION_REPORT.md)
- 🎨 [UI 设计报告](./.kiro/specs/phase3-nextjs-frontend/UI_DESIGN_REPORT.md)

### API 文档
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 开发指南
- [Docker Compose 设置](./.kiro/specs/phase4-deployment/design.md)
- [E2E 测试指南](./.kiro/specs/phase4-deployment/requirements.md)
- [部署检查清单](./.kiro/specs/phase4-deployment/tasks.md)

---

## 🐛 故障排除

### Docker Compose 问题

```bash
# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重建服务
docker-compose build --no-cache

# 重置所有内容
docker-compose down -v
docker-compose up -d --build
```

### 数据库连接问题

```bash
# 检查 PostgreSQL 状态
docker-compose exec postgres pg_isready

# 访问 PostgreSQL shell
docker-compose exec postgres psql -U postgres -d ai_research

# 重置数据库
docker-compose down -v
docker-compose up -d postgres
```

### 前端构建问题

```bash
cd ai-chatbot-main

# 清除 Next.js 缓存
rm -rf .next

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 重新构建
npm run build
```

---

## 🤝 贡献

我们欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 打开 Pull Request

### 开发指南
- 遵循 PEP 8（Python）和 ESLint（TypeScript）
- 为新功能添加单元测试
- 更新文档
- 确保所有测试通过

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 高性价比 AI 模型
- [OpenAI](https://openai.com/) - 回退模型支持
- [Tavily](https://tavily.com/) - 搜索 API
- [Vercel](https://vercel.com/) - Next.js 和部署平台
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web 框架
- [aisuite](https://github.com/andrewyng/aisuite) - 统一 AI API 接口

---

## 📞 联系方式

- **仓库**：https://github.com/ameureka/ai-deepresearch-agent
- **问题**：https://github.com/ameureka/ai-deepresearch-agent/issues
- **文档**：https://github.com/ameureka/ai-deepresearch-agent/tree/main/docs

---

**由 AI DeepResearch 团队用 ❤️ 制作**

**版本**：0.2.0（第 4 阶段）| **最后更新**：2025-10-31
