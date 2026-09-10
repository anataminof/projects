#!/bin/bash
# Start the dev stack (backend + frontend) with the offline Fake AI provider.
# No AI server, no network — deterministic canned responses. Best for UI work.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/dev-lib.sh
source "$ROOT/scripts/dev-lib.sh"

echo "🚀 Job Search System — Dev (AI provider: Fake / offline)"
echo "======================================================="
echo ""

load_env_local
export AI_PROVIDER=fake

trap dev_cleanup EXIT INT TERM

start_stack
