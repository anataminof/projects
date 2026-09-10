#!/bin/bash

# Job Search System - Local Development Server Starter
# Starts both backend (FastAPI) and frontend (Vite) dev servers

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🚀 Starting Job Search System (Local Development)"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to kill process on port
kill_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Killing existing process on port $port...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Clean up on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    # Kill background jobs
    jobs -p | xargs -r kill 2>/dev/null || true
}

trap cleanup EXIT INT TERM

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Kill any existing processes on required ports
echo -e "${BLUE}📍 Checking ports...${NC}"
kill_port 8000
kill_port 5173
echo ""

# Start Backend
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
cd "$BACKEND_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv and start backend
source venv/bin/activate
echo -e "${GREEN}✓ Backend virtual environment activated${NC}"

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -e . -q
fi

echo -e "${GREEN}✓ Backend dependencies ready${NC}"
echo ""
echo -e "${GREEN}📡 Backend running on http://localhost:8000${NC}"
echo -e "${GREEN}📚 API docs at http://localhost:8000/docs${NC}"
echo ""

# Start backend in background
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Start Frontend
echo -e "${BLUE}⚛️  Starting Frontend (Vite)...${NC}"
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install -q
fi

echo -e "${GREEN}✓ Frontend dependencies ready${NC}"
echo ""
echo -e "${GREEN}🌐 Frontend running on http://localhost:5173${NC}"
echo ""

# Start frontend in background
npm run dev &
FRONTEND_PID=$!

# Give frontend time to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

# Print summary
echo -e "${GREEN}=================================================="
echo "✅ Both services are running!"
echo "=================================================${NC}"
echo ""
echo -e "${BLUE}Backend:${NC}  http://localhost:8000"
echo -e "${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
