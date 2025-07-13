from unittest.mock import Mock, patch

from media_renamer.metadata_extractor import MetadataExtractor
from media_renamer.models import MediaType
from tests.fixtures.sample_responses import (
    GUESSIT_EDGE_CASES,
    GUESSIT_MOVIE_RESULT,
    GUESSIT_TV_RESULT,
)


class TestMetadataExtractor:
    """Test cases for MetadataExtractor class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.extractor = MetadataExtractor()

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_movie_from_filename(self, mock_guessit, temp_dir):
        """Test extracting movie metadata from filename"""
        mock_guessit.return_value = GUESSIT_MOVIE_RESULT

        movie_path = temp_dir / "The.Matrix.1999.1080p.BluRay.x264.mkv"
        movie_path.touch()

        result = self.extractor.extract_from_filename(movie_path)

        assert result.media_type == MediaType.MOVIE
        assert result.title == "The Matrix"
        assert result.year == 1999
        assert result.extension == ".mkv"
        assert result.original_path == movie_path
        assert result.season is None
        assert result.episode is None

        mock_guessit.assert_called_once_with("The.Matrix.1999.1080p.BluRay.x264")

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_tv_from_filename(self, mock_guessit, temp_dir):
        """Test extracting TV show metadata from filename"""
        mock_guessit.return_value = GUESSIT_TV_RESULT

        tv_path = temp_dir / "Breaking.Bad.S01E01.720p.HDTV.x264.mkv"
        tv_path.touch()

        result = self.extractor.extract_from_filename(tv_path)

        assert result.media_type == MediaType.TV_SHOW
        assert result.title == "Breaking Bad"
        assert result.season == 1
        assert result.episode == 1
        assert result.extension == ".mkv"
        assert result.original_path == tv_path
        assert result.year is None

        mock_guessit.assert_called_once_with("Breaking.Bad.S01E01.720p.HDTV.x264")

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_unknown_type_with_season_episode(self, mock_guessit, temp_dir):
        """Test unknown type detection with season/episode present"""
        mock_guessit.return_value = {
            "title": "Unknown Show",
            "season": 1,
            "episode": 5,
            "type": "unknown",
        }

        file_path = temp_dir / "Unknown.Show.S01E05.mkv"
        file_path.touch()

        result = self.extractor.extract_from_filename(file_path)

        assert result.media_type == MediaType.TV_SHOW
        assert result.title == "Unknown Show"
        assert result.season == 1
        assert result.episode == 5

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_unknown_type_with_year(self, mock_guessit, temp_dir):
        """Test unknown type detection with year present"""
        mock_guessit.return_value = {
            "title": "Unknown Movie",
            "year": 2020,
            "type": "unknown",
        }

        file_path = temp_dir / "Unknown.Movie.2020.mkv"
        file_path.touch()

        result = self.extractor.extract_from_filename(file_path)

        assert result.media_type == MediaType.MOVIE
        assert result.title == "Unknown Movie"
        assert result.year == 2020

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_completely_unknown(self, mock_guessit, temp_dir):
        """Test completely unknown file type"""
        mock_guessit.return_value = {"title": "random_file"}

        file_path = temp_dir / "random_file.mkv"
        file_path.touch()

        result = self.extractor.extract_from_filename(file_path)

        assert result.media_type == MediaType.UNKNOWN
        assert result.title == "random_file"
        assert result.year is None
        assert result.season is None
        assert result.episode is None

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_with_episode_title(self, mock_guessit, temp_dir):
        """Test extracting episode with episode title"""
        mock_guessit.return_value = {
            "title": "Game of Thrones",
            "season": 1,
            "episode": 1,
            "episode_title": "Winter Is Coming",
            "type": "episode",
        }

        file_path = temp_dir / "Game.of.Thrones.S01E01.Winter.Is.Coming.mkv"
        file_path.touch()

        result = self.extractor.extract_from_filename(file_path)

        assert result.media_type == MediaType.TV_SHOW
        assert result.title == "Game of Thrones"
        assert result.season == 1
        assert result.episode == 1
        assert result.episode_title == "Winter Is Coming"

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_edge_cases(self, mock_guessit, temp_dir):
        """Test various edge cases"""
        test_cases = [
            # Movie with dots in title
            {
                "filename": "Movie.with.dots.in.title.2020.mkv",
                "guessit_result": GUESSIT_EDGE_CASES["movie_with_dots"],
                "expected_type": MediaType.MOVIE,
                "expected_title": "Movie with dots in title",
            },
            # TV show with episode title containing parentheses
            {
                "filename": "TV.Show.S01E01.Episode.with.parentheses.mp4",
                "guessit_result": GUESSIT_EDGE_CASES["tv_with_episode_title"],
                "expected_type": MediaType.TV_SHOW,
                "expected_title": "TV Show",
            },
            # Movie with brackets and special edition
            {
                "filename": "Movie.2021.Special.Edition.avi",
                "guessit_result": GUESSIT_EDGE_CASES["movie_with_brackets"],
                "expected_type": MediaType.MOVIE,
                "expected_title": "Movie",
            },
        ]

        for case in test_cases:
            mock_guessit.return_value = case["guessit_result"]

            file_path = temp_dir / case["filename"]
            file_path.touch()

            result = self.extractor.extract_from_filename(file_path)

            assert result.media_type == case["expected_type"]
            assert result.title == case["expected_title"]

            # Clean up for next iteration
            file_path.unlink()

    def test_guess_media_type_patterns(self):
        """Test media type guessing patterns"""
        # Test TV show patterns
        tv_patterns = [
            "Show.S01E01.mkv",
            "Show.Season.1.Episode.2.mkv",
            "Show.1x02.mkv",
            "SHOW.s01e01.mkv",  # Case insensitive
        ]

        for pattern in tv_patterns:
            result = self.extractor._guess_media_type(pattern)
            assert result == MediaType.TV_SHOW, f"Failed for pattern: {pattern}"

        # Test movie patterns (year detection)
        movie_patterns = [
            "Movie.1999.mkv",
            "Movie.2020.mkv",
            "Movie.2021.1080p.mkv",
        ]

        for pattern in movie_patterns:
            result = self.extractor._guess_media_type(pattern)
            assert result == MediaType.MOVIE, f"Failed for pattern: {pattern}"

        # Test unknown patterns
        unknown_patterns = [
            "random_file.mkv",
            "document.pdf",
            "audio.mp3",
        ]

        for pattern in unknown_patterns:
            result = self.extractor._guess_media_type(pattern)
            assert result == MediaType.UNKNOWN, f"Failed for pattern: {pattern}"

    @patch("media_renamer.metadata_extractor.PyMediaInfo")
    def test_extract_from_mediainfo_success(self, mock_mediainfo, temp_dir):
        """Test successful mediainfo extraction"""
        # Mock MediaInfo track
        mock_track = Mock()
        mock_track.track_type = "General"
        mock_track.title = "Test Movie"
        mock_track.recorded_date = "2020-01-01"
        mock_track.season = "1"
        mock_track.episode = "5"

        # Mock MediaInfo.parse
        mock_info = Mock()
        mock_info.tracks = [mock_track]
        mock_mediainfo.parse.return_value = mock_info

        file_path = temp_dir / "test.mkv"
        file_path.touch()

        result = self.extractor.extract_from_mediainfo(file_path)

        assert result is not None
        assert result["title"] == "Test Movie"
        assert result["year"] == 2020
        assert result["season"] == 1
        assert result["episode"] == 5

        mock_mediainfo.parse.assert_called_once_with(str(file_path))

    @patch("media_renamer.metadata_extractor.PyMediaInfo")
    def test_extract_from_mediainfo_partial_data(self, mock_mediainfo, temp_dir):
        """Test mediainfo extraction with partial data"""
        # Mock MediaInfo track with only title
        mock_track = Mock()
        mock_track.track_type = "General"
        mock_track.title = "Test Movie"
        # These attributes don't exist
        del mock_track.recorded_date
        del mock_track.season
        del mock_track.episode

        mock_info = Mock()
        mock_info.tracks = [mock_track]
        mock_mediainfo.parse.return_value = mock_info

        file_path = temp_dir / "test.mkv"
        file_path.touch()

        result = self.extractor.extract_from_mediainfo(file_path)

        assert result is not None
        assert result["title"] == "Test Movie"
        assert "year" not in result
        assert "season" not in result
        assert "episode" not in result

    @patch("media_renamer.metadata_extractor.PyMediaInfo")
    def test_extract_from_mediainfo_no_general_track(self, mock_mediainfo, temp_dir):
        """Test mediainfo extraction with no general track"""
        # Mock MediaInfo track that's not 'General'
        mock_track = Mock()
        mock_track.track_type = "Video"

        mock_info = Mock()
        mock_info.tracks = [mock_track]
        mock_mediainfo.parse.return_value = mock_info

        file_path = temp_dir / "test.mkv"
        file_path.touch()

        result = self.extractor.extract_from_mediainfo(file_path)

        assert result == {}

    @patch("media_renamer.metadata_extractor.PyMediaInfo")
    def test_extract_from_mediainfo_exception(self, mock_mediainfo, temp_dir):
        """Test mediainfo extraction with exception"""
        mock_mediainfo.parse.side_effect = Exception("MediaInfo error")

        file_path = temp_dir / "test.mkv"
        file_path.touch()

        result = self.extractor.extract_from_mediainfo(file_path)

        assert result is None

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_fallback_to_filename(self, mock_guessit, temp_dir):
        """Test fallback to filename when guessit fails"""
        mock_guessit.return_value = {}

        file_path = temp_dir / "Some.Movie.2020.mkv"
        file_path.touch()

        result = self.extractor.extract_from_filename(file_path)

        assert result.title == "Some.Movie.2020"  # Falls back to filename
        assert (
            result.media_type == MediaType.MOVIE
        )  # Correctly identified by year pattern
        assert result.extension == ".mkv"

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_different_extensions(self, mock_guessit, temp_dir):
        """Test extraction with different file extensions"""
        mock_guessit.return_value = GUESSIT_MOVIE_RESULT

        extensions = [".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"]

        for ext in extensions:
            file_path = temp_dir / f"Movie.2020{ext}"
            file_path.touch()

            result = self.extractor.extract_from_filename(file_path)

            assert result.extension == ext
            assert result.title == "The Matrix"

            file_path.unlink()

    @patch("media_renamer.metadata_extractor.guessit.guessit")
    def test_extract_with_complex_filenames(self, mock_guessit, temp_dir):
        """Test extraction with complex filenames"""
        complex_cases = [
            {
                "filename": "The.Lord.of.the.Rings.The.Fellowship.of.the.Ring.2001.Extended.Edition.1080p.BluRay.x264.mkv",
                "guessit_result": {
                    "title": "The Lord of the Rings The Fellowship of the Ring",
                    "year": 2001,
                    "type": "movie",
                    "edition": "Extended Edition",
                },
            },
            {
                "filename": "Game.of.Thrones.S08E06.The.Iron.Throne.1080p.WEB-DL.DD5.1.H.264.mkv",
                "guessit_result": {
                    "title": "Game of Thrones",
                    "season": 8,
                    "episode": 6,
                    "episode_title": "The Iron Throne",
                    "type": "episode",
                },
            },
        ]

        for case in complex_cases:
            mock_guessit.return_value = case["guessit_result"]

            file_path = temp_dir / case["filename"]
            file_path.touch()

            result = self.extractor.extract_from_filename(file_path)

            assert result.title == case["guessit_result"]["title"]
            if "year" in case["guessit_result"]:
                assert result.year == case["guessit_result"]["year"]
            if "season" in case["guessit_result"]:
                assert result.season == case["guessit_result"]["season"]
            if "episode" in case["guessit_result"]:
                assert result.episode == case["guessit_result"]["episode"]

            file_path.unlink()

    def test_season_episode_patterns(self):
        """Test all season/episode patterns"""
        patterns = [
            ("Show.S01E01.mkv", 1, 1),
            ("Show.s05e12.mkv", 5, 12),
            ("Show.Season.2.Episode.3.mkv", 2, 3),
            ("Show.2x5.mkv", 2, 5),
            ("Show.10x01.mkv", 10, 1),
        ]

        for filename, expected_season, expected_episode in patterns:
            matches = []
            for pattern in self.extractor.season_episode_patterns:
                import re

                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    matches.append((int(match.group(1)), int(match.group(2))))

            assert len(matches) > 0, f"No pattern matched for {filename}"
            assert (
                expected_season,
                expected_episode,
            ) in matches, f"Expected ({expected_season}, {expected_episode}) not found in {matches}"
