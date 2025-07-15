import os
from unittest.mock import Mock, patch

from click.testing import CliRunner

from media_renamer.cli import display_results, main, setup_logging
from media_renamer.models import RenameResult


class TestCLI:
    """Test cases for CLI functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.runner = CliRunner()

    def test_main_with_valid_directory(self, temp_dir):
        """Test main CLI function with valid directory"""
        # Create test files
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer

            # Mock successful rename result
            mock_result = RenameResult(
                original_path=test_file,
                new_path=temp_dir / "Movie (2020).mkv",
                success=True,
                error=None,
            )
            mock_renamer.process_directory.return_value = [mock_result]

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert "Processing directory:" in result.output
            assert str(temp_dir) in result.output

    def test_main_with_dry_run_flag(self, temp_dir):
        """Test main CLI function with dry run flag"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir), "--dry-run"])

            assert result.exit_code == 0
            assert "Dry run: True" in result.output

            # Check that config was set correctly
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.dry_run is True

    def test_main_with_verbose_flag(self, temp_dir):
        """Test main CLI function with verbose flag"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir), "--verbose"])

            assert result.exit_code == 0

            # Check that config was set correctly
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.verbose is True

    def test_main_with_api_keys(self, temp_dir):
        """Test main CLI function with API keys"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(
                main,
                [
                    str(temp_dir),
                    "--tmdb-key",
                    "test_tmdb_key",
                    "--tvdb-key",
                    "test_tvdb_key",
                ],
            )

            assert result.exit_code == 0

            # Check that config was set correctly
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.tmdb_api_key == "test_tmdb_key"
            assert config.tvdb_api_key == "test_tvdb_key"

    def test_main_with_custom_patterns(self, temp_dir):
        """Test main CLI function with custom patterns"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(
                main,
                [
                    str(temp_dir),
                    "--movie-pattern",
                    "{title} [{year}]",
                    "--tv-pattern",
                    "{title} {season}x{episode} {episode_title}",
                ],
            )

            assert result.exit_code == 0

            # Check that config was set correctly
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.movie_pattern == "{title} [{year}]"
            assert config.tv_pattern == "{title} {season}x{episode} {episode_title}"

    def test_main_with_custom_extensions(self, temp_dir):
        """Test main CLI function with custom extensions"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(
                main, [str(temp_dir), "--extensions", ".mkv,.mp4,.avi"]
            )

            assert result.exit_code == 0

            # Check that config was set correctly
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.supported_extensions == [".mkv", ".mp4", ".avi"]

    def test_main_with_no_api_keys_warning(self, temp_dir):
        """Test main CLI function shows warning when no API keys provided"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with (
            patch("media_renamer.cli.FileRenamer") as mock_renamer_class,
            patch.dict(
                os.environ,
                {"TMDB_API_KEY": "", "TVDB_API_KEY": "", "DRY_RUN": "false"},
                clear=False,
            ),
        ):
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert (
                "Warning: No API keys provided. Limited metadata will be available."
                in result.output
            )

    def test_main_with_environment_variables(self, temp_dir):
        """Test main CLI function with environment variables"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with (
            patch("media_renamer.cli.FileRenamer") as mock_renamer_class,
            patch.dict(
                os.environ,
                {
                    "TMDB_API_KEY": "env_tmdb_key",
                    "TVDB_API_KEY": "env_tvdb_key",
                    "DRY_RUN": "false",
                },
            ),
        ):
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert (
                "Warning: No API keys provided. Limited metadata will be available."
                not in result.output
            )

            # Check that config was loaded from environment
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.tmdb_api_key == "env_tmdb_key"
            assert config.tvdb_api_key == "env_tvdb_key"

    def test_main_with_nonexistent_directory(self):
        """Test main CLI function with nonexistent directory"""
        result = self.runner.invoke(main, ["/nonexistent/directory"])

        assert result.exit_code != 0
        assert (
            "does not exist" in result.output
            or "No such file or directory" in result.output
        )

    def test_main_with_file_instead_of_directory(self, temp_dir):
        """Test main CLI function with file instead of directory"""
        test_file = temp_dir / "test.txt"
        test_file.touch()

        result = self.runner.invoke(main, [str(test_file)])

        # File is handled gracefully - not an error condition
        assert result.exit_code == 0
        assert "No media files found to process" in result.output

    def test_main_with_no_media_files(self, temp_dir):
        """Test main CLI function with directory containing no media files"""
        # Create non-media files
        (temp_dir / "document.txt").touch()
        (temp_dir / "image.jpg").touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert "No media files found to process" in result.output

    def test_main_with_successful_results(self, temp_dir):
        """Test main CLI function with successful rename results"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with (
            patch("media_renamer.cli.FileRenamer") as mock_renamer_class,
            patch.dict(os.environ, {"DRY_RUN": "false"}, clear=False),
        ):
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer

            # Mock successful results
            mock_results = [
                RenameResult(
                    original_path=test_file,
                    new_path=temp_dir / "Movie (2020).mkv",
                    success=True,
                    error=None,
                )
            ]
            mock_renamer.process_directory.return_value = mock_results

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert "✓" in result.output  # Success indicator
            assert "Renamed 1 files successfully" in result.output

    def test_main_with_failed_results(self, temp_dir):
        """Test main CLI function with failed rename results"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer

            # Mock failed results
            mock_results = [
                RenameResult(
                    original_path=test_file,
                    new_path=test_file,
                    success=False,
                    error="Test error",
                )
            ]
            mock_renamer.process_directory.return_value = mock_results

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert "✗" in result.output  # Failure indicator
            assert "Failed to rename 1 files" in result.output
            assert "Test error" in result.output

    def test_main_with_mixed_results(self, temp_dir):
        """Test main CLI function with mixed successful and failed results"""
        test_file1 = temp_dir / "Movie1.2020.mkv"
        test_file2 = temp_dir / "Movie2.2020.mkv"
        test_file1.touch()
        test_file2.touch()

        with (
            patch("media_renamer.cli.FileRenamer") as mock_renamer_class,
            patch.dict(os.environ, {"DRY_RUN": "false"}, clear=False),
        ):
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer

            # Mock mixed results
            mock_results = [
                RenameResult(
                    original_path=test_file1,
                    new_path=temp_dir / "Movie1 (2020).mkv",
                    success=True,
                    error=None,
                ),
                RenameResult(
                    original_path=test_file2,
                    new_path=test_file2,
                    success=False,
                    error="Test error",
                ),
            ]
            mock_renamer.process_directory.return_value = mock_results

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            assert "✓" in result.output  # Success indicator
            assert "✗" in result.output  # Failure indicator
            assert "Renamed 1 files successfully" in result.output
            assert "Failed to rename 1 files" in result.output


            # Check that dry_run was set correctly
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.dry_run is False

    def test_display_results_with_successful_results(self, temp_dir):
        """Test display_results function with successful results"""
        from rich.console import Console

        test_file = temp_dir / "Movie.2020.mkv"
        results = [
            RenameResult(
                original_path=test_file,
                new_path=temp_dir / "Movie (2020).mkv",
                success=True,
                error=None,
            )
        ]

        console = Console()

        # This should not raise an exception
        display_results(console, results, dry_run=False)

    def test_display_results_with_failed_results(self, temp_dir):
        """Test display_results function with failed results"""
        from rich.console import Console

        test_file = temp_dir / "Movie.2020.mkv"
        results = [
            RenameResult(
                original_path=test_file,
                new_path=test_file,
                success=False,
                error="Test error",
            )
        ]

        console = Console()

        # This should not raise an exception
        display_results(console, results, dry_run=False)

    def test_display_results_dry_run_mode(self, temp_dir):
        """Test display_results function in dry run mode"""
        from rich.console import Console

        test_file = temp_dir / "Movie.2020.mkv"
        results = [
            RenameResult(
                original_path=test_file,
                new_path=temp_dir / "Movie (2020).mkv",
                success=True,
                error=None,
            )
        ]

        console = Console()

        # This should not raise an exception
        display_results(console, results, dry_run=True)

    def test_display_results_empty_list(self):
        """Test display_results function with empty results list"""
        from rich.console import Console

        console = Console()

        # This should not raise an exception
        display_results(console, [], dry_run=False)

    def test_setup_logging_default(self):
        """Test setup_logging function with default settings"""
        import logging

        # Reset logging to test the function
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.root.setLevel(logging.WARNING)

        setup_logging()

        logger = logging.getLogger()
        assert logger.level == logging.INFO

    def test_setup_logging_verbose(self):
        """Test setup_logging function with verbose mode"""
        import logging

        # Reset logging to test the function
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.root.setLevel(logging.WARNING)

        setup_logging(verbose=True)

        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

    def test_cli_help_message(self):
        """Test CLI help message"""
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Rename movie and TV show files" in result.output
        assert "PATH" in result.output
        assert "--dry-run" in result.output
        assert "--verbose" in result.output
        assert "--tmdb-key" in result.output
        assert "--tvdb-key" in result.output

    def test_cli_version_or_about(self):
        """Test CLI version or about information"""
        # Click doesn't have a built-in version option in our CLI
        # This test ensures the help shows the expected structure
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Options:" in result.output

    @patch("media_renamer.cli.load_dotenv")
    def test_dotenv_loading(self, mock_load_dotenv, temp_dir):
        """Test that .env file is loaded"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            mock_load_dotenv.assert_called_once()

    def test_cli_with_all_options(self, temp_dir):
        """Test CLI with all options provided"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(
                main,
                [
                    str(temp_dir),
                    "--dry-run",
                    "--verbose",
                    "--tmdb-key",
                    "test_tmdb",
                    "--tvdb-key",
                    "test_tvdb",
                    "--movie-pattern",
                    "{title} [{year}]",
                    "--tv-pattern",
                    "{title} {season}x{episode}",
                    "--extensions",
                    ".mkv,.mp4",
                ],
            )

            assert result.exit_code == 0

            # Verify all options were applied
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.dry_run is True
            assert config.verbose is True
            assert config.tmdb_api_key == "test_tmdb"
            assert config.tvdb_api_key == "test_tvdb"
            assert config.movie_pattern == "{title} [{year}]"
            assert config.tv_pattern == "{title} {season}x{episode}"
            assert config.supported_extensions == [".mkv", ".mp4"]

    def test_cli_progress_indicator(self, temp_dir):
        """Test that CLI shows progress indicator"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            result = self.runner.invoke(main, [str(temp_dir)])

            assert result.exit_code == 0
            # Progress indicator should be present
            assert (
                "Processing files" in result.output
                or "Processing directory" in result.output
            )

    def test_cli_extensions_parsing(self, temp_dir):
        """Test that extensions are parsed correctly"""
        test_file = temp_dir / "Movie.2020.mkv"
        test_file.touch()

        with patch("media_renamer.cli.FileRenamer") as mock_renamer_class:
            mock_renamer = Mock()
            mock_renamer_class.return_value = mock_renamer
            mock_renamer.process_directory.return_value = []

            # Test with spaces around commas
            result = self.runner.invoke(
                main, [str(temp_dir), "--extensions", ".mkv, .mp4 , .avi"]
            )

            assert result.exit_code == 0

            # Check that extensions were parsed and stripped
            args, kwargs = mock_renamer_class.call_args
            config = args[0]
            assert config.supported_extensions == [".mkv", ".mp4", ".avi"]
