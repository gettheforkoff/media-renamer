# Media Renamer

A Python tool that automatically renames movie and TV show files to a standardized format using metadata from TVDB and TMDB APIs.

## Features

- **Automatic metadata extraction** from filenames and file properties
- **TVDB and TMDB integration** for accurate show/movie information
- **Configurable naming patterns** for movies and TV shows
- **Dry run mode** to preview changes before applying them
- **Docker support** for easy deployment
- **Binary CLI generation** for standalone executables
- **Rich CLI interface** with progress indicators and formatted output
- **Support for multiple file formats** (mkv, mp4, avi, mov, wmv, flv, webm)
- **File permission preservation** - maintains original file permissions, ownership, and timestamps

## Installation

### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone <repository-url>
cd media-renamer
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

### Binary Installation

#### Download Pre-built Binaries

Download the latest pre-built binaries from the [releases page](https://github.com/gettheforkoff/media-renamer/releases):

```bash
# Linux (x64)
wget https://github.com/gettheforkoff/media-renamer/releases/latest/download/media-renamer-linux-amd64
chmod +x media-renamer-linux-amd64
./media-renamer-linux-amd64 --help

# macOS (Universal)
wget https://github.com/gettheforkoff/media-renamer/releases/latest/download/media-renamer-macos-universal
chmod +x media-renamer-macos-universal
./media-renamer-macos-universal --help

# Windows (x64)
# Download from: https://github.com/gettheforkoff/media-renamer/releases/latest/download/media-renamer-windows-amd64.exe
```

#### Build from Source

Build a standalone binary that doesn't require Python:

```bash
# Using the build script
./scripts/build.sh

# Manual build
python build_binary.py
```

The binary will be created in the `dist/` directory.

### Docker Installation

```bash
docker-compose up --build
```

## Configuration

Create a `.env` file based on `.env.example`:

```env
TMDB_API_KEY=your_tmdb_api_key_here
TVDB_API_KEY=your_tvdb_api_key_here
DRY_RUN=true
VERBOSE=false
MEDIA_PATH=/path/to/your/media/files
```

### API Keys

- **TMDB API Key**: Get from [The Movie Database](https://www.themoviedb.org/settings/api)
- **TVDB API Key**: Get from [The TV Database](https://thetvdb.com/api-information)

## Usage

### Command Line (uv)

```bash
# Basic usage
uv run python -m media_renamer.cli /path/to/media/files

# Or with installed CLI
media-renamer /path/to/media/files

# Dry run (preview changes)
media-renamer /path/to/media/files --dry-run

# Verbose output
media-renamer /path/to/media/files --verbose

# Custom patterns
media-renamer /path/to/media/files --movie-pattern "{title} [{year}]" --tv-pattern "{title} S{season:02d}E{episode:02d}"
```

### Binary

```bash
# After building the binary
./dist/media-renamer /path/to/media/files --dry-run --verbose
```

### Docker

```bash
# Using docker-compose
docker-compose up

# Using GitHub Container Registry image (recommended)
docker run -v /path/to/media:/media -e TMDB_API_KEY=your_key -e TVDB_API_KEY=your_key ghcr.io/gettheforkoff/media-renamer:latest

# Using specific version
docker run -v /path/to/media:/media -e TMDB_API_KEY=your_key -e TVDB_API_KEY=your_key ghcr.io/gettheforkoff/media-renamer:v1.1.0

# Using docker directly (local build)
docker run -v /path/to/media:/media -e TMDB_API_KEY=your_key media-renamer
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
uv pip install -r requirements-dev.txt

# Or install dev dependencies defined in pyproject.toml
uv pip install -e .[dev]
```

### Code Quality

```bash
# Format code
uv run black media_renamer/
uv run ruff check media_renamer/

# Type checking
uv run mypy media_renamer/

# Run tests
uv run pytest
```

### Building

```bash
# Build wheel
uv build

# Build binary
./scripts/build.sh
```

## Naming Patterns

### Default Patterns

- **Movies**: `{title} ({year})`
- **TV Shows**: `{title} - S{season:02d}E{episode:02d} - {episode_title}`

### Available Variables

#### Movies
- `{title}` - Movie title
- `{year}` - Release year

#### TV Shows
- `{title}` - Show title
- `{season}` - Season number
- `{episode}` - Episode number
- `{episode_title}` - Episode title
- `{year}` - Show's first air year

## Examples

### Before
```
/media/movies/The.Matrix.1999.1080p.BluRay.x264.mkv
/media/tv/Breaking.Bad.S01E01.720p.HDTV.x264.mkv
```

### After
```
/media/movies/The Matrix (1999).mkv
/media/tv/Breaking Bad - S01E01 - Pilot.mkv
```

## Project Structure

```
media_renamer/
├── __init__.py
├── api_clients.py      # TVDB and TMDB API clients
├── cli.py             # Command-line interface
├── config.py          # Configuration management
├── main.py            # Entry point
├── metadata_extractor.py  # File metadata extraction
├── models.py          # Data models
└── renamer.py         # File renaming logic

scripts/
└── build.sh           # Build script for binary

build_binary.py        # PyInstaller binary builder
pyproject.toml         # Project configuration
docker-compose.yml     # Docker compose configuration
Dockerfile             # Docker image definition
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run quality checks (`uv run black`, `uv run ruff`, `uv run mypy`)
6. Submit a pull request

### Release Process

Releases are fully automated through GitHub Actions. The process is triggered by creating and pushing a version tag:

#### Creating a Release

1. **For Maintainers**: Create and push a version tag
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. **Alternative**: Use the "Manual Release" workflow dispatch in GitHub Actions UI

#### What Happens During Release

The release workflow automatically:

1. **✅ Quality Checks**: Runs full test suite across Python 3.8-3.13
2. **🐳 Docker Images**: Builds and pushes multi-platform images to GHCR
   - `ghcr.io/gettheforkoff/media-renamer:latest`
   - `ghcr.io/gettheforkoff/media-renamer:v1.2.3`
   - `ghcr.io/gettheforkoff/media-renamer:v1.2`
   - `ghcr.io/gettheforkoff/media-renamer:v1`

3. **📦 Binary Builds**: Creates standalone executables for:
   - Linux (x64)
   - macOS (Universal)
   - Windows (x64)

4. **📋 Changelog**: Automatically updates `CHANGELOG.md` with:
   - Categorized commits (Added/Changed/Fixed)
   - Proper version section with date
   - Commit links and references

5. **🚀 GitHub Release**: Creates release with:
   - Downloadable binary assets
   - Docker installation instructions
   - Auto-generated changelog
   - Semantic version tagging

#### Release Requirements

- All CI checks must pass
- Version tags must follow semantic versioning (`v1.2.3`)
- Only maintainers can create releases
- Releases are immutable once created

#### Docker Images

After each release, Docker images are available at:
```bash
# Latest release
docker pull ghcr.io/gettheforkoff/media-renamer:latest

# Specific version
docker pull ghcr.io/gettheforkoff/media-renamer:v1.1.0
```

#### Binary Downloads

Pre-built binaries are available on the [releases page](https://github.com/gettheforkoff/media-renamer/releases) for immediate download without requiring Python installation.

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **API Rate Limits**: The tool includes built-in rate limiting, but you may need to wait between large batches
2. **Missing Dependencies**: Ensure all requirements are installed, especially `pymediainfo`
3. **File Permissions**: Make sure the tool has read/write access to the media directory
4. **uv Not Found**: Install uv using `curl -LsSf https://astral.sh/uv/install.sh | sh`

### File Permission Preservation

The media renamer automatically preserves the following file attributes during renaming:
- **File permissions** (read/write/execute for owner/group/others)
- **File ownership** (user ID and group ID)
- **Timestamps** (creation, modification, and access times)

This ensures that renamed files maintain their original security settings and metadata, which is particularly important in shared environments or when files have specific permission requirements.

### Debug Mode

Run with `--verbose` flag to see detailed processing information:

```bash
media-renamer /path/to/media --verbose --dry-run
```

### Binary Issues

If the binary doesn't work:
1. Ensure all system dependencies are installed (libmediainfo)
2. Try running from source first to verify functionality
3. Check the build logs for missing dependencies