# AI DeepResearch Agent

[简体中文](./README.md) | English

> 🚀 **Intelligent Research System** - Full-stack AI research platform with integrated Next.js frontend and FastAPI backend

A production-ready AI research assistant featuring a modern Next.js frontend with real-time research progress tracking and a FastAPI backend powered by multiple specialized agents (Planner, Researcher, Writer, Editor).

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/ameureka/ai-deepresearch-agent)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-15.3-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🎯 Features

### ✨ Full-Stack Integration (Phase 3 & 4.5)
- **Modern UI**: Next.js 15 with App Router and Server Components
- **Real-Time Updates**: SSE-based research progress streaming + queue telemetry
- **Responsive Design**: Mobile-first with sticky research panel
- **User-Triggered Research**: Seamless AI-to-research workflow
- **Research History**: Inline “Recent Research” list with one-click report restore
- **Production Ready**: Vercel deployment + Python/Docker backend + Neon database

### 🧠 Intelligent Context Management (Phase 1.5)
- **Unlimited Length**: Process arbitrary length texts
- **Smart Chunking**: Semantic text splitting with context preservation
- **Auto-Adaptation**: Automatic model parameter tuning
- **Error Recovery**: Automatic retry with adjusted parameters

### 💰 Cost Optimization (Phase 1)
- **DeepSeek Integration**: ~45% cost savings vs OpenAI
- **Smart Fallback**: Auto-switch to OpenAI on DeepSeek failure
- **Real-Time Tracking**: Monitor API costs and token usage
- **Tool Calling**: 100% compatible with OpenAI function calling

### 🤖 Multi-Agent Collaboration
- **Planner Agent**: Task planning with deepseek-reasoner
- **Researcher Agent**: Information gathering via Tavily, arXiv, Wikipedia
- **Writer Agent**: Structured report generation
- **Editor Agent**: Quality optimization and refinement

---

## 🏗️ Architecture

### Monorepo Structure

```
ai-deepresearch-agent/
├── ai-chatbot-main/            # Next.js 15 frontend
│   ├── app/(chat)/...          # Chat routes & API proxies
│   ├── components/             # Shared UI (ResearchPanel, Artifact, ...)
│   ├── hooks/                  # Custom hooks (useResearchProgress, etc.)
│   ├── lib/                    # DB queries, providers, utilities
│   ├── tests/                  # Vitest + Playwright suites
│   └── package.json            # Frontend manifest
├── src/                        # FastAPI backend modules
│   ├── agents.py               # Research/Writer/Editor agent wrappers
│   ├── planning_agent.py       # Planner & execution pipeline
│   ├── research_tools.py       # Tavily/Wikipedia integrations
│   ├── sse.py                  # Task queue & streaming helpers
│   └── model_adapter.py        # Model selection & fallback logic
├── main.py                     # FastAPI entry point (APIs + queue worker)
├── scripts/                    # Setup & developer utilities
├── docker-compose.yml          # Local orchestration (frontend + backend)
└── README.en.md                # English documentation
```

### System Architecture

**Development Environment:**
```
┌─────────────────────────────────────────────────────────────┐
│         Next.js Frontend (npm run dev / vercel dev)          │
│  - Local dev server (Port 3000)                              │
│  - Real-time SSE streaming (fetch-event-source)              │
│  - ResearchPanel with sticky positioning                     │
│  - useResearchProgress Hook                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          FastAPI Backend (uvicorn --reload)                  │
│  - Python direct run (Port 8000) - RECOMMENDED               │
│  - OR Docker Compose (optional, low priority)                │
│  - REST API + SSE Research Streaming                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Agent Workflow Engine                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Planner    │→ │  Researcher  │→ │    Writer    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                                      ↓             │
│  ┌──────────────┐                      ┌──────────────┐     │
│  │   Editor     │                      │ Cost Tracker │     │
│  └──────────────┘                      └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 API Integration Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DeepSeek    │  │   OpenAI     │  │   Tavily     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Neon PostgreSQL (SaaS - cloud.neon.tech)          │
│  - Serverless database for dev AND production                │
│  - Task state management                                     │
│  - Research results storage                                  │
└─────────────────────────────────────────────────────────────┘
```

**Production Environment:**
```
┌─────────────────────────────────────────────────────────────┐
│                 Vercel Platform (Edge CDN)                   │
│  - Next.js 15 deployment                                     │
│  - Global Edge Network                                       │
│  - Automatic HTTPS                                           │
│  - URL: https://your-app.vercel.app                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Render / Independent Server                         │
│  - Python uvicorn deployment (RECOMMENDED)                   │
│  - OR Docker container (optional)                            │
│  - URL: https://your-backend.onrender.com                    │
└────────────────────────┬────────────────────────────────────┘
                         │ SSL/TLS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Neon PostgreSQL (Production)                      │
│  - Serverless PostgreSQL with auto-scaling                   │
│  - Automatic backups                                         │
│  - URL: postgresql://...@ep-xxx-prod.neon.tech/...          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** and **Node.js 18+**
- **Neon Account** - Free serverless PostgreSQL ([sign up](https://neon.tech))
- **API Keys**:
  - [DeepSeek API Key](https://platform.deepseek.com/)
  - [OpenAI API Key](https://platform.openai.com/)
  - [Tavily API Key](https://tavily.com/)

### Method A: Automated Setup (Recommended)

#### 1. Clone Repository

```bash
git clone https://github.com/ameureka/ai-deepresearch-agent.git
cd ai-deepresearch-agent
```

#### 2. Setup Neon Database

1. Visit https://neon.tech and create a free account
2. Create a new project (e.g., `ai-research-dev`)
3. Copy the connection string (looks like: `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require`)

#### 3. Configure Environment

```bash
# Backend environment
cp .env.example .env
nano .env  # Add your API keys and Neon DATABASE_URL

# Frontend environment
cp ai-chatbot-main/.env.local.example ai-chatbot-main/.env.local
nano ai-chatbot-main/.env.local  # Add POSTGRES_URL and backend API URL
```

Required environment variables:

**.env (Backend):**
```bash
# API Keys
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key

# Database (Neon SaaS - same for dev and prod)
DATABASE_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/db?sslmode=require

# Server Config
HOST=0.0.0.0
PORT=8000
```

**ai-chatbot-main/.env.local (Frontend):**
```bash
# Database (same Neon connection)
POSTGRES_URL=postgresql://user:pass@ep-xxx-dev.neon.tech/db?sslmode=require

# Backend API
RESEARCH_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth
AUTH_SECRET=your-random-secret-min-32-chars
```

#### 4. Run Automated Setup

```bash
# Setup backend (creates venv, installs dependencies)
./scripts/setup-backend.sh

# Setup frontend (installs npm packages)
./scripts/setup-frontend.sh

# Start all services (frontend + backend)
./scripts/dev.sh
```

This will start:
- **Frontend**: http://localhost:3000 (Vercel Dev / npm run dev)
- **Backend**: http://localhost:8000 (Python uvicorn)
- **Database**: Neon SaaS (no local setup needed!)

#### 5. Stop Services

```bash
# In another terminal
./scripts/stop-dev.sh
```

### Method B: Docker Compose (Optional - Backend Only)

⚠️ **Note**: Docker is optional and only for backend deployment (low priority). Frontend always uses Vercel.

```bash
# Start backend + PostgreSQL in Docker (for testing)
docker-compose up -d backend postgres

# Frontend still runs with npm
cd ai-chatbot-main && npm run dev
```

See [docker-compose.yml](./docker-compose.yml) for warnings and detailed configuration.

### Method C: Manual Setup (Advanced)

For complete manual control, see the [Local Development Guide](./docs/LOCAL_DEVELOPMENT.md) for detailed instructions including:
- Manual virtual environment setup
- Neon database configuration
- Individual service startup
- Troubleshooting tips

---

## 📖 Usage

### Web Interface

1. Open http://localhost:3000
2. Chat with the AI assistant
3. When AI suggests research, click **"Start Research"** button
4. Watch real-time progress with SSE streaming
5. View final research report in chat

### Research Flow (Phase 3 Architecture)

```typescript
User Message: "Tell me about quantum computing"
        ↓
AI Response: "I can research quantum computing for you..."
        ↓
ResearchButton appears (sticky at bottom-[72px])
        ↓
User clicks "Start Research"
        ↓
useResearchProgress Hook initiates POST SSE to /api/research/stream
        ↓
ResearchProgress displays real-time events:
  - start: Research started
  - plan: Research plan generated
  - progress: Search results found
  - done: Final report ready
        ↓
onComplete callback sends report to chat
        ↓
AI continues conversation with research context
```

### API Usage

#### Start Research Task

```bash
curl -X POST http://localhost:8000/api/research/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "quantum computing applications"}'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
cd /path/to/project
PYTHONPATH=. pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd ai-chatbot-main

# Unit tests
pnpm test:unit

# E2E tests (Phase 3 updated)
pnpm test:e2e

# Visual regression (Percy)
export NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW=true
PERCY_TOKEN=*** pnpm test:visual

# Accessibility checks (axe-core)
export NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW=true
pnpm test:a11y

# Performance audits (Lighthouse CI)
export NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW=true
pnpm test:perf

# Interactive E2E
pnpm exec playwright test --ui
```

> Percy 测试会访问 `/research-preview` 场景页面；请仅在本地或具备受控凭据的环境下开启 `NEXT_PUBLIC_ENABLE_RESEARCH_PREVIEW`。  
> 研究端到端流程测试需设置 `RUN_RESEARCH_E2E=true` 且确保 FastAPI 后端与 Neon 数据库可用。

### E2E Test Coverage (Phase 3)

- ✅ Research keyword detection
- ✅ ResearchButton display and positioning
- ✅ ResearchPanel state transitions
- ✅ useResearchProgress SSE connection
- ✅ Real-time event streaming
- ✅ Report completion flow

---

## 🔧 Configuration

### Backend Configuration (.env)

```bash
# API Keys
DEEPSEEK_API_KEY=sk-your-key
OPENAI_API_KEY=sk-your-key
TAVILY_API_KEY=tvly-your-key
SERPER_API_KEY=your-key (optional)

# Database (Neon SaaS - recommended for both dev and prod)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

# Model Selection
PLANNER_MODEL=deepseek:deepseek-reasoner
RESEARCHER_MODEL=deepseek:deepseek-chat
WRITER_MODEL=deepseek:deepseek-chat
EDITOR_MODEL=deepseek:deepseek-chat
FALLBACK_MODEL=openai:gpt-4o-mini

# Context Management
ENABLE_CHUNKING=true
CHUNKING_THRESHOLD=0.8
MAX_CHUNK_SIZE=6000
CHUNK_OVERLAP=200

# Server Config
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Frontend Configuration (.env.local)

```bash
# Database (same Neon connection as backend)
POSTGRES_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

# Backend API
RESEARCH_API_URL=http://localhost:8000       # Server-side
NEXT_PUBLIC_API_URL=http://localhost:8000    # Client-side

# Auth
AUTH_SECRET=your-random-secret-min-32-chars
AUTH_URL=http://localhost:3000/api/auth

# Vercel Services (optional)
BLOB_READ_WRITE_TOKEN=vercel_blob_xxx
AI_GATEWAY_API_KEY=vercel_ag_xxx

# Node Environment
NODE_ENV=development
```

---

## 📊 Performance

### Cost Comparison

| Task Type | OpenAI (gpt-4o-mini) | DeepSeek | Savings |
|-----------|---------------------|----------|---------|
| Research Task | $0.0238 | $0.0129 | **45.8%** |
| Long Document | $0.0450 | $0.0247 | **45.1%** |
| Complex Reasoning | $0.0320 | $0.0176 | **45.0%** |

### Technical Metrics

| Metric | Value |
|--------|-------|
| **Backend Test Coverage** | 83% (64/64 tests pass) |
| **Frontend Unit Tests** | 17/17 tests pass |
| **Max Text Length** | Unlimited (via chunking) |
| **API Response Time** | < 100ms |
| **SSE Latency** | < 50ms |

---

## 🔄 Version History

### v0.2.0 - Phase 4 Deployment (2025-11-01)
- ✅ Monorepo structure (frontend + backend at same level)
- ✅ **Architecture Clarification**:
  - Frontend: Vercel deployment (NOT Docker)
  - Backend: Python direct run (recommended) OR Docker (optional)
  - Database: Neon PostgreSQL SaaS (unified for dev and prod)
- ✅ Automated setup scripts (setup-backend.sh, setup-frontend.sh, dev.sh)
- ✅ Production deployment guides (Vercel + Render/Server + Neon)
- ✅ Complete environment variable documentation
- ✅ Local development guide with Vercel Dev support
- ✅ Updated .gitignore for Phase 4
- ✅ Comprehensive README documentation

### v0.1.5 - Phase 3 Frontend Integration (2025-10-31)
- ✅ ResearchButton, ResearchPanel, ResearchProgress components
- ✅ useResearchProgress Hook with POST SSE
- ✅ Integration in Chat component
- ✅ Research utility functions
- ✅ 17 unit tests for all components

### v0.1.2 - Phase 2 API Standardization (2025-10-31)
- ✅ Unified API response format (ApiResponse)
- ✅ SSE streaming interface (/api/research/stream)
- ✅ 5 SSE event types (START, PLAN, PROGRESS, DONE, ERROR)
- ✅ Global error handling (3-tier exception handlers)
- ✅ Health check endpoint (/api/health)
- ✅ Models list endpoint (/api/models)
- ✅ CORS configuration with environment variables
- ✅ Complete SSE workflow integration
- ✅ Real-time progress streaming
- ✅ Full backward compatibility

### v0.1.0 - Phase 1 & 1.5 (2025-10-31)
- ✅ DeepSeek API integration
- ✅ Intelligent context management
- ✅ Cost optimization (~45% savings)
- ✅ 64 backend unit tests

---

## 📚 Documentation

### Core Documentation
- 🚀 [Quick Start Guide](./QUICK_START.md)
- 📖 [Phase 4 Deployment Tasks](./.kiro/specs/phase4-deployment/tasks.md)
- 📊 [Phase 3 Implementation Report](./.kiro/specs/phase3-nextjs-frontend/PHASE3_IMPLEMENTATION_REPORT.md)
- 🎨 [UI Design Report](./.kiro/specs/phase3-nextjs-frontend/UI_DESIGN_REPORT.md)

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Development Guides
- 🤖 [Repository Guidelines](./AGENTS.md) - Contributor workflow and coding standards
- 💻 [Local Development Guide](./docs/LOCAL_DEVELOPMENT.md) - **Complete setup and workflow**
- 🔧 [Environment Variables Guide](./docs/ENVIRONMENT_VARIABLES.md)
- 🗄️ [Database Configuration](./docs/DATABASE_CONFIGURATION.md)
- 🐳 [Docker Compose Setup (Optional)](./.kiro/specs/phase4-deployment/design.md) - Backend only, low priority
- 🧪 [E2E Testing Guide](./.kiro/specs/phase4-deployment/requirements.md)
- ✅ [Deployment Checklist](./.kiro/specs/phase4-deployment/tasks.md)

### Deployment Guides
- 🚀 [Vercel Deployment Guide](./docs/VERCEL_DEPLOYMENT.md) - **Frontend deployment (Vercel platform)**
- 🌐 [Production Deployment Guide](./docs/PRODUCTION_DEPLOYMENT.md) - **Complete production setup**
  - Frontend: Vercel
  - Backend: Render or independent server (Python uvicorn)
  - Database: Neon PostgreSQL SaaS

---

## 🐛 Troubleshooting

### Backend Issues

```bash
# Check Python version
python --version  # Should be 3.11+

# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Check backend is running
curl http://localhost:8000/health

# View backend logs
# Check terminal where uvicorn is running
```

### Frontend Issues

```bash
cd ai-chatbot-main

# Check Node version
node --version  # Should be 18+

# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build

# Test in development mode
npm run dev
```

### Database Connection Issues (Neon)

```bash
# Test connection manually
psql "postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require"

# Common issues:
# 1. Check DATABASE_URL includes ?sslmode=require
# 2. Verify Neon database is not suspended (free tier auto-suspends)
# 3. Check IP allowlist in Neon dashboard (if configured)
# 4. Ensure connection string has correct password (no special chars issues)
```

### Docker Compose Issues (If Using Optional Docker)

⚠️ **Note**: Docker is optional for backend only. Frontend should NOT use Docker.

```bash
# Check backend service status
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Rebuild backend only
docker-compose build --no-cache backend

# Reset backend
docker-compose down
docker-compose up -d backend

# Frontend still runs with npm (NOT Docker)
cd ai-chatbot-main && npm run dev
```

### Common Issues

**Issue**: "Cannot connect to backend API"
- **Solution**: Ensure backend is running on port 8000 and `NEXT_PUBLIC_API_URL=http://localhost:8000` is set

**Issue**: "Database connection timeout"
- **Solution**: Check Neon database status (may be suspended), verify connection string format

**Issue**: "Module not found" errors
- **Solution**: Run `pip install -r requirements.txt` (backend) or `npm install` (frontend)

**Issue**: "Port already in use"
- **Solution**: Check what's using the port:
  ```bash
  # macOS/Linux
  lsof -i :8000  # Backend
  lsof -i :3000  # Frontend

  # Windows
  netstat -ano | findstr :8000
  ```

For more detailed troubleshooting, see:
- [Local Development Guide](./docs/LOCAL_DEVELOPMENT.md#troubleshooting)
- [Vercel Deployment Guide](./docs/VERCEL_DEPLOYMENT.md#故障排查)
- [Production Deployment Guide](./docs/PRODUCTION_DEPLOYMENT.md#故障排查)

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 (Python) and ESLint (TypeScript)
- Add unit tests for new features
- Update documentation
- Ensure all tests pass

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [DeepSeek](https://www.deepseek.com/) - Cost-effective AI models
- [OpenAI](https://openai.com/) - Fallback model support
- [Tavily](https://tavily.com/) - Search API
- [Vercel](https://vercel.com/) - Next.js and deployment platform
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [aisuite](https://github.com/andrewyng/aisuite) - Unified AI API interface

---

## 📞 Contact

- **Repository**: https://github.com/ameureka/ai-deepresearch-agent
- **Issues**: https://github.com/ameureka/ai-deepresearch-agent/issues
- **Documentation**: https://github.com/ameureka/ai-deepresearch-agent/tree/main/docs

---

**Made with ❤️ by the AI DeepResearch Team**

**Version**: 0.2.0 (Phase 4) | **Last Updated**: 2025-10-31
