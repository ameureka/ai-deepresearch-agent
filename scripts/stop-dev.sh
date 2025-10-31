#!/bin/bash

# ============================================================================
# Stop Development Services Script
# Phase 4 Deployment - Stop all running development services
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_DIR="logs"

echo ""
echo "🛑 Stopping development services..."
echo ""

# Stop backend
if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✅ Backend stopped (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend was not running${NC}"
    fi
    rm "$LOG_DIR/backend.pid"
else
    echo -e "${YELLOW}⚠️  Backend PID file not found${NC}"
fi

# Stop frontend
if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ Frontend stopped (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend was not running${NC}"
    fi
    rm "$LOG_DIR/frontend.pid"
else
    echo -e "${YELLOW}⚠️  Frontend PID file not found${NC}"
fi

# Kill any remaining processes on ports 8000 and 3000
echo ""
echo "Checking for any remaining processes on ports 8000 and 3000..."

# Port 8000 (backend)
BACKEND_PROCS=$(lsof -ti:8000)
if [ ! -z "$BACKEND_PROCS" ]; then
    echo "Killing processes on port 8000: $BACKEND_PROCS"
    kill -9 $BACKEND_PROCS 2>/dev/null || true
fi

# Port 3000 (frontend)
FRONTEND_PROCS=$(lsof -ti:3000)
if [ ! -z "$FRONTEND_PROCS" ]; then
    echo "Killing processes on port 3000: $FRONTEND_PROCS"
    kill -9 $FRONTEND_PROCS 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✨ All services stopped${NC}"
echo ""
