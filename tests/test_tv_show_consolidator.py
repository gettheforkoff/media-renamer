from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from media_renamer.config import Config
from media_renamer.models import MediaInfo, MediaType
from media_renamer.tv_show_consolidator import (
    TVShowConsolidator,
    TVShowDirectory,
    TVShowGroup,
)


@pytest.fixture
def config():
    """Create a test configuration"""
    return Config(
        tmdb_api_key="test_tmdb_key",
        tvdb_api_key="test_tvdb_key",
        dry_run=True,
        verbose=True,
        supported_extensions=[".mkv", ".mp4", ".avi"],
    )


@pytest.fixture
def mock_api_manager():
    """Mock API manager that returns enhanced metadata"""
    with patch("media_renamer.tv_show_consolidator.APIClientManager") as mock:
        manager_instance = Mock()
        manager_instance.enhance_media_info.return_value = MediaInfo(
            original_path=Path("/test"),
            media_type=MediaType.TV_SHOW,
            title="WWE SmackDown",
            year=1999,
            tvdb_id="73255",
            extension="",
        )
        mock.return_value = manager_instance
        yield manager_instance


@pytest.fixture
def sample_tv_directories(tmp_path):
    """Create sample TV show directories for testing"""
    # Create SmackDown directories with different naming patterns
    dirs = {
        "smackdown_2016": tmp_path / "2016 SmackDown - XWT",
        "smackdown_2012": tmp_path / "SmackDown.2012.Pack.720p.WEB.h264-WD",
        "smackdown_2013": tmp_path / "SmackDown.2013.Pack.720p.WEB.h264-WD",
        "smackdown_2017": tmp_path / "SmackDown 2017",
        "smackdown_2018": tmp_path / "SmackDown 2018",
        "different_show": tmp_path / "Supernatural Season 1",
    }

    # Create directories and add sample video files
    for _, dir_path in dirs.items():
        dir_path.mkdir()
        # Add a sample video file to make it a valid TV directory
        (dir_path / "sample.mkv").touch()

    return dirs


class TestTVShowConsolidator:

    def test_normalize_show_title(self, config):
        consolidator = TVShowConsolidator(config)

        # Test basic normalization
        assert consolidator._normalize_show_title("WWE SmackDown Live") == "smackdown"
        assert consolidator._normalize_show_title("SmackDown 2018") == "smackdown"
        assert (
            consolidator._normalize_show_title("Friday Night SmackDown") == "smackdown"
        )

        # Test other shows
        assert consolidator._normalize_show_title("Supernatural") == "supernatural"
        assert (
            consolidator._normalize_show_title("The Walking Dead") == "the walking dead"
        )

    def test_extract_show_title(self, config):
        consolidator = TVShowConsolidator(config)

        # Test SmackDown variations
        assert "SmackDown" in consolidator._extract_show_title("2016 SmackDown - XWT")
        assert "SmackDown" in consolidator._extract_show_title(
            "SmackDown.2012.Pack.720p.WEB.h264-WD"
        )
        assert "SmackDown" in consolidator._extract_show_title("SmackDown 2018")

        # Test other shows
        assert "Supernatural" in consolidator._extract_show_title(
            "Supernatural Season 1"
        )

    def test_extract_season_from_name(self, config):
        consolidator = TVShowConsolidator(config)

        # Test explicit season patterns
        assert consolidator._extract_season_from_name("Supernatural Season 1") == 1
        assert consolidator._extract_season_from_name("Breaking Bad S05") == 5
        assert consolidator._extract_season_from_name("Game of Thrones S8") == 8

        # Test no season found (years should not be detected as seasons)
        assert consolidator._extract_season_from_name("SmackDown 2018") is None
        assert consolidator._extract_season_from_name("SmackDown 2020") is None
        assert consolidator._extract_season_from_name("SmackDown 2012") is None

        # Test valid 1-2 digit seasons still work
        assert consolidator._extract_season_from_name("Season 1") == 1
        assert consolidator._extract_season_from_name("Season 25") == 25

    def test_extract_year_from_name(self, config):
        consolidator = TVShowConsolidator(config)

        # Test year extraction
        assert consolidator._extract_year_from_name("SmackDown 2018") == 2018
        assert consolidator._extract_year_from_name("2016 SmackDown - XWT") == 2016
        assert (
            consolidator._extract_year_from_name("SmackDown.2012.Pack.720p.WEB.h264-WD")
            == 2012
        )

        # Test no year found
        assert consolidator._extract_year_from_name("Supernatural Season 1") is None

    def test_has_video_files(self, config, tmp_path):
        consolidator = TVShowConsolidator(config)

        # Directory with video files
        video_dir = tmp_path / "with_video"
        video_dir.mkdir()
        (video_dir / "episode.mkv").touch()
        assert consolidator._has_video_files(video_dir) is True

        # Directory without video files
        no_video_dir = tmp_path / "no_video"
        no_video_dir.mkdir()
        (no_video_dir / "readme.txt").touch()
        assert consolidator._has_video_files(no_video_dir) is False

    @patch("media_renamer.tv_show_consolidator.MetadataExtractor")
    def test_analyze_directory_for_tv_content(self, mock_extractor, config, tmp_path):
        # Setup mock extractor
        mock_extractor_instance = Mock()
        mock_extractor_instance.extract_from_filename.return_value = MediaInfo(
            original_path=Path("/test.mkv"),
            media_type=MediaType.TV_SHOW,
            title="SmackDown",
            season=1,
            episode=1,
            extension=".mkv",
        )
        mock_extractor.return_value = mock_extractor_instance

        consolidator = TVShowConsolidator(config)

        # Create test directory with video file
        test_dir = tmp_path / "SmackDown 2018"
        test_dir.mkdir()
        (test_dir / "episode.mkv").touch()

        result = consolidator._analyze_directory_for_tv_content(test_dir)

        assert result is not None
        assert result.show_title == "SmackDown"
        assert result.year == 2018
        assert result.normalized_title == "smackdown"

    def test_are_same_show(self, config):
        consolidator = TVShowConsolidator(config)

        # Create test directories
        dir1 = TVShowDirectory(
            path=Path("/test1"),
            show_title="WWE SmackDown",
            normalized_title="smackdown",
        )
        dir2 = TVShowDirectory(
            path=Path("/test2"),
            show_title="SmackDown Live",
            normalized_title="smackdown",
        )
        dir3 = TVShowDirectory(
            path=Path("/test3"),
            show_title="Supernatural",
            normalized_title="supernatural",
        )

        # Test same show detection
        assert consolidator._are_same_show(dir1, dir2) is True
        assert consolidator._are_same_show(dir1, dir3) is False

    def test_map_year_to_season(self, config):
        consolidator = TVShowConsolidator(config)

        # Create test group with base year
        group = TVShowGroup(
            show_title="SmackDown", year=1999  # SmackDown started in 1999
        )

        # Test year to season mapping
        assert consolidator._map_year_to_season(1999, group) == 1  # First season
        assert consolidator._map_year_to_season(2000, group) == 2  # Second season
        assert consolidator._map_year_to_season(2012, group) == 14  # 2012 -> Season 14
        assert consolidator._map_year_to_season(2013, group) == 15  # 2013 -> Season 15
        assert consolidator._map_year_to_season(2016, group) == 18  # 2016 -> Season 18
        assert consolidator._map_year_to_season(2017, group) == 19  # 2017 -> Season 19
        assert consolidator._map_year_to_season(2018, group) == 20  # 2018 -> Season 20
        assert consolidator._map_year_to_season(2020, group) == 22  # 2020 -> Season 22

        # Test invalid mappings
        assert consolidator._map_year_to_season(None, group) is None
        assert consolidator._map_year_to_season(1950, group) is None  # Too early

    def test_generate_unified_directory_name(self, config):
        consolidator = TVShowConsolidator(config)

        # Test with full metadata
        group = TVShowGroup(show_title="WWE SmackDown", year=1999, tvdb_id="73255")

        result = consolidator._generate_unified_directory_name(group)
        expected = "WWE SmackDown (1999) [tvdbid-73255]"
        assert result == expected

        # Test without TVDB ID
        group_no_tvdb = TVShowGroup(show_title="WWE SmackDown", year=1999)

        result_no_tvdb = consolidator._generate_unified_directory_name(group_no_tvdb)
        expected_no_tvdb = "WWE SmackDown (1999)"
        assert result_no_tvdb == expected_no_tvdb

    @patch("media_renamer.tv_show_consolidator.shutil.move")
    def test_move_directory_contents(self, mock_move, config, tmp_path):
        consolidator = TVShowConsolidator(config)

        # Create source directory with files
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.mkv").touch()
        (source_dir / "file2.mp4").touch()

        # Create destination directory
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        # Test moving contents
        consolidator._move_directory_contents(source_dir, dest_dir)

        # Verify shutil.move was called for each file
        assert mock_move.call_count == 2

    def test_discover_tv_directories(
        self, config, sample_tv_directories, mock_api_manager
    ):
        with patch("media_renamer.tv_show_consolidator.MetadataExtractor"):
            consolidator = TVShowConsolidator(config)

            # Mock the directory analysis to return valid TV directories
            with patch.object(
                consolidator, "_analyze_directory_for_tv_content"
            ) as mock_analyze:
                mock_analyze.side_effect = lambda d: (
                    TVShowDirectory(
                        path=d,
                        show_title=(
                            "SmackDown"
                            if "smackdown" in d.name.lower()
                            else "Supernatural"
                        ),
                        normalized_title=(
                            "smackdown"
                            if "smackdown" in d.name.lower()
                            else "supernatural"
                        ),
                        year=2018,
                    )
                    if d.name != "sample.mkv"
                    else None
                )

                root_dir = sample_tv_directories["smackdown_2016"].parent
                tv_dirs = consolidator._discover_tv_directories(root_dir)

                # Should find multiple TV directories
                assert len(tv_dirs) > 0


@pytest.mark.integration
class TestTVShowConsolidatorIntegration:

    @patch("media_renamer.tv_show_consolidator.APIClientManager")
    def test_full_consolidation_workflow(
        self, mock_api_manager_class, config, sample_tv_directories
    ):
        """Test the complete consolidation workflow"""

        # Setup mock API manager
        mock_api_manager = Mock()
        mock_api_manager.enhance_media_info.return_value = MediaInfo(
            original_path=Path("/test"),
            media_type=MediaType.TV_SHOW,
            title="WWE SmackDown",
            year=1999,
            tvdb_id="73255",
            extension="",
        )
        mock_api_manager_class.return_value = mock_api_manager

        # Create consolidator
        consolidator = TVShowConsolidator(config)

        # Mock directory analysis to return SmackDown directories
        with patch.object(
            consolidator, "_analyze_directory_for_tv_content"
        ) as mock_analyze:

            def mock_analyze_func(directory):
                name = directory.name.lower()
                if "smackdown" in name:
                    year = None
                    if "2016" in name:
                        year = 2016
                    elif "2012" in name:
                        year = 2012
                    elif "2018" in name:
                        year = 2018

                    return TVShowDirectory(
                        path=directory,
                        show_title="SmackDown",
                        normalized_title="smackdown",
                        year=year,
                    )
                return None

            mock_analyze.side_effect = mock_analyze_func

            # Run consolidation
            root_dir = sample_tv_directories["smackdown_2016"].parent
            results = consolidator.consolidate_tv_shows(root_dir)

            # Verify results
            assert len(results) > 0
            result = results[0]
            assert result["show_title"] == "WWE SmackDown"
            assert result["tvdb_id"] == "73255"
            assert "WWE SmackDown (1999) [tvdbid-73255]" in result["unified_directory"]


if __name__ == "__main__":
    pytest.main([__file__])
