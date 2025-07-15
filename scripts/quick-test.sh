#!/bin/bash

# Quick test script for current Python environment
# Usage: ./scripts/quick-test.sh [python-version]

set -e

VERSION=${1:-"3.13"}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧪 Quick test with Python $VERSION"
echo "Project root: $PROJECT_ROOT"
echo

cd "$PROJECT_ROOT"

# Create/recreate virtual environment
echo "📦 Setting up environment..."
rm -rf .venv
uv venv --python "$VERSION"
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -e .
uv pip install pytest pytest-cov black ruff mypy

# Run tests
echo "🧪 Running tests..."
uv run pytest --tb=short

# Run quality checks
echo "🔍 Running code quality checks..."
uv run black --check media_renamer/
uv run ruff check media_renamer/
uv run mypy media_renamer/

echo "✅ All checks passed!"