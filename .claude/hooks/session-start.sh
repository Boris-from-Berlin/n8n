#!/bin/bash
set -euo pipefail

# Only run in Claude Code on the web
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "🔧 n8n SessionStart Hook - Installing dependencies and building project..."
echo ""

echo "📦 Installing dependencies with pnpm..."
if pnpm install; then
  echo "✅ Dependencies installed successfully"
else
  echo "❌ Failed to install dependencies"
  exit 1
fi

echo ""
echo "🏗️  Building project (this may take a few minutes)..."
if pnpm build > build.log 2>&1; then
  echo "✅ Build completed successfully"
else
  echo "❌ Build failed - check build.log for details"
  tail -20 build.log
  exit 1
fi

echo ""
echo "✅ SessionStart hook completed successfully!"
echo "Your n8n development environment is ready."
