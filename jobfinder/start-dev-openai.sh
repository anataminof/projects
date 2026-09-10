#!/bin/bash
# Start the dev stack (backend + frontend) with the cloud OpenAI AI provider.
# Requires OPENAI_API_KEY in .env.local.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/dev-lib.sh
source "$ROOT/scripts/dev-lib.sh"

echo "🚀 Job Search System — Dev (AI provider: OpenAI)"
echo "==============================================="
echo ""

load_env_local
export AI_PROVIDER=openai

if [ -z "${OPENAI_API_KEY:-}" ]; then
    err "❌ OPENAI_API_KEY is not set. Add it to .env.local and retry."
    exit 1
fi

trap dev_cleanup EXIT INT TERM

start_stack
