#!/bin/bash

# ============================================================================
# Development Startup Script
# Phase 4 Deployment - Start all services for local development
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# Configuration
# ============================================================================

BACKEND_PORT=8000
FRONTEND_PORT=3000
LOG_DIR="logs"

# ============================================================================
# Functions
# ============================================================================

# Print banner
print_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                          ║${NC}"
    echo -e "${CYAN}║           AI DeepResearch Agent - Dev Server            ║${NC}"
    echo -e "${CYAN}║                                                          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        echo "Please stop the service using this port or choose a different port"
        return 1
    fi
    return 0
}

# Create logs directory
create_logs_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        echo -e "${GREEN}✅ Created logs directory${NC}"
    fi
}

# Check environment variables
check_env() {
    echo -e "${BLUE}🔍 Checking environment variables...${NC}"
    echo ""

    # Check backend .env
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ Backend .env file not found${NC}"
        echo "Run: cp .env.example .env"
        echo "Then edit .env with your API keys"
        exit 1
    fi

    # Check frontend .env.local
    if [ ! -f "ai-chatbot-main/.env.local" ]; then
        echo -e "${RED}❌ Frontend .env.local file not found${NC}"
        echo "Run: cp ai-chatbot-main/.env.local.example ai-chatbot-main/.env.local"
        echo "Then edit .env.local with your credentials"
        exit 1
    fi

    echo -e "${GREEN}✅ Environment files found${NC}"
    echo ""
}

# Check dependencies
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    echo ""

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python $(python3 --version | awk '{print $2}')${NC}"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js $(node --version)${NC}"

    # Check backend venv
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Backend virtual environment not found${NC}"
        echo "Run: ./scripts/setup-backend.sh"
        exit 1
    fi
    echo -e "${GREEN}✅ Backend virtual environment${NC}"

    # Check frontend node_modules
    if [ ! -d "ai-chatbot-main/node_modules" ]; then
        echo -e "${YELLOW}⚠️  Frontend dependencies not installed${NC}"
        echo "Run: ./scripts/setup-frontend.sh"
        exit 1
    fi
    echo -e "${GREEN}✅ Frontend dependencies${NC}"

    echo ""
}

# Start backend
start_backend() {
    echo -e "${BLUE}🚀 Starting backend server on port $BACKEND_PORT...${NC}"
    echo ""

    # Activate virtual environment and start uvicorn
    source venv/bin/activate

    # Start backend in background
    nohup uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT \
        > "$LOG_DIR/backend.log" 2>&1 &

    BACKEND_PID=$!
    echo $BACKEND_PID > "$LOG_DIR/backend.pid"

    echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    echo "   URL: http://localhost:$BACKEND_PORT"
    echo "   Docs: http://localhost:$BACKEND_PORT/docs"
    echo "   Logs: $LOG_DIR/backend.log"
    echo ""

    # Wait for backend to be ready
    echo "⏳ Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is ready!${NC}"
            echo ""
            return 0
        fi
        sleep 1
    done

    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check logs: tail -f $LOG_DIR/backend.log"
    exit 1
}

# Start frontend
start_frontend() {
    echo -e "${BLUE}🚀 Starting frontend server on port $FRONTEND_PORT...${NC}"
    echo ""

    cd ai-chatbot-main

    # Detect package manager
    if [ -f "pnpm-lock.yaml" ]; then
        PACKAGE_MANAGER="pnpm"
    else
        PACKAGE_MANAGER="npm"
    fi

    # Start frontend in background
    nohup $PACKAGE_MANAGER run dev --port $FRONTEND_PORT \
        > "../$LOG_DIR/frontend.log" 2>&1 &

    FRONTEND_PID=$!
    echo $FRONTEND_PID > "../$LOG_DIR/frontend.pid"

    cd ..

    echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo "   URL: http://localhost:$FRONTEND_PORT"
    echo "   Logs: $LOG_DIR/frontend.log"
    echo ""

    # Wait for frontend to be ready
    echo "⏳ Waiting for frontend to be ready..."
    for i in {1..60}; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend is ready!${NC}"
            echo ""
            return 0
        fi
        sleep 1
    done

    echo -e "${YELLOW}⚠️  Frontend is taking longer than expected${NC}"
    echo "It may still be starting. Check logs: tail -f $LOG_DIR/frontend.log"
    echo ""
}

# Print status
print_status() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${GREEN}✨ All services are running!${NC}"
    echo ""
    echo "Services:"
    echo "  • Backend:  http://localhost:$BACKEND_PORT"
    echo "  • Frontend: http://localhost:$FRONTEND_PORT"
    echo ""
    echo "API Documentation:"
    echo "  • Swagger UI: http://localhost:$BACKEND_PORT/docs"
    echo "  • ReDoc:      http://localhost:$BACKEND_PORT/redoc"
    echo ""
    echo "Logs:"
    echo "  • Backend:  tail -f $LOG_DIR/backend.log"
    echo "  • Frontend: tail -f $LOG_DIR/frontend.log"
    echo ""
    echo "To stop all services:"
    echo "  ./scripts/stop-dev.sh"
    echo ""
    echo "Press Ctrl+C to stop monitoring logs"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Monitor logs
monitor_logs() {
    # Trap Ctrl+C
    trap 'echo ""; echo "Logs stopped. Services are still running."; echo "Use ./scripts/stop-dev.sh to stop services."; exit 0' INT

    # Show combined logs
    tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
}

# Cleanup on exit
cleanup() {
    echo ""
    echo "Cleaning up..."
}

trap cleanup EXIT

# ============================================================================
# Main Execution
# ============================================================================

print_banner

# Check if ports are available
check_port $BACKEND_PORT || exit 1
check_port $FRONTEND_PORT || exit 1

# Create logs directory
create_logs_dir

# Check environment and dependencies
check_env
check_dependencies

# Start services
start_backend
start_frontend

# Print status
print_status

# Monitor logs
monitor_logs
