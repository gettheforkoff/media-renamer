# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses `uv` for package management. Always use `uv run` prefix for commands:

```bash
# Install dependencies and setup
uv venv
uv pip install -e .

# Testing
uv run pytest                           # Run all tests
uv run pytest tests/unit/              # Run unit tests only
uv run pytest tests/integration/       # Run integration tests only
uv run pytest path/to/test_file.py::TestClass::test_method  # Run specific test
uv run pytest --cov=media_renamer --cov-report=html --cov-report=term-missing  # With coverage

# Code Quality
uv run black media_renamer/            # Format code
uv run ruff check media_renamer/       # Lint code
uv run mypy media_renamer/             # Type checking

# Build
uv build                               # Build wheel package
python build_binary.py                 # Build PyInstaller binary

# Docker
docker build -t media-renamer:multi-stage --target runtime .  # Multi-stage build
docker-compose up --build             # Full stack with docker-compose

# Release Management
./scripts/release.sh test              # Run all tests and quality checks
./scripts/release.sh all               # Run tests + build Docker + build binary
./scripts/release.sh tag v1.2.3        # Create and push release tag
```

## Architecture Overview

### Core Data Flow
1. **CLI Entry** (`cli.py`) → **File Renamer** (`renamer.py`) → **Metadata Extractor** (`metadata_extractor.py`) → **API Clients** (`api_clients.py`)
2. Files are processed through: filename parsing → API enhancement → renaming with preserved permissions

### Key Components

**Models (`models.py`)**
- `MediaInfo`: Central data structure containing file metadata (title, year, season/episode, IDs)
- `MediaType`: Enum for MOVIE, TV_SHOW, UNKNOWN
- `RenameResult`: Contains original path, new path, success status, error info
- Pydantic validation with field validators for ID string conversion

**Metadata Extraction (`metadata_extractor.py`)**
- Primary: `guessit` library for filename parsing
- Fallback: `pymediainfo` for embedded metadata
- Pattern-based detection for season/episode formats
- Media type inference based on year presence vs season/episode

**API Integration (`api_clients.py`)**
- `APIClientManager`: Orchestrates TVDB and TMDB clients
- `TVDBClient`: TV show metadata and episode titles
- `TMDBClient`: Movie metadata and TV show details
- Rate limiting and error handling built-in
- Returns enhanced `MediaInfo` objects

**File Operations (`renamer.py`)**
- Uses `shutil.move()` to preserve file permissions, ownership, and timestamps
- Configurable naming patterns via `Config` class
- Filename sanitization for cross-platform compatibility
- Recursive directory processing with extension filtering

**Configuration (`config.py`)**
- Pydantic-based configuration with environment variable loading
- Default patterns: Movies `"{title} ({year})"`, TV Shows `"{title} - S{season:02d}E{episode:02d} - {episode_title}"`
- API keys loaded from environment or `.env` file

### Testing Architecture
- **Unit tests**: Mock external dependencies (API calls, file operations)
- **Integration tests**: Mock `APIClientManager.enhance_media_info()` method specifically
- **Fixtures**: `conftest.py` provides reusable test data and mocked API responses
- **Permission tests**: Verify file attributes are preserved during renaming

### Build Systems
- **Docker**: Multi-stage build (python:3.11-slim → debian:12-slim) for optimized images
- **PyInstaller**: Standalone binary with hidden imports for all dependencies
- **uv**: Modern Python package management with lock files

## GitHub Actions & CI/CD

### Workflows
- **CI (`ci.yml`)**: Runs on push/PR - tests, linting, Docker builds, binary artifacts
- **Release (`release.yml`)**: Triggered by version tags - full release with Docker images, binaries, and changelog updates
- **Manual Release (`manual-release.yml`)**: Workflow dispatch for manual releases with version input
- **Security (`security.yml`)**: Dependency scanning with Safety, Bandit, and Trivy

### Docker Registry
- Images pushed to GitHub Container Registry (GHCR): `ghcr.io/owner/repo:tag`
- Multi-platform builds: `linux/amd64`, `linux/arm64`
- Tags: `latest`, `main-<sha>`, version tags (`v1.2.3`, `v1.2`, `v1`)

### Release Process

**Automated Release Process** (Recommended):
1. **Tag Creation**: `git tag v1.2.3 && git push origin v1.2.3`
2. **Automatic Workflow**: Tag push triggers release workflow which:
   - Runs full test suite across Python 3.8-3.13
   - Builds and pushes multi-platform Docker images to GHCR
   - Builds binaries for Linux, macOS, and Windows
   - Updates CHANGELOG.md with categorized commits
   - Creates GitHub release with assets and changelog

**Manual Release Process**:
1. Use "Manual Release" workflow dispatch in GitHub Actions
2. Input version number (e.g., v1.2.3)
3. Same automated process as above

**Release Workflow Details**:
- **Triggers**: Push tags matching `v*` pattern
- **Dependencies**: All tests must pass before release creation
- **Artifacts**: Creates downloadable binaries and Docker images
- **Changelog**: Automatically categorizes commits into Added/Changed/Fixed sections
- **GitHub Release**: Creates release with proper versioning and assets

**Important Notes**:
- Version tags must follow semantic versioning (v1.2.3)
- All CI checks must pass before release is created
- Docker images are published to ghcr.io/gettheforkoff/media-renamer
- Changelog is automatically updated and committed to main branch

### Binary Artifacts
- Cross-platform builds using PyInstaller
- Artifacts uploaded to releases and available for 30 days in CI runs
- System dependencies handled per platform in workflows

## Important Implementation Notes

- **API Client Testing**: Always mock `APIClientManager` rather than individual clients in integration tests
- **File Permissions**: `shutil.move()` automatically preserves permissions, ownership, and timestamps
- **Error Handling**: All operations return result objects with success/error states rather than raising exceptions
- **Configuration**: Environment variables take precedence over `.env` file values
- **Docker**: Use absolute paths in CMD instruction (`/usr/local/bin/media-renamer`) for proper execution
- **CI/CD**: Use `[skip changelog]` in commit messages to prevent changelog automation
- **Dependencies**: Dependabot configured for Python, Docker, and GitHub Actions updates