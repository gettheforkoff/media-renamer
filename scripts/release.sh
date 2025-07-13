#!/bin/bash

# Media Renamer Release Script
# This script helps with local testing of the release process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command_exists "uv"; then
        missing_deps+=("uv")
    fi
    
    if ! command_exists "docker"; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists "git"; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install missing dependencies and try again."
        exit 1
    fi
    
    print_success "All dependencies found"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment..."
        uv venv
    fi
    
    # Install dependencies
    print_status "Installing dependencies..."
    uv pip install -e .
    uv pip install pytest pytest-cov black ruff mypy
    
    # Run tests
    print_status "Running test suite..."
    uv run pytest
    
    print_status "Running code formatting check..."
    uv run black --check media_renamer/
    
    print_status "Running linting..."
    uv run ruff check media_renamer/
    
    print_status "Running type checking..."
    uv run mypy media_renamer/
    
    print_success "All tests and checks passed!"
}

# Build Docker image
build_docker() {
    print_status "Building Docker image..."
    docker build -t media-renamer:test --target runtime .
    print_success "Docker image built successfully!"
}

# Test Docker image
test_docker() {
    print_status "Testing Docker image..."
    
    # Create test directory
    mkdir -p /tmp/media-renamer-test
    echo "Testing Docker functionality..." > /tmp/media-renamer-test/test.txt
    
    # Test help command
    docker run --rm media-renamer:test /usr/local/bin/media-renamer --help
    
    # Test dry run
    docker run --rm -v /tmp/media-renamer-test:/media media-renamer:test
    
    # Cleanup
    rm -rf /tmp/media-renamer-test
    
    print_success "Docker image test completed!"
}

# Build binary
build_binary() {
    print_status "Building binary..."
    uv run python build_binary.py
    
    if [ -f "dist/media-renamer" ]; then
        print_success "Binary built successfully at dist/media-renamer"
        
        # Test binary
        print_status "Testing binary..."
        ./dist/media-renamer --help
        print_success "Binary test completed!"
    elif [ -f "dist/media-renamer.exe" ]; then
        print_success "Binary built successfully at dist/media-renamer.exe"
        
        # Test binary on Windows
        print_status "Testing binary..."
        ./dist/media-renamer.exe --help
        print_success "Binary test completed!"
    else
        print_error "Binary build failed!"
        exit 1
    fi
}

# Create release tag
create_tag() {
    local version=$1
    
    if [ -z "$version" ]; then
        print_error "Version not provided!"
        echo "Usage: $0 tag <version>"
        echo "Example: $0 tag v1.2.3"
        exit 1
    fi
    
    # Validate version format
    if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
        print_error "Invalid version format. Use semantic versioning (e.g., v1.2.3)"
        exit 1
    fi
    
    # Check if tag already exists
    if git tag -l | grep -q "^$version$"; then
        print_error "Tag $version already exists!"
        exit 1
    fi
    
    print_status "Creating tag $version..."
    
    # Update version in pyproject.toml
    local clean_version=${version#v}
    sed -i.bak "s/version = \".*\"/version = \"$clean_version\"/" pyproject.toml
    rm pyproject.toml.bak
    
    # Commit version change
    git add pyproject.toml
    git commit -m "chore: bump version to $version"
    
    # Create and push tag
    git tag "$version"
    git push origin main
    git push origin "$version"
    
    print_success "Tag $version created and pushed!"
    print_status "GitHub Actions will now build and create the release automatically."
}

# Main script logic
main() {
    local command=$1
    
    case $command in
        "deps"|"dependencies")
            check_dependencies
            ;;
        "test")
            check_dependencies
            run_tests
            ;;
        "docker")
            check_dependencies
            build_docker
            test_docker
            ;;
        "binary")
            check_dependencies
            build_binary
            ;;
        "all")
            check_dependencies
            run_tests
            build_docker
            test_docker
            build_binary
            ;;
        "tag")
            check_dependencies
            create_tag "$2"
            ;;
        *)
            echo "Media Renamer Release Script"
            echo ""
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  deps         Check dependencies"
            echo "  test         Run tests and code quality checks"
            echo "  docker       Build and test Docker image"
            echo "  binary       Build and test binary"
            echo "  all          Run all tests and builds"
            echo "  tag <version> Create and push release tag"
            echo ""
            echo "Examples:"
            echo "  $0 test"
            echo "  $0 all"
            echo "  $0 tag v1.2.3"
            ;;
    esac
}

# Run main function with all arguments
main "$@"