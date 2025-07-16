from unittest.mock import Mock, patch

from media_renamer.config import Config
from media_renamer.renamer import FileRenamer


class TestFullWorkflow:
    """Integration tests for the complete file renaming workflow"""

    def test_complete_movie_workflow(self, temp_dir):
        """Test complete workflow for movie files"""
        # Create test files
        movie_files = [
            "The.Matrix.1999.1080p.BluRay.x264.mkv",
            "Inception.2010.720p.HDTV.x264.mp4",
            "The.Godfather.1972.1080p.BluRay.x264.avi",
        ]

        for filename in movie_files:
            (temp_dir / filename).touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=False,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with (
            patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit,
            patch("media_renamer.api_clients.TMDBClient") as mock_tmdb_class
        ):
            # Mock guessit responses
            def mock_guessit_side_effect(filename):
                if "Matrix" in filename:
                    return {
                        "title": "The Matrix",
                        "year": 1999,
                        "type": "movie",
                        "container": "mkv",
                    }
                elif "Inception" in filename:
                    return {
                        "title": "Inception",
                        "year": 2010,
                        "type": "movie",
                        "container": "mp4",
                    }
                elif "Godfather" in filename:
                    return {
                        "title": "The Godfather",
                        "year": 1972,
                        "type": "movie",
                        "container": "avi",
                    }
                return {}

            mock_guessit.side_effect = mock_guessit_side_effect

            # Mock TMDB client
            mock_tmdb = Mock()
            mock_tmdb_class.return_value = mock_tmdb

            def mock_search_movie(title, year=None):
                if "Matrix" in title:
                    return {
                        "title": "The Matrix",
                        "year": 1999,
                        "tmdb_id": 603,
                        "imdb_id": "tt0133093",
                    }
                elif "Inception" in title:
                    return {
                        "title": "Inception",
                        "year": 2010,
                        "tmdb_id": 27205,
                        "imdb_id": "tt1375666",
                    }
                elif "Godfather" in title:
                    return {
                        "title": "The Godfather",
                        "year": 1972,
                        "tmdb_id": 238,
                        "imdb_id": "tt0068646",
                    }
                return None

            mock_tmdb.search_movie.side_effect = mock_search_movie

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == 3
            assert all(result.success for result in results)

            # Check that files were renamed correctly
            expected_names = [
                "The Matrix (1999).mkv",
                "Inception (2010).mp4",
                "The Godfather (1972).avi",
            ]

            actual_names = [result.new_path.name for result in results]
            for expected in expected_names:
                assert expected in actual_names

            # Check that new files exist and old files are gone
            for result in results:
                assert result.new_path.exists()
                assert not result.original_path.exists()

    def test_complete_tv_workflow(self, temp_dir):
        """Test complete workflow for TV show files"""
        # Create test files
        tv_files = [
            "Breaking.Bad.S01E01.720p.HDTV.x264.mkv",
            "Game.of.Thrones.S01E01.Winter.Is.Coming.1080p.BluRay.x264.mp4",
            "The.Office.US.S02E01.The.Dundies.720p.HDTV.x264.avi",
        ]

        for filename in tv_files:
            (temp_dir / filename).touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=False,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with (
            patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit,
            patch(
                "media_renamer.api_clients.APIClientManager"
            ) as mock_api_manager_class
        ):
            # Mock guessit responses
            def mock_guessit_side_effect(filename):
                if "Breaking.Bad" in filename:
                    return {
                        "title": "Breaking Bad",
                        "season": 1,
                        "episode": 1,
                        "type": "episode",
                        "container": "mkv",
                    }
                elif "Game.of.Thrones" in filename:
                    return {
                        "title": "Game of Thrones",
                        "season": 1,
                        "episode": 1,
                        "episode_title": "Winter Is Coming",
                        "type": "episode",
                        "container": "mp4",
                    }
                elif "The.Office" in filename:
                    return {
                        "title": "The Office US",
                        "season": 2,
                        "episode": 1,
                        "episode_title": "The Dundies",
                        "type": "episode",
                        "container": "avi",
                    }
                return {}

            mock_guessit.side_effect = mock_guessit_side_effect

            # Mock APIClientManager
            mock_api_manager = Mock()
            mock_api_manager_class.return_value = mock_api_manager

            def mock_enhance_media_info(media_info):
                # For TV shows, enhance with API data
                if media_info.is_tv_show:
                    if "Breaking Bad" in media_info.title:
                        media_info.title = "Breaking Bad"
                        media_info.year = 2008
                        media_info.tvdb_id = "81189"
                        if media_info.season == 1 and media_info.episode == 1:
                            media_info.episode_title = "Pilot"
                    elif "Game of Thrones" in media_info.title:
                        media_info.title = "Game of Thrones"
                        media_info.year = 2011
                        media_info.tvdb_id = "121361"
                        if media_info.season == 1 and media_info.episode == 1:
                            media_info.episode_title = "Winter Is Coming"
                    elif "Office" in media_info.title:
                        media_info.title = "The Office (US)"
                        media_info.year = 2005
                        media_info.tvdb_id = "73244"
                        if media_info.season == 2 and media_info.episode == 1:
                            media_info.episode_title = "The Dundies"
                return media_info

            mock_api_manager.enhance_media_info.side_effect = mock_enhance_media_info

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == 3
            assert all(result.success for result in results)

            # Check that files were renamed correctly
            expected_names = [
                "Breaking Bad - S01E01 - Pilot.mkv",
                "Game of Thrones - S01E01 - Winter Is Coming.mp4",
                "The Office (US) - S02E01 - The Dundies.avi",
            ]

            actual_names = [result.new_path.name for result in results]
            for expected in expected_names:
                assert expected in actual_names

            # Check that new files exist and old files are gone
            for result in results:
                assert result.new_path.exists()
                assert not result.original_path.exists()

    def test_mixed_media_workflow(self, temp_dir):
        """Test workflow with mixed movie and TV show files"""
        # Create test files
        mixed_files = [
            "The.Matrix.1999.1080p.BluRay.x264.mkv",
            "Breaking.Bad.S01E01.720p.HDTV.x264.mkv",
            "Inception.2010.720p.HDTV.x264.mp4",
            "Game.of.Thrones.S01E01.Winter.Is.Coming.1080p.BluRay.x264.mp4",
            "random_file.mkv",  # Should fail
            "document.txt",  # Should be ignored
        ]

        for filename in mixed_files:
            (temp_dir / filename).touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=False,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with (
            patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit,
            patch(
                "media_renamer.api_clients.APIClientManager"
            ) as mock_api_manager_class
        ):
            # Mock guessit responses
            def mock_guessit_side_effect(filename):
                if "Matrix" in filename:
                    return {"title": "The Matrix", "year": 1999, "type": "movie"}
                elif "Inception" in filename:
                    return {"title": "Inception", "year": 2010, "type": "movie"}
                elif "Breaking.Bad" in filename:
                    return {
                        "title": "Breaking Bad",
                        "season": 1,
                        "episode": 1,
                        "type": "episode",
                    }
                elif "Game.of.Thrones" in filename:
                    return {
                        "title": "Game of Thrones",
                        "season": 1,
                        "episode": 1,
                        "episode_title": "Winter Is Coming",
                        "type": "episode",
                    }
                else:
                    return {"title": "random_file"}  # Unknown type

            mock_guessit.side_effect = mock_guessit_side_effect

            # Mock APIClientManager
            mock_api_manager = Mock()
            mock_api_manager_class.return_value = mock_api_manager

            def mock_enhance_media_info(media_info):
                if media_info.is_movie:
                    if "Matrix" in media_info.title:
                        media_info.title = "The Matrix"
                        media_info.year = 1999
                        media_info.tmdb_id = "603"
                    elif "Inception" in media_info.title:
                        media_info.title = "Inception"
                        media_info.year = 2010
                        media_info.tmdb_id = "27205"
                elif media_info.is_tv_show:
                    if "Breaking Bad" in media_info.title:
                        media_info.title = "Breaking Bad"
                        if media_info.season == 1 and media_info.episode == 1:
                            media_info.episode_title = "Pilot"
                    elif "Game of Thrones" in media_info.title:
                        media_info.title = "Game of Thrones"
                        if media_info.season == 1 and media_info.episode == 1:
                            media_info.episode_title = "Winter Is Coming"
                return media_info

            mock_api_manager.enhance_media_info.side_effect = mock_enhance_media_info

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == 5  # 4 valid media files + 1 unknown

            # Check success/failure counts
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]

            assert len(successful_results) == 4
            assert len(failed_results) == 1

            # Check that the unknown file failed
            failed_file = failed_results[0]
            assert "random_file" in str(failed_file.original_path)
            assert "Could not generate filename" in failed_file.error

    def test_dry_run_workflow(self, temp_dir):
        """Test workflow in dry run mode"""
        # Create test files
        test_files = [
            "The.Matrix.1999.1080p.BluRay.x264.mkv",
            "Breaking.Bad.S01E01.720p.HDTV.x264.mkv",
        ]

        for filename in test_files:
            (temp_dir / filename).touch()

        # Setup config with dry run
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=True,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with (
            patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit,
            patch(
                "media_renamer.api_clients.APIClientManager"
            ) as mock_api_manager_class
        ):
            # Mock guessit responses
            def mock_guessit_side_effect(filename):
                if "Matrix" in filename:
                    return {"title": "The Matrix", "year": 1999, "type": "movie"}
                elif "Breaking.Bad" in filename:
                    return {
                        "title": "Breaking Bad",
                        "season": 1,
                        "episode": 1,
                        "type": "episode",
                    }
                return {}

            mock_guessit.side_effect = mock_guessit_side_effect

            # Mock APIClientManager
            mock_api_manager = Mock()
            mock_api_manager_class.return_value = mock_api_manager

            def mock_enhance_media_info(media_info):
                if media_info.is_movie and "Matrix" in media_info.title:
                    media_info.title = "The Matrix"
                    media_info.year = 1999
                    media_info.tmdb_id = "603"
                elif media_info.is_tv_show and "Breaking Bad" in media_info.title:
                    media_info.title = "Breaking Bad"
                    media_info.episode_title = "Pilot"
                return media_info

            mock_api_manager.enhance_media_info.side_effect = mock_enhance_media_info

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == 2
            assert all(result.success for result in results)

            # Check that original files still exist (dry run mode)
            for result in results:
                assert result.original_path.exists()
                assert not result.new_path.exists()

            # Check that new paths are correctly calculated
            expected_names = [
                "The Matrix (1999).mkv",
                "Breaking Bad - S01E01 - Pilot.mkv",
            ]

            actual_names = [result.new_path.name for result in results]
            for expected in expected_names:
                assert expected in actual_names

    def test_workflow_with_subdirectories(self, temp_dir):
        """Test workflow with files in subdirectories"""
        # Create subdirectory structure
        movies_dir = temp_dir / "movies"
        tv_dir = temp_dir / "tv"
        movies_dir.mkdir()
        tv_dir.mkdir()

        # Create test files in subdirectories
        movie_file = movies_dir / "The.Matrix.1999.1080p.BluRay.x264.mkv"
        tv_file = tv_dir / "Breaking.Bad.S01E01.720p.HDTV.x264.mkv"
        movie_file.touch()
        tv_file.touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=False,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with (
            patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit,
            patch(
                "media_renamer.api_clients.APIClientManager"
            ) as mock_api_manager_class
        ):
            # Mock guessit responses
            def mock_guessit_side_effect(filename):
                if "Matrix" in filename:
                    return {"title": "The Matrix", "year": 1999, "type": "movie"}
                elif "Breaking.Bad" in filename:
                    return {
                        "title": "Breaking Bad",
                        "season": 1,
                        "episode": 1,
                        "type": "episode",
                    }
                return {}

            mock_guessit.side_effect = mock_guessit_side_effect

            # Mock APIClientManager
            mock_api_manager = Mock()
            mock_api_manager_class.return_value = mock_api_manager

            def mock_enhance_media_info(media_info):
                if media_info.is_movie and "Matrix" in media_info.title:
                    media_info.title = "The Matrix"
                    media_info.year = 1999
                    media_info.tmdb_id = "603"
                elif media_info.is_tv_show and "Breaking Bad" in media_info.title:
                    media_info.title = "Breaking Bad"
                    media_info.episode_title = "Pilot"
                return media_info

            mock_api_manager.enhance_media_info.side_effect = mock_enhance_media_info

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == 2
            assert all(result.success for result in results)

            # Check that files were renamed in their respective directories
            expected_movie_path = movies_dir / "The Matrix (1999).mkv"
            expected_tv_path = tv_dir / "Breaking Bad - S01E01 - Pilot.mkv"

            assert expected_movie_path.exists()
            assert expected_tv_path.exists()
            assert not movie_file.exists()
            assert not tv_file.exists()

    def test_workflow_with_api_failures(self, temp_dir):
        """Test workflow when API calls fail"""
        # Create test file
        test_file = temp_dir / "Unknown.Movie.2020.mkv"
        test_file.touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=False,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses with failures
        with (
            patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit,
            patch("media_renamer.api_clients.TMDBClient") as mock_tmdb_class
        ):
            # Mock guessit to return movie info
            mock_guessit.return_value = {
                "title": "Unknown Movie",
                "year": 2020,
                "type": "movie",
            }

            # Mock TMDB client to return None (API failure)
            mock_tmdb = Mock()
            mock_tmdb.search_movie.return_value = None
            mock_tmdb_class.return_value = mock_tmdb

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == 1
            assert results[0].success is True

            # Check that file was renamed with original metadata
            expected_path = temp_dir / "Unknown Movie (2020).mkv"
            assert expected_path.exists()
            assert not test_file.exists()

    def test_workflow_with_file_conflicts(self, temp_dir):
        """Test workflow when target file already exists"""
        # Create test file and conflicting target
        test_file = temp_dir / "Movie.2020.mkv"
        conflict_file = temp_dir / "Movie (2020).mkv"
        test_file.touch()
        conflict_file.touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=False,
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit:
            # Mock guessit to return movie info
            mock_guessit.return_value = {
                "title": "Movie",
                "year": 2020,
                "type": "movie",
            }

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results - we have 2 files processed
            assert len(results) == 2

            # Find the result for the original file that should fail
            failed_result = next(r for r in results if not r.success)
            success_result = next(r for r in results if r.success)

            assert failed_result.success is False
            assert "Target file already exists" in failed_result.error

            # The conflict file should succeed (no change needed)
            assert success_result.success is True

            # Check that original file still exists
            assert test_file.exists()
            assert conflict_file.exists()

    def test_workflow_performance_with_many_files(self, temp_dir):
        """Test workflow performance with many files"""
        # Create many test files
        num_files = 50
        for i in range(num_files):
            test_file = temp_dir / f"Movie.{2000 + i}.mkv"
            test_file.touch()

        # Setup config
        config = Config(
            movie_pattern="{title} ({year})",
            tv_pattern="{title} - S{season:02d}E{episode:02d} - {episode_title}",
            dry_run=True,  # Use dry run for performance
            verbose=False,
            supported_extensions=[".mkv", ".mp4", ".avi"],
        )

        # Mock API responses
        with patch("media_renamer.metadata_extractor.guessit.guessit") as mock_guessit:
            # Mock guessit to return movie info
            def mock_guessit_side_effect(filename):
                # Extract year from filename
                import re

                match = re.search(r"(\d{4})", filename)
                year = int(match.group(1)) if match else 2000
                return {"title": "Movie", "year": year, "type": "movie"}

            mock_guessit.side_effect = mock_guessit_side_effect

            # Run the workflow
            renamer = FileRenamer(config)
            results = renamer.process_directory(temp_dir)

            # Verify results
            assert len(results) == num_files
            assert all(result.success for result in results)

            # Check that all files would be renamed correctly
            # Extract years from the results and verify they're all present
            result_years = set()
            for result in results:
                # Extract year from the new filename
                import re

                match = re.search(r"Movie \((\d{4})\)\.mkv", result.new_path.name)
                if match:
                    result_years.add(int(match.group(1)))

            expected_years = set(range(2000, 2000 + num_files))
            assert result_years == expected_years
