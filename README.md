# Media Renamer

A Python tool that automatically renames movie and TV show files to a standardized format using metadata from TVDB and TMDB APIs.

## Features

- **Automatic metadata extraction** from filenames and file properties
- **TVDB and TMDB integration** for accurate show/movie information
- **Configurable naming patterns** for movies and TV shows
- **Dry run mode** to preview changes before applying them
- **Docker support** for easy deployment
- **Rich CLI interface** with progress indicators and formatted output
- **Support for multiple file formats** (mkv, mp4, avi, mov, wmv, flv, webm)

## Installation

### Local Installation

```bash
pip install -r requirements.txt
```

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

### Command Line

```bash
# Basic usage
python -m src.cli /path/to/media/files

# Dry run (preview changes)
python -m src.cli /path/to/media/files --dry-run

# Verbose output
python -m src.cli /path/to/media/files --verbose

# Custom patterns
python -m src.cli /path/to/media/files --movie-pattern "{title} [{year}]" --tv-pattern "{title} S{season:02d}E{episode:02d}"
```

### Docker

```bash
# Using docker-compose
docker-compose up

# Using docker directly
docker run -v /path/to/media:/media -e TMDB_API_KEY=your_key media-renamer
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
src/
├── __init__.py
├── api_clients.py      # TVDB and TMDB API clients
├── cli.py             # Command-line interface
├── config.py          # Configuration management
├── main.py            # Entry point
├── metadata_extractor.py  # File metadata extraction
├── models.py          # Data models
└── renamer.py         # File renaming logic
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Building Docker Image

```bash
docker build -t media-renamer .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **API Rate Limits**: The tool includes built-in rate limiting, but you may need to wait between large batches
2. **Missing Dependencies**: Ensure all requirements are installed, especially `pymediainfo`
3. **File Permissions**: Make sure the tool has read/write access to the media directory

### Debug Mode

Run with `--verbose` flag to see detailed processing information:

```bash
python -m src.cli /path/to/media --verbose --dry-run
```