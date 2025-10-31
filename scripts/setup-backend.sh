#!/bin/bash

# ============================================================================
# Backend Environment Setup Script
# Phase 4 Deployment - Week 1 Day 3
# ============================================================================

set -e

echo "🚀 Setting up backend environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Step 1: Check Python Version
# ============================================================================

echo "📦 Step 1: Checking Python version..."
echo ""

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.11 or higher"
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}✅ Python version: $PYTHON_VERSION${NC}"
echo ""

# Check if version is >= 3.11
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${YELLOW}⚠️  Warning: Python 3.11+ is recommended (found $PYTHON_VERSION)${NC}"
    echo ""
fi

# ============================================================================
# Step 2: Create Virtual Environment
# ============================================================================

echo "🔧 Step 2: Creating Python virtual environment..."
echo ""

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "Skipping virtual environment creation"
        echo ""
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created: $VENV_DIR${NC}"
else
    echo -e "${GREEN}✅ Using existing virtual environment${NC}"
fi

echo ""

# ============================================================================
# Step 3: Activate Virtual Environment
# ============================================================================

echo "🔌 Step 3: Activating virtual environment..."
echo ""

source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo "   Python: $(which python)"
echo "   Version: $(python --version)"
echo ""

# ============================================================================
# Step 4: Upgrade pip
# ============================================================================

echo "📦 Step 4: Upgrading pip..."
echo ""

pip install --upgrade pip --quiet

echo -e "${GREEN}✅ pip upgraded to version $(pip --version | awk '{print $2}')${NC}"
echo ""

# ============================================================================
# Step 5: Install Dependencies
# ============================================================================

echo "📦 Step 5: Installing dependencies from requirements.txt..."
echo ""

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

echo "This may take a few minutes..."
pip install -r requirements.txt

echo ""
echo -e "${GREEN}✅ All dependencies installed successfully${NC}"
echo ""

# ============================================================================
# Step 6: Check Environment Variables
# ============================================================================

echo "🔍 Step 6: Checking environment variables..."
echo ""

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo ""
    echo "Creating .env from .env.example..."

    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Please edit .env and add your API keys:${NC}"
        echo "   - DEEPSEEK_API_KEY"
        echo "   - OPENAI_API_KEY"
        echo "   - TAVILY_API_KEY"
        echo "   - DATABASE_URL"
        echo ""
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
fi

# Load .env file
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Check required variables
REQUIRED_VARS=("DEEPSEEK_API_KEY" "OPENAI_API_KEY" "TAVILY_API_KEY" "DATABASE_URL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please edit .env and add the missing variables"
    exit 1
else
    echo -e "${GREEN}✅ All required environment variables are set${NC}"
fi

echo ""

# ============================================================================
# Step 7: Test Database Connection
# ============================================================================

echo "🔍 Step 7: Testing database connection..."
echo ""

python -c "
import sys
try:
    import psycopg2
    from os import getenv

    db_url = getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL not set')
        sys.exit(1)

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f'✅ Database connection successful')
    print(f'   PostgreSQL version: {version.split(\",\")[0]}')
    conn.close()
except ImportError:
    print('⚠️  psycopg2 not installed, skipping database test')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
" || true

echo ""

# ============================================================================
# Step 8: Verify Installation
# ============================================================================

echo "🔍 Step 8: Verifying installation..."
echo ""

# Check critical packages
CRITICAL_PACKAGES=("fastapi" "uvicorn" "sqlalchemy" "aisuite")

for package in "${CRITICAL_PACKAGES[@]}"; do
    if pip show "$package" &> /dev/null; then
        VERSION=$(pip show "$package" | grep Version | awk '{print $2}')
        echo -e "${GREEN}✅ $package ($VERSION)${NC}"
    else
        echo -e "${RED}❌ $package not installed${NC}"
    fi
done

echo ""

# ============================================================================
# Summary
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✨ Backend environment setup completed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Configure .env with your API keys (if not done)"
echo "  3. Start backend server: uvicorn main:app --reload --port 8000"
echo "  4. Visit API docs: http://localhost:8000/docs"
echo ""
echo "To deactivate virtual environment later: deactivate"
echo ""
