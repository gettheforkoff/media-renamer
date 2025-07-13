import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from media_renamer.config import Config
from media_renamer.models import MediaInfo, MediaType


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing"""
    return Config(
        tmdb_api_key="test_tmdb_key",
        tvdb_api_key="test_tvdb_key",
        movie_pattern="{title} ({year})",
        tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
        dry_run=False,
        verbose=False,
        supported_extensions=[".mkv", ".mp4", ".avi"],
    )


@pytest.fixture
def sample_movie_info(temp_dir):
    """Create sample movie MediaInfo"""
    movie_path = temp_dir / "The Matrix 1999.mkv"
    movie_path.touch()

    return MediaInfo(
        original_path=movie_path,
        media_type=MediaType.MOVIE,
        title="The Matrix",
        year=1999,
        extension=".mkv",
        tmdb_id=603,
        imdb_id="tt0133093",
    )


@pytest.fixture
def sample_tv_info(temp_dir):
    """Create sample TV show MediaInfo"""
    tv_path = temp_dir / "Breaking Bad S01E01.mkv"
    tv_path.touch()

    return MediaInfo(
        original_path=tv_path,
        media_type=MediaType.TV_SHOW,
        title="Breaking Bad",
        year=2008,
        season=1,
        episode=1,
        episode_title="Pilot",
        extension=".mkv",
        tvdb_id=81189,
        tmdb_id=1396,
    )


@pytest.fixture
def sample_unknown_info(temp_dir):
    """Create sample unknown MediaInfo"""
    unknown_path = temp_dir / "unknown_file.mkv"
    unknown_path.touch()

    return MediaInfo(
        original_path=unknown_path,
        media_type=MediaType.UNKNOWN,
        title="unknown_file",
        extension=".mkv",
    )


@pytest.fixture
def mock_tmdb_client():
    """Create a mock TMDB client"""
    client = Mock()
    client.search_movie.return_value = {
        "title": "The Matrix",
        "year": 1999,
        "tmdb_id": 603,
        "imdb_id": "tt0133093",
    }
    client.search_tv_show.return_value = {
        "title": "Breaking Bad",
        "year": 2008,
        "tmdb_id": 1396,
        "season": 1,
        "episode": 1,
        "episode_title": "Pilot",
    }
    return client


@pytest.fixture
def mock_tvdb_client():
    """Create a mock TVDB client"""
    client = Mock()
    client.search_movie.return_value = {
        "title": "The Matrix",
        "year": 1999,
        "tvdb_id": 12345,
    }
    client.search_tv_show.return_value = {
        "title": "Breaking Bad",
        "year": 2008,
        "tvdb_id": 81189,
        "season": 1,
        "episode": 1,
        "episode_title": "Pilot",
    }
    return client


@pytest.fixture
def sample_media_files(temp_dir):
    """Create sample media files for testing"""
    files = [
        # Movies
        "The.Matrix.1999.1080p.BluRay.x264.mkv",
        "Inception (2010) [1080p].mp4",
        "The Godfather 1972 720p.avi",
        "Pulp Fiction [1994].mkv",
        "The_Dark_Knight_2008.mp4",
        # TV Shows
        "Breaking.Bad.S01E01.720p.HDTV.x264.mkv",
        "Game of Thrones - S01E01 - Winter Is Coming.mp4",
        "The Office US S02E01 The Dundies.avi",
        "Friends.1x01.The.One.Where.Monica.Gets.a.Roommate.mkv",
        "Stranger Things S01E01 1080p.mp4",
        # Edge cases
        "Movie.with.dots.in.title.2020.mkv",
        "TV Show - S01E01 - Episode with (parentheses).mp4",
        "Movie [2021] {Special Edition}.avi",
        "Show_with_underscores_S01E01.mkv",
        "Movie with spaces 2019.mp4",
        # Problematic files
        "Movie<>:|?*.mkv",  # Invalid characters
        "Very.Long.Movie.Title.With.Many.Words.And.Dots.2020.1080p.BluRay.x264.AAC.mkv",
        "Movie.2020.2021.mkv",  # Multiple years
        "Show.S01E01E02.mkv",  # Double episode
        # Unknown format
        "random_file.mkv",
        "Document.pdf",  # Wrong extension
        "audio_file.mp3",  # Audio file
    ]

    created_files = []
    for filename in files:
        file_path = temp_dir / filename
        file_path.touch()
        created_files.append(file_path)

    return created_files


@pytest.fixture
def mock_requests_session():
    """Create a mock requests session"""
    session = Mock()

    # Mock successful movie response
    movie_response = Mock()
    movie_response.json.return_value = {
        "results": [
            {
                "title": "The Matrix",
                "release_date": "1999-03-31",
                "id": 603,
                "imdb_id": "tt0133093",
            }
        ]
    }
    movie_response.raise_for_status.return_value = None

    # Mock successful TV response
    tv_response = Mock()
    tv_response.json.return_value = {
        "results": [
            {"name": "Breaking Bad", "first_air_date": "2008-01-20", "id": 1396}
        ]
    }
    tv_response.raise_for_status.return_value = None

    # Mock episode response
    episode_response = Mock()
    episode_response.json.return_value = {
        "name": "Pilot",
        "air_date": "2008-01-20",
        "episode_number": 1,
        "season_number": 1,
    }
    episode_response.raise_for_status.return_value = None

    # Configure session to return appropriate responses
    def mock_get(url, **kwargs):
        if "/search/movie" in url:
            return movie_response
        elif "/search/tv" in url:
            return tv_response
        elif "/tv/" in url and "/episode/" in url:
            return episode_response
        else:
            return Mock()

    session.get.side_effect = mock_get
    return session
