#!/bin/bash

# ============================================================================
# Environment Variables Validation Script
# Phase 4 Deployment - Week 1 Day 2
# ============================================================================

set -e

echo "🔍 Checking environment variables configuration..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
MISSING=0
CONFIGURED=0

# ============================================================================
# Backend Environment Variables
# ============================================================================

echo "📦 Checking backend environment variables..."
echo ""

# Required backend variables
REQUIRED_BACKEND=(
  "DEEPSEEK_API_KEY"
  "OPENAI_API_KEY"
  "TAVILY_API_KEY"
  "DATABASE_URL"
)

# Optional backend variables
OPTIONAL_BACKEND=(
  "HOST"
  "PORT"
  "WORKERS"
  "LOG_LEVEL"
  "ALLOWED_ORIGINS"
  "PLANNER_MODEL"
  "RESEARCHER_MODEL"
  "WRITER_MODEL"
  "EDITOR_MODEL"
  "FALLBACK_MODEL"
  "ENABLE_CHUNKING"
  "CHUNKING_THRESHOLD"
  "MAX_CHUNK_SIZE"
  "CHUNK_OVERLAP"
)

# Check required backend variables
for var in "${REQUIRED_BACKEND[@]}"; do
  if [ -z "${!var}" ]; then
    echo -e "${RED}❌ Missing (required): $var${NC}"
    MISSING=$((MISSING + 1))
  else
    # Mask sensitive values
    if [[ $var == *"KEY"* ]] || [[ $var == *"SECRET"* ]] || [[ $var == *"URL"* ]]; then
      VALUE="${!var:0:10}..."
    else
      VALUE="${!var}"
    fi
    echo -e "${GREEN}✅ Configured: $var = $VALUE${NC}"
    CONFIGURED=$((CONFIGURED + 1))
  fi
done

echo ""

# Check optional backend variables
for var in "${OPTIONAL_BACKEND[@]}"; do
  if [ -z "${!var}" ]; then
    echo -e "${YELLOW}⚠️  Optional (not set): $var${NC}"
  else
    echo -e "${GREEN}✅ Configured: $var = ${!var}${NC}"
    CONFIGURED=$((CONFIGURED + 1))
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================================
# Frontend Environment Variables
# ============================================================================

echo "🎨 Checking frontend environment variables..."
echo ""

# Check if frontend directory exists
if [ ! -d "ai-chatbot-main" ]; then
  echo -e "${RED}❌ Frontend directory 'ai-chatbot-main' not found${NC}"
  exit 1
fi

cd ai-chatbot-main

# Load frontend .env.local if exists
if [ -f ".env.local" ]; then
  set -a
  source .env.local
  set +a
  echo -e "${GREEN}✅ Loaded .env.local${NC}"
  echo ""
fi

# Required frontend variables
REQUIRED_FRONTEND=(
  "POSTGRES_URL"
  "AUTH_SECRET"
)

# Optional frontend variables
OPTIONAL_FRONTEND=(
  "RESEARCH_API_URL"
  "NEXT_PUBLIC_API_URL"
  "BLOB_READ_WRITE_TOKEN"
  "AI_GATEWAY_API_KEY"
  "OPENAI_API_KEY"
  "NODE_ENV"
  "NEXTAUTH_URL"
)

# Check required frontend variables
for var in "${REQUIRED_FRONTEND[@]}"; do
  if [ -z "${!var}" ]; then
    echo -e "${RED}❌ Missing (required): $var${NC}"
    MISSING=$((MISSING + 1))
  else
    # Mask sensitive values
    if [[ $var == *"KEY"* ]] || [[ $var == *"SECRET"* ]] || [[ $var == *"URL"* ]]; then
      VALUE="${!var:0:10}..."
    else
      VALUE="${!var}"
    fi
    echo -e "${GREEN}✅ Configured: $var = $VALUE${NC}"
    CONFIGURED=$((CONFIGURED + 1))
  fi
done

echo ""

# Check optional frontend variables
for var in "${OPTIONAL_FRONTEND[@]}"; do
  if [ -z "${!var}" ]; then
    echo -e "${YELLOW}⚠️  Optional (not set): $var${NC}"
  else
    # Mask sensitive values
    if [[ $var == *"KEY"* ]] || [[ $var == *"SECRET"* ]] || [[ $var == *"TOKEN"* ]]; then
      VALUE="${!var:0:10}..."
    else
      VALUE="${!var}"
    fi
    echo -e "${GREEN}✅ Configured: $var = $VALUE${NC}"
    CONFIGURED=$((CONFIGURED + 1))
  fi
done

cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================================
# Summary
# ============================================================================

echo "📊 Summary:"
echo "   - Configured: $CONFIGURED"
echo "   - Missing: $MISSING"
echo ""

if [ $MISSING -eq 0 ]; then
  echo -e "${GREEN}✨ All required environment variables are configured!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Start PostgreSQL: docker-compose up -d postgres"
  echo "  2. Start backend: uvicorn main:app --reload"
  echo "  3. Start frontend: cd ai-chatbot-main && npm run dev"
  exit 0
else
  echo -e "${RED}❌ $MISSING required environment variable(s) are missing!${NC}"
  echo ""
  echo "Please configure missing variables:"
  echo "  1. Copy .env.example to .env"
  echo "  2. Copy ai-chatbot-main/.env.example to ai-chatbot-main/.env.local"
  echo "  3. Fill in your API keys and credentials"
  echo "  4. Run this script again to verify"
  exit 1
fi
