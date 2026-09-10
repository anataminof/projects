#!/bin/bash
# Start the dev stack (backend + frontend) with the local Ollama AI provider.
# Also boots the Ollama server and pulls the configured model if needed.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/dev-lib.sh
source "$ROOT/scripts/dev-lib.sh"

echo "🚀 Job Search System — Dev (AI provider: Ollama)"
echo "================================================"
echo ""

load_env_local
export AI_PROVIDER=ollama

trap 'dev_cleanup; stop_ollama' EXIT INT TERM

start_ollama
start_stack
