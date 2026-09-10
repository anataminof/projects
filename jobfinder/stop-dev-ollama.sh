#!/bin/bash
# Stop the dev stack started with the Ollama provider.
# Also stops the Ollama server, but only if start-dev started it.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/dev-lib.sh
source "$ROOT/scripts/dev-lib.sh"

echo "🛑 Stopping Job Search System (Ollama)..."
echo ""

load_env_local
stop_stack
stop_ollama

echo ""
ok "✅ All services stopped"
