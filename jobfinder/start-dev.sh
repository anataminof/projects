#!/bin/bash
# Start the dev stack (backend + frontend) using whichever AI provider is set
# as AI_PROVIDER in .env.local (ollama | openai | fake).
#
# For an explicit provider, use the dedicated scripts instead:
#   ./start-dev-ollama.sh   ./start-dev-openai.sh   ./start-dev-fake.sh
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/dev-lib.sh
source "$ROOT/scripts/dev-lib.sh"

load_env_local

echo "🚀 Job Search System — Dev (AI provider: $AI_PROVIDER)"
echo "=================================================="
echo ""

case "$AI_PROVIDER" in
    ollama)
        trap 'dev_cleanup; stop_ollama' EXIT INT TERM
        start_ollama
        ;;
    openai)
        if [ -z "${OPENAI_API_KEY:-}" ]; then
            err "❌ OPENAI_API_KEY is not set. Add it to .env.local and retry."
            exit 1
        fi
        trap dev_cleanup EXIT INT TERM
        ;;
    fake)
        trap dev_cleanup EXIT INT TERM
        ;;
    *)
        err "❌ Unknown AI_PROVIDER '$AI_PROVIDER' (expected: ollama | openai | fake)"
        exit 1
        ;;
esac

start_stack
