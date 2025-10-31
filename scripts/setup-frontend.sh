#!/bin/bash

# ============================================================================
# Frontend Environment Setup Script
# Phase 4 Deployment - Week 1 Day 3
# ============================================================================

set -e

echo "🚀 Setting up frontend environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Step 1: Check Node.js Version
# ============================================================================

echo "📦 Step 1: Checking Node.js version..."
echo ""

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18 or higher"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | sed 's/v//')
NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)

echo -e "${GREEN}✅ Node.js version: v$NODE_VERSION${NC}"
echo ""

if [ "$NODE_MAJOR" -lt 18 ]; then
    echo -e "${RED}❌ Node.js 18+ is required (found v$NODE_VERSION)${NC}"
    exit 1
fi

# ============================================================================
# Step 2: Check Package Manager
# ============================================================================

echo "📦 Step 2: Checking package manager..."
echo ""

if command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
    echo -e "${GREEN}✅ Using pnpm $(pnpm --version)${NC}"
elif command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
    echo -e "${GREEN}✅ Using npm $(npm --version)${NC}"
else
    echo -e "${RED}❌ No package manager found${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Step 3: Navigate to Frontend Directory
# ============================================================================

echo "📂 Step 3: Navigating to frontend directory..."
echo ""

if [ ! -d "ai-chatbot-main" ]; then
    echo -e "${RED}❌ Frontend directory 'ai-chatbot-main' not found${NC}"
    exit 1
fi

cd ai-chatbot-main

echo -e "${GREEN}✅ In directory: $(pwd)${NC}"
echo ""

# ============================================================================
# Step 4: Check Environment Variables
# ============================================================================

echo "🔍 Step 4: Checking environment variables..."
echo ""

if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠️  .env.local file not found${NC}"
    echo ""
    echo "Creating .env.local from .env.local.example..."

    if [ -f ".env.local.example" ]; then
        cp .env.local.example .env.local
        echo -e "${GREEN}✅ Created .env.local file${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Please edit ai-chatbot-main/.env.local and add:${NC}"
        echo "   - POSTGRES_URL (database connection string)"
        echo "   - AUTH_SECRET (run: openssl rand -base64 32)"
        echo "   - RESEARCH_API_URL (backend URL, default: http://localhost:8000)"
        echo ""
    elif [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo -e "${GREEN}✅ Created .env.local from .env.example${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Please edit ai-chatbot-main/.env.local${NC}"
        echo ""
    else
        echo -e "${RED}❌ No .env template found${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment file exists${NC}"
echo ""

# ============================================================================
# Step 5: Install Dependencies
# ============================================================================

echo "📦 Step 5: Installing frontend dependencies..."
echo ""

if [ "$PACKAGE_MANAGER" = "pnpm" ]; then
    pnpm install
else
    npm install
fi

echo ""
echo -e "${GREEN}✅ All frontend dependencies installed${NC}"
echo ""

# ============================================================================
# Step 6: Verify Installation
# ============================================================================

echo "🔍 Step 6: Verifying installation..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${RED}❌ node_modules directory not found${NC}"
    exit 1
fi

# Check critical packages
CRITICAL_PACKAGES=("next" "react" "ai" "@ai-sdk/react")

for package in "${CRITICAL_PACKAGES[@]}"; do
    if [ -d "node_modules/$package" ]; then
        echo -e "${GREEN}✅ $package${NC}"
    else
        echo -e "${RED}❌ $package not installed${NC}"
    fi
done

echo ""

# ============================================================================
# Step 7: Check TypeScript Configuration
# ============================================================================

echo "🔍 Step 7: Checking TypeScript configuration..."
echo ""

if [ -f "tsconfig.json" ]; then
    echo -e "${GREEN}✅ tsconfig.json found${NC}"
else
    echo -e "${YELLOW}⚠️  tsconfig.json not found${NC}"
fi

echo ""

cd ..

# ============================================================================
# Summary
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✨ Frontend environment setup completed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure ai-chatbot-main/.env.local with your credentials"
echo "  2. Start frontend: cd ai-chatbot-main && npm run dev"
echo "  3. Visit: http://localhost:3000"
echo ""
echo "Optional:"
echo "  - Run database migrations: cd ai-chatbot-main && npm run db:migrate"
echo "  - View database: cd ai-chatbot-main && npm run db:studio"
echo ""
