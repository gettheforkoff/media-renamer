#!/bin/bash
set -e

echo "Media Renamer Build Script"
echo "=========================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment and install dependencies
echo "Setting up virtual environment..."
uv venv
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -e .

# Install PyInstaller for binary building
echo "Installing PyInstaller..."
uv pip install pyinstaller

# Build the binary
echo "Building binary..."
python build_binary.py

echo "Build completed!"
echo "Binary location: dist/media-renamer"