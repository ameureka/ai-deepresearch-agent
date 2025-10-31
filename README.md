# AI DeepResearch Agent

English | [简体中文](./README.zh-CN.md)

> 🚀 **Intelligent Research System** - Full-stack AI research platform with integrated Next.js frontend and FastAPI backend

A production-ready AI research assistant featuring a modern Next.js frontend with real-time research progress tracking and a FastAPI backend powered by multiple specialized agents (Planner, Researcher, Writer, Editor).

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/ameureka/ai-deepresearch-agent)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/next.js-15.3-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 🎯 Features

### ✨ Full-Stack Integration (Phase 3 & 4)
- **Modern UI**: Next.js 15 with App Router and Server Components
- **Real-Time Updates**: SSE-based research progress streaming
- **Responsive Design**: Mobile-first with sticky research panel
- **User-Triggered Research**: Seamless AI-to-research workflow
- **Production Ready**: Docker Compose orchestration for all services

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
├── ai-chatbot-main/              # Next.js Frontend
│   ├── app/                      # Next.js App Router
│   ├── components/               # React Components
│   │   ├── chat.tsx             # Main chat interface
│   │   ├── research-button.tsx  # Research trigger button
│   │   ├── research-panel.tsx   # Research UI container
│   │   └── research-progress.tsx # Real-time progress display
│   ├── hooks/                    # React Hooks
│   │   └── use-research-progress.ts # SSE research hook
│   ├── lib/                      # Utilities
│   │   └── research-utils.ts    # Keyword detection
│   └── playwright/               # E2E Tests
├── src/                          # FastAPI Backend
│   ├── planning_agent.py         # Task planning and execution
│   ├── agents.py                 # Research/Writer/Editor agents
│   ├── research_tools.py         # Search tools integration
│   ├── model_adapter.py          # Model parameter adaptation
│   ├── chunking.py               # Text chunking processor
│   └── context_manager.py        # Context management
├── main.py                       # FastAPI entry point
├── Dockerfile.backend            # Backend Docker configuration
├── docker-compose.yml            # Multi-service orchestration
└── README.md                     # This file
```

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (Port 3000)             │
│  - Modern React UI with App Router                           │
│  - Real-time SSE streaming (fetch-event-source)              │
│  - ResearchPanel with sticky positioning                     │
│  - useResearchProgress Hook                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (Port 8000)                   │
│  - REST API Endpoints                                        │
│  - SSE Research Streaming (/api/research/stream)             │
│  - Background Task Management                                │
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
│             PostgreSQL Database (Port 5432)                  │
│  - Task state management                                     │
│  - Research results storage                                  │
│  - Cost tracking records                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
- **API Keys**:
  - [DeepSeek API Key](https://platform.deepseek.com/)
  - [OpenAI API Key](https://platform.openai.com/)
  - [Tavily API Key](https://tavily.com/)

### Method A: Docker Compose (Recommended)

#### 1. Clone Repository

```bash
git clone https://github.com/ameureka/ai-deepresearch-agent.git
cd ai-deepresearch-agent
```

#### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:

```bash
# API Keys
DEEPSEEK_API_KEY=sk-your-deepseek-key
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key

# Database (PostgreSQL in Docker)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_research

# Auth
AUTH_SECRET=your-random-secret-key
```

#### 3. Start All Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### 5. Stop Services

```bash
docker-compose down        # Stop services
docker-compose down -v     # Stop and remove volumes
```

### Method B: Direct Run (Development)

#### Terminal 1: PostgreSQL

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
psql postgres -c "CREATE DATABASE ai_research;"
```

#### Terminal 2: FastAPI Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_research
export DEEPSEEK_API_KEY=sk-your-key
export TAVILY_API_KEY=tvly-your-key

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 3: Next.js Frontend

```bash
# Install Node.js dependencies
cd ai-chatbot-main
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API keys

# Start frontend
npm run dev
```

Access: http://localhost:3000

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
npm test

# E2E tests (Phase 3 updated)
npx playwright test

# Interactive E2E
npx playwright test --ui
```

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

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_research

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
```

### Frontend Configuration (.env.local)

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth
AUTH_SECRET=your-secret-key
AUTH_URL=http://localhost:3000/api/auth

# AI SDK
OPENAI_API_KEY=sk-your-key

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

### v0.2.0 - Phase 4 Deployment (2025-10-31)
- ✅ Monorepo structure (frontend + backend at same level)
- ✅ Docker Compose multi-service orchestration
- ✅ Production-ready configuration
- ✅ Updated .gitignore for Phase 4
- ✅ Unified README documentation

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
- [Docker Compose Setup](./.kiro/specs/phase4-deployment/design.md)
- [E2E Testing Guide](./.kiro/specs/phase4-deployment/requirements.md)
- [Deployment Checklist](./.kiro/specs/phase4-deployment/tasks.md)

---

## 🐛 Troubleshooting

### Docker Compose Issues

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Rebuild services
docker-compose build --no-cache

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Access PostgreSQL shell
docker-compose exec postgres psql -U postgres -d ai_research

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Frontend Build Issues

```bash
cd ai-chatbot-main

# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

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
