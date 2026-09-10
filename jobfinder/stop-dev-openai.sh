#!/bin/bash
# Stop the dev stack started with the OpenAI provider.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/dev-lib.sh
source "$ROOT/scripts/dev-lib.sh"

echo "🛑 Stopping Job Search System (OpenAI)..."
echo ""

load_env_local
stop_stack

echo ""
ok "✅ All services stopped"
