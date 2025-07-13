"""
Test coverage configuration and utilities
"""

from pathlib import Path

import pytest


def test_coverage_configuration():
    """Test that coverage configuration is properly set"""
    # This test ensures our coverage configuration is working
    # It's mainly for verification that the pytest-cov plugin is working

    # Get the project root
    project_root = Path(__file__).parent.parent

    # Check that source files exist
    source_files = [
        project_root / "media_renamer" / "__init__.py",
        project_root / "media_renamer" / "cli.py",
        project_root / "media_renamer" / "config.py",
        project_root / "media_renamer" / "models.py",
        project_root / "media_renamer" / "metadata_extractor.py",
        project_root / "media_renamer" / "api_clients.py",
        project_root / "media_renamer" / "renamer.py",
        project_root / "media_renamer" / "main.py",
    ]

    for source_file in source_files:
        assert source_file.exists(), f"Source file {source_file} does not exist"


def test_all_modules_importable():
    """Test that all modules can be imported without errors"""

    # Test individual module imports
    try:
        import media_renamer.api_clients  # noqa: F401
        import media_renamer.cli  # noqa: F401
        import media_renamer.config  # noqa: F401
        import media_renamer.main  # noqa: F401
        import media_renamer.metadata_extractor  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")


def test_main_entry_point():
    """Test that main entry point is accessible"""
    from media_renamer.main import main

    # Should be callable (we're not actually calling it)
    assert callable(main)


def test_cli_entry_point():
    """Test that CLI entry point is accessible"""
    from media_renamer.cli import main

    # Should be callable
    assert callable(main)


def test_all_classes_instantiable():
    """Test that all main classes can be instantiated"""
    from media_renamer.api_clients import APIClientManager
    from media_renamer.config import Config
    from media_renamer.metadata_extractor import MetadataExtractor
    from media_renamer.renamer import FileRenamer

    # Test Config
    config = Config()
    assert config is not None

    # Test MetadataExtractor
    extractor = MetadataExtractor()
    assert extractor is not None

    # Test APIClientManager
    api_manager = APIClientManager()
    assert api_manager is not None

    # Test FileRenamer
    renamer = FileRenamer(config)
    assert renamer is not None


def test_models_can_be_created():
    """Test that all models can be created"""
    import tempfile
    from pathlib import Path

    from media_renamer.models import MediaInfo, MediaType, RenameResult

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test.mkv"
        temp_path.touch()

        # Test MediaInfo
        media_info = MediaInfo(
            original_path=temp_path,
            media_type=MediaType.MOVIE,
            title="Test",
            extension=".mkv",
        )
        assert media_info is not None

        # Test RenameResult
        rename_result = RenameResult(
            original_path=temp_path, new_path=temp_path, success=True
        )
        assert rename_result is not None


def test_enums_accessible():
    """Test that all enums are accessible"""
    from media_renamer.models import MediaType

    # Test MediaType enum
    assert MediaType.MOVIE == "movie"
    assert MediaType.TV_SHOW == "tv_show"
    assert MediaType.UNKNOWN == "unknown"


def test_constants_defined():
    """Test that important constants are defined"""
    from media_renamer.config import Config

    # Test default config values
    config = Config()
    assert config.movie_pattern is not None
    assert config.tv_pattern is not None
    assert len(config.supported_extensions) > 0


def test_api_clients_structure():
    """Test that API clients have required structure"""
    from media_renamer.api_clients import (
        APIClientManager,
        BaseAPIClient,
        TMDBClient,
        TVDBClient,
    )

    # Test that classes exist
    assert BaseAPIClient is not None
    assert TMDBClient is not None
    assert TVDBClient is not None
    assert APIClientManager is not None

    # Test that TMDBClient inherits from BaseAPIClient
    assert issubclass(TMDBClient, BaseAPIClient)
    assert issubclass(TVDBClient, BaseAPIClient)


def test_metadata_extractor_patterns():
    """Test that metadata extractor has required patterns"""
    from media_renamer.metadata_extractor import MetadataExtractor

    extractor = MetadataExtractor()

    # Test that patterns exist
    assert hasattr(extractor, "season_episode_patterns")
    assert hasattr(extractor, "year_pattern")
    assert len(extractor.season_episode_patterns) > 0
    assert extractor.year_pattern is not None


def test_file_renamer_methods():
    """Test that FileRenamer has required methods"""
    from media_renamer.config import Config
    from media_renamer.renamer import FileRenamer

    config = Config()
    renamer = FileRenamer(config)

    # Test that methods exist
    assert hasattr(renamer, "rename_file")
    assert hasattr(renamer, "process_directory")
    assert hasattr(renamer, "_generate_filename")
    assert hasattr(renamer, "_generate_movie_filename")
    assert hasattr(renamer, "_generate_tv_filename")
    assert hasattr(renamer, "_sanitize_filename")

    # Test that methods are callable
    assert callable(renamer.rename_file)
    assert callable(renamer.process_directory)


def test_cli_functions():
    """Test that CLI functions exist"""
    from media_renamer.cli import display_results, main, setup_logging

    # Test that functions exist
    assert callable(main)
    assert callable(display_results)
    assert callable(setup_logging)


def test_no_syntax_errors():
    """Test that there are no syntax errors in any module"""
    import ast
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    source_dir = project_root / "media_renamer"

    # Test all Python files in the source directory
    for py_file in source_dir.glob("*.py"):
        with open(py_file, encoding="utf-8") as f:
            content = f.read()

        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {py_file}: {e}")


if __name__ == "__main__":
    # Run coverage tests
    test_coverage_configuration()
    test_all_modules_importable()
    test_main_entry_point()
    test_cli_entry_point()
    test_all_classes_instantiable()
    test_models_can_be_created()
    test_enums_accessible()
    test_constants_defined()
    test_api_clients_structure()
    test_metadata_extractor_patterns()
    test_file_renamer_methods()
    test_cli_functions()
    test_no_syntax_errors()

    print("All coverage tests passed!")
