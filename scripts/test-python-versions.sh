#!/bin/bash

# Script to test media-renamer against multiple Python versions locally
# Requires uv to be installed

set -e

PYTHON_VERSIONS=("3.9" "3.10" "3.11" "3.12" "3.13")
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED_VERSIONS=()

echo "🧪 Testing media-renamer against multiple Python versions"
echo "Project root: $PROJECT_ROOT"
echo

cd "$PROJECT_ROOT"

# Function to test a specific Python version
test_python_version() {
    local version=$1
    echo "🐍 Testing Python $version..."
    
    # Create a clean virtual environment for this version
    local venv_name=".venv-py${version}"
    rm -rf "$venv_name"
    
    if ! uv venv "$venv_name" --python "$version"; then
        echo "❌ Failed to create venv for Python $version (version not available)"
        return 1
    fi
    
    # Activate the environment and install dependencies
    source "$venv_name/bin/activate"
    
    if ! uv pip install -e .; then
        echo "❌ Failed to install dependencies for Python $version"
        deactivate
        return 1
    fi
    
    if ! uv pip install pytest pytest-cov black ruff mypy; then
        echo "❌ Failed to install dev dependencies for Python $version"
        deactivate
        return 1
    fi
    
    # Run tests
    echo "  📋 Running tests..."
    if ! uv run pytest --tb=short; then
        echo "❌ Tests failed for Python $version"
        deactivate
        return 1
    fi
    
    # Run linting (only for the latest version to avoid noise)
    if [ "$version" = "3.13" ]; then
        echo "  🔍 Running linting..."
        if ! uv run black --check media_renamer/; then
            echo "❌ Black formatting check failed"
            deactivate
            return 1
        fi
        
        if ! uv run ruff check media_renamer/; then
            echo "❌ Ruff linting failed"
            deactivate
            return 1
        fi
        
        echo "  🔎 Running type checking..."
        if ! uv run mypy media_renamer/; then
            echo "❌ MyPy type checking failed"
            deactivate
            return 1
        fi
    fi
    
    deactivate
    echo "✅ Python $version: PASSED"
    echo
    return 0
}

# Install required Python versions
echo "📦 Installing Python versions..."
for version in "${PYTHON_VERSIONS[@]}"; do
    echo "Installing Python $version..."
    uv python install "$version" || echo "Warning: Could not install Python $version"
done
echo

# Test each version
for version in "${PYTHON_VERSIONS[@]}"; do
    if ! test_python_version "$version"; then
        FAILED_VERSIONS+=("$version")
    fi
done

# Cleanup
echo "🧹 Cleaning up temporary environments..."
for version in "${PYTHON_VERSIONS[@]}"; do
    rm -rf ".venv-py${version}"
done

# Summary
echo "📊 Test Summary:"
echo "================"
if [ ${#FAILED_VERSIONS[@]} -eq 0 ]; then
    echo "🎉 All Python versions passed!"
    exit 0
else
    echo "❌ Failed versions: ${FAILED_VERSIONS[*]}"
    echo "✅ Passed versions: $(printf '%s\n' "${PYTHON_VERSIONS[@]}" | grep -v -F -f <(printf '%s\n' "${FAILED_VERSIONS[@]}") | tr '\n' ' ')"
    exit 1
fi