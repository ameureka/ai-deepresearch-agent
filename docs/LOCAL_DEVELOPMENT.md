# Local Development Guide

## Overview

This guide explains how to set up and run the AI DeepResearch Agent locally for development. We provide automated scripts for quick setup and manual steps for those who prefer more control.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Automated)](#quick-start-automated)
- [Manual Setup](#manual-setup)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL Database** - Choose one:
  - Local PostgreSQL 15+
  - Docker for PostgreSQL
  - Neon (SaaS) - [Sign up](https://neon.tech/)

### Required API Keys

You'll need API keys from:

- **DeepSeek** - [Get key](https://platform.deepseek.com/)
- **OpenAI** - [Get key](https://platform.openai.com/)
- **Tavily** - [Get key](https://tavily.com/)

---

## Quick Start (Automated)

### 1. Clone and Navigate

```bash
git clone https://github.com/ameureka/ai-deepresearch-agent.git
cd ai-deepresearch-agent
```

### 2. Configure Environment

```bash
# Backend configuration
cp .env.example .env
nano .env  # Add your API keys

# Frontend configuration
cp ai-chatbot-main/.env.local.example ai-chatbot-main/.env.local
nano ai-chatbot-main/.env.local  # Add your credentials
```

### 3. Run Setup Scripts

```bash
# Setup backend (creates venv, installs dependencies)
./scripts/setup-backend.sh

# Setup frontend (installs npm packages)
./scripts/setup-frontend.sh
```

### 4. Start All Services

```bash
# Start backend and frontend together
./scripts/dev.sh
```

This will:
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:3000
- ✅ Monitor logs in real-time

### 5. Stop Services

```bash
# In another terminal
./scripts/stop-dev.sh
```

---

## Manual Setup

If you prefer to set up services manually or need more control:

### Backend Setup

#### 1. Create Virtual Environment

```bash
# In project root
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Copy example and edit
cp .env.example .env

# Add your API keys
DEEPSEEK_API_KEY=sk-your-key
OPENAI_API_KEY=sk-your-key
TAVILY_API_KEY=tvly-your-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

#### 4. Test Configuration

```bash
# Verify environment variables
./scripts/check-env.sh

# Test database connection
python -c "
from src.config import get_config
config = get_config()
print('✅ Backend configuration loaded')
"
```

### Frontend Setup

#### 1. Navigate to Frontend

```bash
cd ai-chatbot-main
```

#### 2. Install Dependencies

```bash
# Using npm
npm install

# Or using pnpm (if installed)
pnpm install
```

#### 3. Configure Environment

```bash
# Copy example and edit
cp .env.local.example .env.local

# Add your credentials
POSTGRES_URL=postgresql://user:pass@host:5432/dbname
AUTH_SECRET=$(openssl rand -base64 32)
RESEARCH_API_URL=http://localhost:8000
```

#### 4. Run Database Migrations

```bash
# Generate migration files (if schema changed)
npm run db:generate

# Apply migrations
npm run db:migrate

# Or push schema directly (development)
npm run db:push
```

#### 5. Verify Setup

```bash
# Check TypeScript compilation
npx tsc --noEmit

# View database
npm run db:studio
```

---

## Running the Application

### Method 1: Automated (Recommended)

```bash
# From project root
./scripts/dev.sh
```

This starts both services and shows combined logs.

### Method 2: Separate Terminals

#### Terminal 1: Backend

```bash
# From project root
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Frontend

```bash
# From project root
cd ai-chatbot-main
npm run dev
```

### Method 3: Background Processes

```bash
# Start backend in background
source venv/bin/activate
nohup uvicorn main:app --reload --port 8000 > backend.log 2>&1 &

# Start frontend in background
cd ai-chatbot-main
nohup npm run dev > frontend.log 2>&1 &

# Monitor logs
tail -f backend.log frontend.log
```

---

## Development Workflow

### Daily Workflow

1. **Start services**
   ```bash
   ./scripts/dev.sh
   ```

2. **Open in browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

3. **Make changes**
   - Backend changes auto-reload (uvicorn --reload)
   - Frontend changes auto-reload (Next.js dev)

4. **Test changes**
   - Use browser DevTools
   - Check backend logs
   - Run unit tests

5. **Stop services**
   ```bash
   ./scripts/stop-dev.sh
   ```

### Common Tasks

#### Update Dependencies

```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ai-chatbot-main
npm install
```

#### Database Migrations

```bash
cd ai-chatbot-main

# Create new migration
npm run db:generate

# Apply migrations
npm run db:migrate

# View database
npm run db:studio
```

#### Run Tests

```bash
# Backend tests
PYTHONPATH=. pytest tests/ -v

# Frontend tests
cd ai-chatbot-main
npm test

# E2E tests
cd ai-chatbot-main
npx playwright test
```

#### Check Code Quality

```bash
# Backend linting
ruff check src/
black src/

# Frontend linting
cd ai-chatbot-main
npm run lint
```

---

## Troubleshooting

### Backend Issues

#### Problem: "Port 8000 already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)

# Or use stop script
./scripts/stop-dev.sh
```

#### Problem: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Problem: "Database connection failed"

**Solution:**
```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
python -c "
import psycopg2
from os import getenv
conn = psycopg2.connect(getenv('DATABASE_URL'))
print('✅ Connection successful')
conn.close()
"

# For Neon, ensure SSL mode:
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

#### Problem: "API key invalid"

**Solution:**
```bash
# Verify API keys in .env
cat .env | grep API_KEY

# Check key format:
# DeepSeek: sk-xxx
# OpenAI: sk-proj-xxx or sk-xxx
# Tavily: tvly-xxx

# Regenerate keys if needed
```

### Frontend Issues

#### Problem: "Port 3000 already in use"

**Solution:**
```bash
# Kill process on port 3000
kill -9 $(lsof -ti:3000)

# Or change port
cd ai-chatbot-main
npm run dev -- --port 3001
```

#### Problem: "Cannot find module"

**Solution:**
```bash
cd ai-chatbot-main

# Clear cache
rm -rf .next node_modules

# Reinstall
npm install

# Rebuild
npm run build
```

#### Problem: "Database migration failed"

**Solution:**
```bash
cd ai-chatbot-main

# Check database connection
echo $POSTGRES_URL

# Reset database (WARNING: deletes data)
npm run db:push -- --force-reset

# Or apply migrations manually
npm run db:migrate
```

#### Problem: "CORS error in browser"

**Solution:**
```bash
# Check ALLOWED_ORIGINS in backend .env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Restart backend
./scripts/stop-dev.sh
./scripts/dev.sh
```

### Environment Variable Issues

#### Problem: "Environment variable not loading"

**Solution:**
```bash
# Verify file exists
ls -la .env ai-chatbot-main/.env.local

# Check syntax (no spaces around =)
cat .env

# Reload environment
source .env

# Run validation
./scripts/check-env.sh
```

#### Problem: "AUTH_SECRET missing"

**Solution:**
```bash
# Generate new secret
openssl rand -base64 32

# Add to ai-chatbot-main/.env.local
echo "AUTH_SECRET=$(openssl rand -base64 32)" >> ai-chatbot-main/.env.local
```

---

## Performance Tips

### Backend Optimization

1. **Use multiple workers (production)**
   ```bash
   uvicorn main:app --workers 4
   ```

2. **Enable response caching**
   - Implement Redis for API caching
   - Cache expensive operations

3. **Optimize database queries**
   - Use connection pooling
   - Add indexes to frequently queried fields

### Frontend Optimization

1. **Enable SWC compiler**
   - Already enabled in Next.js 15

2. **Use production build locally**
   ```bash
   cd ai-chatbot-main
   npm run build
   npm start
   ```

3. **Analyze bundle size**
   ```bash
   cd ai-chatbot-main
   npm run build
   # Check .next/analyze/
   ```

---

## Additional Resources

### Documentation

- [Environment Variables Guide](./ENVIRONMENT_VARIABLES.md)
- [Database Configuration](./DATABASE_CONFIGURATION.md)
- [API Documentation](http://localhost:8000/docs)
- [Phase 4 Design](../.kiro/specs/phase4-deployment/design.md)

### Scripts Reference

| Script | Purpose |
|--------|---------|
| `./scripts/setup-backend.sh` | Install backend dependencies |
| `./scripts/setup-frontend.sh` | Install frontend dependencies |
| `./scripts/dev.sh` | Start all services |
| `./scripts/stop-dev.sh` | Stop all services |
| `./scripts/check-env.sh` | Validate environment variables |

### Useful Commands

```bash
# Check Python packages
pip list

# Check Node packages
cd ai-chatbot-main && npm list

# View backend logs
tail -f logs/backend.log

# View frontend logs
tail -f logs/frontend.log

# Monitor database
cd ai-chatbot-main && npm run db:studio

# View API docs
open http://localhost:8000/docs
```

---

## Next Steps

After successfully running locally:

1. **Test Research Flow**
   - Create account
   - Start research task
   - Verify SSE streaming
   - Check report generation

2. **Review Phase 3 Architecture**
   - Read [Phase 3 Report](../.kiro/specs/phase3-nextjs-frontend/PHASE3_IMPLEMENTATION_REPORT.md)
   - Understand ResearchPanel integration
   - Review useResearchProgress hook

3. **Prepare for Docker**
   - Read [Docker Compose Guide](../.kiro/specs/phase4-deployment/design.md)
   - Understand service dependencies

4. **Plan Production Deployment**
   - Review [Deployment Requirements](../.kiro/specs/phase4-deployment/requirements.md)
   - Prepare Neon, Render, and Vercel accounts

---

## Support

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/ameureka/ai-deepresearch-agent/issues)
2. Review backend logs: `logs/backend.log`
3. Review frontend logs: `logs/frontend.log`
4. Run environment validation: `./scripts/check-env.sh`

---

**Happy Coding! 🚀**
