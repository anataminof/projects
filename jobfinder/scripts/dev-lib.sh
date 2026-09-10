#!/bin/bash
# Shared helpers for the start-dev-* / stop-dev-* scripts.
#
# Not executable on its own — each provider script does:
#   source "$(dirname "$0")/scripts/dev-lib.sh"

DEV_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$DEV_LIB_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
OLLAMA_PID_FILE="$PROJECT_ROOT/.dev-ollama.pid"
OLLAMA_LOG_FILE="$PROJECT_ROOT/.dev-ollama.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${BLUE}$*${NC}"; }
ok()   { echo -e "${GREEN}$*${NC}"; }
warn() { echo -e "${YELLOW}$*${NC}"; }
err()  { echo -e "${RED}$*${NC}"; }

# --- .env.local -----------------------------------------------------------
# Load every assignment from .env.local into the environment. Provider scripts
# call this first, then force their own AI_PROVIDER.
load_env_local() {
    local f="$PROJECT_ROOT/.env.local"
    if [ -f "$f" ]; then
        log "📄 Loading .env.local"
        set -a
        # shellcheck disable=SC1090
        source "$f"
        set +a
    else
        warn "⚠️  No .env.local — using built-in defaults."
        warn "   Create it with:  cp .env.local.example .env.local"
    fi

    # Defaults for anything .env.local did not set.
    AI_PROVIDER="${AI_PROVIDER:-ollama}"
    OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1}"
    OLLAMA_PORT="${OLLAMA_PORT:-11434}"
    OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://${OLLAMA_HOST}:${OLLAMA_PORT}}"
    OLLAMA_MODEL="${OLLAMA_MODEL:-mistral:7b}"
    OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"
    BACKEND_PORT="${BACKEND_PORT:-8000}"
    FRONTEND_PORT="${FRONTEND_PORT:-5173}"
    export AI_PROVIDER OLLAMA_BASE_URL OLLAMA_MODEL OPENAI_MODEL \
           OPENAI_API_KEY OPENAI_BASE_URL BACKEND_PORT FRONTEND_PORT
}

kill_port() {
    local port=$1
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        warn "⚠️  Killing existing process on port $port..."
        lsof -ti:"$port" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# --- Ollama --------------------------------------------------------------
ollama_running() {
    curl -sf "http://${OLLAMA_HOST}:${OLLAMA_PORT}/api/version" >/dev/null 2>&1
}

start_ollama() {
    local model="${OLLAMA_MODEL:-mistral:7b}"

    if ! command -v ollama >/dev/null 2>&1; then
        err "❌ 'ollama' not found on PATH. Install it first: https://ollama.com/download"
        exit 1
    fi

    if ollama_running; then
        ok "✓ Ollama already running on ${OLLAMA_HOST}:${OLLAMA_PORT}"
    else
        log "🧠 Starting Ollama server..."
        nohup ollama serve >"$OLLAMA_LOG_FILE" 2>&1 &
        echo $! > "$OLLAMA_PID_FILE"
        local tries=0
        until ollama_running; do
            tries=$((tries + 1))
            if [ "$tries" -gt 30 ]; then
                err "❌ Ollama did not become ready (see $OLLAMA_LOG_FILE)"
                exit 1
            fi
            sleep 1
        done
        ok "✓ Ollama started (PID $(cat "$OLLAMA_PID_FILE"))"
    fi

    if ollama list 2>/dev/null | awk 'NR>1{print $1}' | grep -qx "$model"; then
        ok "✓ Model '$model' present"
    else
        warn "⬇️  Pulling Ollama model '$model' (first run may take several minutes)..."
        ollama pull "$model"
        ok "✓ Model '$model' ready"
    fi
}

# Stop Ollama only if these scripts started it (pid file present).
stop_ollama() {
    if [ -f "$OLLAMA_PID_FILE" ]; then
        local pid; pid="$(cat "$OLLAMA_PID_FILE" 2>/dev/null)"
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            warn "Stopping Ollama server (PID $pid, started by start-dev)..."
            kill "$pid" 2>/dev/null || true
            ok "✓ Ollama stopped"
        fi
        rm -f "$OLLAMA_PID_FILE"
    else
        ok "✓ Ollama left as-is (not started by these scripts)"
    fi
}

# --- Backend + Frontend ------------------------------------------------
start_stack() {
    [ -d "$BACKEND_DIR" ]  || { err "❌ Backend dir not found: $BACKEND_DIR"; exit 1; }
    [ -d "$FRONTEND_DIR" ] || { err "❌ Frontend dir not found: $FRONTEND_DIR"; exit 1; }

    log "📍 Freeing ports $BACKEND_PORT / $FRONTEND_PORT..."
    kill_port "$BACKEND_PORT"
    kill_port "$FRONTEND_PORT"

    log "🔧 Starting Backend (FastAPI) — AI_PROVIDER=$AI_PROVIDER"
    cd "$BACKEND_DIR"
    if [ ! -d venv ]; then
        warn "Creating virtual environment..."
        python3 -m venv venv
        # shellcheck disable=SC1091
        source venv/bin/activate
        pip install --upgrade pip -q   # editable installs from pyproject need a recent pip
    else
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    if ! python -c "import fastapi" 2>/dev/null; then
        warn "Installing backend dependencies..."
        pip install -e . -q
    fi
    # New optional deps (e.g. openai) — reinstall if missing.
    if [ "$AI_PROVIDER" = "openai" ] && ! python -c "import openai" 2>/dev/null; then
        warn "Installing OpenAI SDK..."
        pip install -e . -q
    fi
    ok "✓ Backend dependencies ready"

    uvicorn app.main:app --reload --port "$BACKEND_PORT" &
    BACKEND_PID=$!
    sleep 2
    kill -0 "$BACKEND_PID" 2>/dev/null || { err "❌ Backend failed to start"; exit 1; }
    ok "✅ Backend on http://localhost:$BACKEND_PORT (PID $BACKEND_PID)"

    log "⚛️  Starting Frontend (Vite)..."
    cd "$FRONTEND_DIR"
    [ -d node_modules ] || { warn "Installing frontend dependencies..."; npm install -q; }
    npm run dev &
    FRONTEND_PID=$!
    sleep 3
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        err "❌ Frontend failed to start"
        kill "$BACKEND_PID" 2>/dev/null || true
        exit 1
    fi
    ok "✅ Frontend on http://localhost:$FRONTEND_PORT (PID $FRONTEND_PID)"

    echo ""
    ok "=================================================="
    ok "✅ Dev stack running — AI provider: $AI_PROVIDER"
    [ "$AI_PROVIDER" = "ollama" ] && ok "   Ollama:  $OLLAMA_BASE_URL  ($OLLAMA_MODEL)"
    [ "$AI_PROVIDER" = "openai" ] && ok "   OpenAI:  model $OPENAI_MODEL"
    ok "=================================================="
    echo -e "${BLUE}Backend:${NC}  http://localhost:$BACKEND_PORT"
    echo -e "${BLUE}API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
    echo -e "${BLUE}Frontend:${NC} http://localhost:$FRONTEND_PORT"
    echo ""
    warn "Press Ctrl+C to stop backend + frontend"
    echo ""
    wait "$BACKEND_PID" "$FRONTEND_PID"
}

stop_stack() {
    _stop_port() {
        local port=$1 name=$2
        if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
            warn "Stopping $name (port $port)..."
            lsof -ti:"$port" | xargs kill -9 2>/dev/null || true
            ok "✓ $name stopped"
        else
            ok "✓ $name not running"
        fi
    }
    _stop_port "$BACKEND_PORT" "Backend"
    _stop_port "$FRONTEND_PORT" "Frontend"
}

dev_cleanup() {
    echo ""
    warn "Shutting down services..."
    jobs -p | xargs -r kill 2>/dev/null || true
}
