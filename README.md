# AI 深度研究助手

简体中文 | [English](./README.en.md)

> 🚀 **智能研究系统** - 集成 Next.js 前端和 FastAPI 后端的全栈 AI 研究平台

一个生产就绪的 AI 研究助手，具有现代化的 Next.js 前端（实时研究进度追踪）和由多个专业智能体（规划器、研究员、写作者、编辑）驱动的 FastAPI 后端。

[![版本](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/ameureka/ai-deepresearch-agent)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-15.3-black.svg)](https://nextjs.org/)
[![许可证](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🎥 项目演示视频 / Project Demo Video

<div align="center">
  <a href="https://www.youtube.com/watch?v=CaXQkpPLbiY">
    <img src="https://img.youtube.com/vi/CaXQkpPLbiY/maxresdefault.jpg" alt="点击观看演示视频 / Click to watch demo video" width="600" />
  </a>
  
  <p>
    <a href="https://www.youtube.com/watch?v=CaXQkpPLbiY">📺 在 YouTube 观看 / Watch on YouTube</a>
  </p>
</div>

---

## 🎯 功能特性

### ✨ 全栈集成（第 3、4.5 阶段）
- **现代化 UI**：Next.js 15 配合 App Router 和服务器组件
- **实时更新**：基于 SSE 的研究进度流式传输与排队耗时反馈
- **响应式设计**：移动优先，带有固定研究面板
- **用户触发研究**：无缝的 AI 到研究工作流
- **研究历史**：内置“最近研究”列表，可一键重新打开历史报告
- **生产就绪**：Vercel 部署 + Python/Docker 后端 + Neon 数据库

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
├── ai-chatbot-main/            # Next.js 15 前端
│   ├── app/(chat)/...          # 聊天路由与 API 代理
│   ├── components/             # 共享 UI（ResearchPanel、Artifact 等）
│   ├── hooks/                  # 自定义 Hook（useResearchProgress 等）
│   ├── lib/                    # 数据库查询、Provider 与工具函数
│   ├── tests/                  # Vitest + Playwright 测试
│   └── package.json            # 前端依赖清单
├── src/                        # FastAPI 后端模块
│   ├── agents.py               # 研究/写作/编辑智能体封装
│   ├── planning_agent.py       # 规划器与执行流水线
│   ├── research_tools.py       # Tavily、Wikipedia 集成
│   ├── sse.py                  # 任务队列与流式工具
│   └── model_adapter.py        # 模型选择与回退逻辑
├── main.py                     # FastAPI 入口（API + 队列）
├── scripts/                    # 初始化与开发脚本
├── docker-compose.yml          # 本地编排（前端 + 后端）
└── README.md                   # 项目文档
```

### 系统架构

**开发环境：**
```
┌─────────────────────────────────────────────────────────────┐
│         Next.js 前端（npm run dev / vercel dev）             │
│  - 本地开发服务器（端口 3000）                                 │
│  - 实时 SSE 流式传输（fetch-event-source）                    │
│  - 带有固定定位的 ResearchPanel                               │
│  - useResearchProgress Hook                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          FastAPI 后端（uvicorn --reload）                    │
│  - Python 直接运行（端口 8000）- 推荐                         │
│  - 或 Docker Compose（可选，低优先级）                        │
│  - REST API + SSE 研究流式传输                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              多智能体工作流引擎                                │
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
│                 API 集成层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DeepSeek    │  │   OpenAI     │  │   Tavily     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Neon PostgreSQL（SaaS - cloud.neon.tech）           │
│  - 无服务器数据库，用于开发和生产环境                           │
│  - 任务状态管理                                               │
│  - 研究结果存储                                               │
└─────────────────────────────────────────────────────────────┘
```

**生产环境：**
```
┌─────────────────────────────────────────────────────────────┐
│              Vercel 平台（Edge CDN）                         │
│  - Next.js 15 部署                                           │
│  - 全球边缘网络                                               │
│  - 自动 HTTPS                                                │
│  - URL：https://your-app.vercel.app                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Render / 独立服务器                                 │
│  - Python uvicorn 部署（推荐）                               │
│  - 或 Docker 容器（可选）                                     │
│  - URL：https://your-backend.onrender.com                   │
└────────────────────────┬────────────────────────────────────┘
                         │ SSL/TLS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Neon PostgreSQL（生产环境）                        │
│  - 无服务器 PostgreSQL，自动扩展                              │
│  - 自动备份                                                   │
│  - URL：postgresql://...@ep-xxx-prod.neon.tech/...         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求

- **Python 3.11+** 和 **Node.js 18+**
- **Neon 账号** - 免费的无服务器 PostgreSQL（[注册](https://neon.tech)）
- **API 密钥**：
  - [DeepSeek API 密钥](https://platform.deepseek.com/)
  - [OpenAI API 密钥](https://platform.openai.com/)
  - [Tavily API 密钥](https://tavily.com/)

### 方法 A：自动化安装（推荐）

#### 1. 克隆仓库

```bash
git clone https://github.com/ameureka/ai-deepresearch-agent.git
cd ai-deepresearch-agent
```

#### 2. 设置 Neon 数据库

1. 访问 https://neon.tech 并创建免费账号
2. 创建新项目（例如：`ai-research-dev`）
3. 复制连接字符串（格式类似：`postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require`）

#### 3. 配置环境

```bash
# 后端环境
cp .env.example .env
nano .env  # 添加你的 API 密钥和 Neon DATABASE_URL

# 前端环境
cp ai-chatbot-main/.env.local.example ai-chatbot-main/.env.local
nano ai-chatbot-main/.env.local  # 添加 POSTGRES_URL 和后端 API URL
```

必需的环境变量：

**.env（后端）：**
```bash
# API 密钥
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key

# 数据库（Neon SaaS - 开发和生产环境通用）
DATABASE_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/db?sslmode=require

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

**ai-chatbot-main/.env.local（前端）：**
```bash
# 数据库（与后端相同的 Neon 连接）
POSTGRES_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/db?sslmode=require

# 后端 API
RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# 认证
AUTH_SECRET=your-random-secret-min-32-chars
```

#### 4. 运行自动化设置

```bash
# 设置后端（创建 venv，安装依赖）
./scripts/setup-backend.sh

# 设置前端（安装 npm 包）
./scripts/setup-frontend.sh

# 启动所有服务（前端 + 后端）
./scripts/dev.sh
```

这将启动：
- **前端**：http://localhost:3000（Vercel Dev / npm run dev）
- **后端**：http://localhost:8000（Python uvicorn）
- **数据库**：Neon SaaS（无需本地设置！）

#### 5. 停止服务

```bash
# 在另一个终端中
./scripts/stop-dev.sh
```

### 方法 B：Docker Compose（可选 - 仅后端）

⚠️ **注意**：Docker 是可选的，仅用于后端部署（低优先级）。前端始终使用 Vercel。

```bash
# 在 Docker 中启动后端 + PostgreSQL（用于测试）
docker-compose up -d backend postgres

# 前端仍然使用 npm 运行
cd ai-chatbot-main && npm run dev
```

详见 [docker-compose.yml](./docker-compose.yml) 了解警告和详细配置。

### 方法 C：手动设置（高级）

要完全手动控制，请参阅[本地开发指南](./docs/LOCAL_DEVELOPMENT.md)获取详细说明，包括：
- 手动虚拟环境设置
- Neon 数据库配置
- 单个服务启动
- 故障排查提示

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

# 数据库（Neon SaaS - 推荐用于开发和生产环境）
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

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

# 服务器配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### 前端配置（.env.local）

```bash
# 数据库（与后端相同的 Neon 连接）
POSTGRES_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

# 后端 API
RESEARCH_API_URL=http://localhost:8000       # 服务器端
NEXT_PUBLIC_API_URL=http://localhost:8000    # 客户端

# 认证
AUTH_SECRET=your-random-secret-min-32-chars
AUTH_URL=http://localhost:3000/api/auth

# Vercel 服务（可选）
BLOB_READ_WRITE_TOKEN=vercel_blob_xxx
AI_GATEWAY_API_KEY=vercel_ag_xxx

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

### v0.3.0 - 生产部署完成（2025-11-04）
- ✅ **前端部署**：Vercel 平台 https://deepresearch.ameureka.com
- ✅ **后端部署**：腾讯云 Ubuntu + Cloudflare Tunnel https://api.ameureka.com
- ✅ **数据库**：Neon PostgreSQL 生产环境
- ✅ **完整文档**：
  - 后端部署状态文档（配置详情、运维命令）
  - Cloudflare Tunnel 设置指南
  - 环境配置检查指南
  - 腾讯云部署指南
- ✅ **运维脚本**：
  - 后端状态检查脚本（check-backend-status.sh）
  - 部署验证脚本（verify-deployment.sh）
  - Cloudflare 自动化部署脚本（deploy-cloudflare.sh）
  - 后端更新脚本（update-backend.sh）
- ✅ **CORS 配置修复**：支持跨域请求
- ✅ **TypeScript 类型错误修复**：构建成功
- ✅ **生产环境验证**：所有服务运行正常

### v0.2.0 - 第 4 阶段部署（2025-11-01）
- ✅ Monorepo 结构（前端 + 后端同级）
- ✅ **架构说明**：
  - 前端：Vercel 部署（不使用 Docker）
  - 后端：Python 直接运行（推荐）或 Docker（可选）
  - 数据库：Neon PostgreSQL SaaS（开发和生产环境统一）
- ✅ 自动化设置脚本（setup-backend.sh、setup-frontend.sh、dev.sh）
- ✅ 生产环境部署指南（Vercel + Render/服务器 + Neon）
- ✅ 完整的环境变量文档
- ✅ 支持 Vercel Dev 的本地开发指南
- ✅ 更新第 4 阶段的 .gitignore
- ✅ 全面的 README 文档

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
- 💻 [本地开发指南](./docs/LOCAL_DEVELOPMENT.md) - **完整的设置和工作流程**
- 🔧 [环境变量指南](./docs/ENVIRONMENT_VARIABLES.md)
- 🗄️ [数据库配置](./docs/DATABASE_CONFIGURATION.md)
- 🐳 [Docker Compose 设置（可选）](./.kiro/specs/phase4-deployment/design.md) - 仅后端，低优先级
- 🧪 [E2E 测试指南](./.kiro/specs/phase4-deployment/requirements.md)
- ✅ [部署检查清单](./.kiro/specs/phase4-deployment/tasks.md)

### 部署指南
- 🚀 [Vercel 部署指南](./docs/VERCEL_DEPLOYMENT_GUIDE.md) - **前端部署（Vercel 平台）**
- ☁️ [腾讯云部署指南](./docs/TENCENT_CLOUD_DEPLOYMENT.md) - **后端部署到腾讯云**
- 🔒 [Cloudflare Tunnel 设置](./docs/CLOUDFLARE_TUNNEL_SETUP.md) - **HTTPS 隧道配置**
- 📊 [后端部署状态文档](./docs/BACKEND_DEPLOYMENT_STATUS.md) - **生产环境配置详情**
- 🔍 [环境配置检查](./docs/ENVIRONMENT_CONFIG_CHECK.md) - **配置验证指南**

### 运维脚本
- 🛠️ [后端状态检查脚本](./scripts/check-backend-status.sh) - **一键检查后端服务状态**
- ✅ [部署验证脚本](./scripts/verify-deployment.sh) - **验证完整部署**
- 🚀 [Cloudflare 部署脚本](./scripts/deploy-cloudflare.sh) - **自动化部署到腾讯云**
- 🔄 [后端更新脚本](./scripts/update-backend.sh) - **快速更新后端代码**

---

## 🐛 故障排除

### 后端问题

```bash
# 检查 Python 版本
python --version  # 应该是 3.11+

# 重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows：venv\Scripts\activate
pip install -r requirements.txt

# 检查后端是否运行
curl http://localhost:8000/health

# 查看后端日志
# 检查运行 uvicorn 的终端
```

### 前端问题

```bash
cd ai-chatbot-main

# 检查 Node 版本
node --version  # 应该是 18+

# 清除 Next.js 缓存
rm -rf .next

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 重新构建
npm run build

# 在开发模式下测试
npm run dev
```

### 数据库连接问题（Neon）

```bash
# 手动测试连接
psql "postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require"

# 常见问题：
# 1. 检查 DATABASE_URL 是否包含 ?sslmode=require
# 2. 验证 Neon 数据库未暂停（免费层会自动暂停）
# 3. 检查 Neon 控制台中的 IP 允许列表（如果已配置）
# 4. 确保连接字符串有正确的密码（没有特殊字符问题）
```

### Docker Compose 问题（如果使用可选 Docker）

⚠️ **注意**：Docker 仅适用于后端（可选）。前端不应使用 Docker。

```bash
# 检查后端服务状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 仅重建后端
docker-compose build --no-cache backend

# 重置后端
docker-compose down
docker-compose up -d backend

# 前端仍使用 npm 运行（不使用 Docker）
cd ai-chatbot-main && npm run dev
```

### 常见问题

**问题**："无法连接到后端 API"
- **解决方案**：确保后端在 8000 端口运行，并且设置了 `NEXT_PUBLIC_API_URL=http://localhost:8000`

**问题**："数据库连接超时"
- **解决方案**：检查 Neon 数据库状态（可能已暂停），验证连接字符串格式

**问题**："Module not found" 错误
- **解决方案**：运行 `pip install -r requirements.txt`（后端）或 `npm install`（前端）

**问题**："端口已被使用"
- **解决方案**：检查哪个进程在使用该端口：
  ```bash
  # macOS/Linux
  lsof -i :8000  # 后端
  lsof -i :3000  # 前端

  # Windows
  netstat -ano | findstr :8000
  ```

有关更详细的故障排除，请参阅：
- [本地开发指南](./docs/LOCAL_DEVELOPMENT.md#troubleshooting)
- [Vercel 部署指南](./docs/VERCEL_DEPLOYMENT.md#故障排查)
- [生产环境部署指南](./docs/PRODUCTION_DEPLOYMENT.md#故障排查)

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

**版本**：0.3.0（生产部署完成）| **最后更新**：2025-11-04
