# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline with multi-platform support
- Docker image builds and publishing to GitHub Container Registry (GHCR)
- Automated binary builds for Linux, macOS, and Windows
- Multi-stage Docker builds for optimized image size
- File permission preservation during renaming operations
- Comprehensive test coverage including permission preservation tests

### Changed
- Improved Docker image efficiency with multi-stage builds (43% size reduction)
- Enhanced documentation with explicit file permission preservation details

### Fixed
- File permissions, ownership, and timestamps are now properly preserved during renaming

## [1.0.0] - Initial Release

### Added
- Automatic metadata extraction from filenames using guessit
- TVDB and TMDB API integration for accurate metadata
- Configurable naming patterns for movies and TV shows
- Dry run mode for previewing changes
- Docker support with docker-compose
- Rich CLI interface with progress indicators
- Support for multiple video formats (mkv, mp4, avi, mov, wmv, flv, webm)
- Comprehensive unit and integration test suite
- Binary generation using PyInstaller
- Environment-based configuration with .env support