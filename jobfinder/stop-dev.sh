#!/bin/bash

# Job Search System - Stop Development Services
# Kills backend and frontend dev servers

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Stopping Job Search System services...${NC}"
echo ""

# Kill processes on ports
stop_port() {
    local port=$1
    local name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Stopping $name (port $port)...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ $name stopped${NC}"
    else
        echo -e "${GREEN}✓ $name not running${NC}"
    fi
}

stop_port 8000 "Backend"
stop_port 5173 "Frontend"

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
