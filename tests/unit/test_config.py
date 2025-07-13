import os
from unittest.mock import patch

import pytest

from media_renamer.config import Config


class TestConfig:
    """Test cases for Config class"""

    def test_default_config_values(self):
        """Test default configuration values"""
        config = Config()

        assert config.tmdb_api_key is None
        assert config.tvdb_api_key is None
        assert config.imdb_api_key is None
        assert config.movie_pattern == "{title} ({year})"
        assert (
            config.tv_pattern
            == "{title} - S{season:02d}E{episode:02d} - {episode_title}"
        )
        assert config.dry_run is False
        assert config.verbose is False
        assert config.supported_extensions == [
            ".mkv",
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
        ]

    def test_custom_config_values(self):
        """Test custom configuration values"""
        config = Config(
            tmdb_api_key="test_tmdb_key",
            tvdb_api_key="test_tvdb_key",
            imdb_api_key="test_imdb_key",
            movie_pattern="{title} [{year}]",
            tv_pattern="{title} {season}x{episode} {episode_title}",
            dry_run=True,
            verbose=True,
            supported_extensions=[".mkv", ".mp4"],
        )

        assert config.tmdb_api_key == "test_tmdb_key"
        assert config.tvdb_api_key == "test_tvdb_key"
        assert config.imdb_api_key == "test_imdb_key"
        assert config.movie_pattern == "{title} [{year}]"
        assert config.tv_pattern == "{title} {season}x{episode} {episode_title}"
        assert config.dry_run is True
        assert config.verbose is True
        assert config.supported_extensions == [".mkv", ".mp4"]

    @patch.dict(
        os.environ,
        {
            "TMDB_API_KEY": "env_tmdb_key",
            "TVDB_API_KEY": "env_tvdb_key",
            "IMDB_API_KEY": "env_imdb_key",
            "DRY_RUN": "true",
            "VERBOSE": "true",
        },
    )
    def test_load_from_env_with_all_vars(self):
        """Test loading configuration from environment variables"""
        config = Config.load_from_env()

        assert config.tmdb_api_key == "env_tmdb_key"
        assert config.tvdb_api_key == "env_tvdb_key"
        assert config.imdb_api_key == "env_imdb_key"
        assert config.dry_run is True
        assert config.verbose is True

    @patch.dict(os.environ, {"DRY_RUN": "false", "VERBOSE": "false"})
    def test_load_from_env_false_values(self):
        """Test loading false values from environment"""
        config = Config.load_from_env()

        assert config.dry_run is False
        assert config.verbose is False

    @patch.dict(os.environ, {"DRY_RUN": "True", "VERBOSE": "FALSE"})
    def test_load_from_env_case_insensitive(self):
        """Test case insensitive boolean parsing"""
        config = Config.load_from_env()

        assert config.dry_run is True
        assert config.verbose is False

    @patch.dict(os.environ, {"DRY_RUN": "yes", "VERBOSE": "no"})
    def test_load_from_env_non_boolean_values(self):
        """Test non-boolean values are treated as false"""
        config = Config.load_from_env()

        assert config.dry_run is False
        assert config.verbose is False

    @patch.dict(os.environ, {}, clear=True)
    def test_load_from_env_empty_environment(self):
        """Test loading from empty environment"""
        config = Config.load_from_env()

        assert config.tmdb_api_key is None
        assert config.tvdb_api_key is None
        assert config.imdb_api_key is None
        assert config.dry_run is False
        assert config.verbose is False

        # Default values should remain
        assert config.movie_pattern == "{title} ({year})"
        assert (
            config.tv_pattern
            == "{title} - S{season:02d}E{episode:02d} - {episode_title}"
        )

    @patch.dict(
        os.environ, {"TMDB_API_KEY": "", "TVDB_API_KEY": "", "IMDB_API_KEY": ""}
    )
    def test_load_from_env_empty_strings(self):
        """Test loading empty strings from environment"""
        config = Config.load_from_env()

        assert config.tmdb_api_key == ""
        assert config.tvdb_api_key == ""
        assert config.imdb_api_key == ""

    def test_config_is_pydantic_model(self):
        """Test that Config is a proper Pydantic model"""
        config = Config()

        # Should have Pydantic model methods
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")

        # Test serialization
        data = config.model_dump()
        assert isinstance(data, dict)
        assert "tmdb_api_key" in data
        assert "movie_pattern" in data

        # Test validation
        new_config = Config.model_validate(data)
        assert new_config.movie_pattern == config.movie_pattern

    def test_config_validation_with_invalid_data(self):
        """Test config validation with invalid data"""
        with pytest.raises(ValueError):
            Config(dry_run="invalid_boolean")

        with pytest.raises(ValueError):
            Config(verbose="invalid_boolean")

    def test_config_with_none_values(self):
        """Test config with None values"""
        config = Config(tmdb_api_key=None, tvdb_api_key=None, imdb_api_key=None)

        assert config.tmdb_api_key is None
        assert config.tvdb_api_key is None
        assert config.imdb_api_key is None

    def test_config_immutability(self):
        """Test that config fields can be modified after creation"""
        config = Config()

        # Pydantic models are mutable by default
        config.dry_run = True
        config.verbose = True

        assert config.dry_run is True
        assert config.verbose is True

    def test_supported_extensions_validation(self):
        """Test supported extensions validation"""
        config = Config(supported_extensions=[".mkv", ".mp4", ".avi"])

        assert ".mkv" in config.supported_extensions
        assert ".mp4" in config.supported_extensions
        assert ".avi" in config.supported_extensions
        assert len(config.supported_extensions) == 3

    def test_pattern_validation(self):
        """Test pattern validation"""
        # Valid patterns
        valid_movie_pattern = "{title} ({year})"
        valid_tv_pattern = "{title} - S{season:02d}E{episode:02d} - {episode_title}"

        config = Config(movie_pattern=valid_movie_pattern, tv_pattern=valid_tv_pattern)

        assert config.movie_pattern == valid_movie_pattern
        assert config.tv_pattern == valid_tv_pattern

    def test_config_field_types(self):
        """Test that config fields have correct types"""
        config = Config()

        # Optional string fields
        assert config.tmdb_api_key is None or isinstance(config.tmdb_api_key, str)
        assert config.tvdb_api_key is None or isinstance(config.tvdb_api_key, str)
        assert config.imdb_api_key is None or isinstance(config.imdb_api_key, str)

        # String fields
        assert isinstance(config.movie_pattern, str)
        assert isinstance(config.tv_pattern, str)

        # Boolean fields
        assert isinstance(config.dry_run, bool)
        assert isinstance(config.verbose, bool)

        # List field
        assert isinstance(config.supported_extensions, list)
        assert all(isinstance(ext, str) for ext in config.supported_extensions)

    def test_config_with_custom_extensions(self):
        """Test config with custom supported extensions"""
        custom_extensions = [".mkv", ".mp4", ".avi", ".webm", ".flv"]
        config = Config(supported_extensions=custom_extensions)

        assert config.supported_extensions == custom_extensions
        assert len(config.supported_extensions) == 5

    def test_config_pattern_format_validation(self):
        """Test that patterns can be formatted correctly"""
        config = Config()

        # Test movie pattern
        movie_formatted = config.movie_pattern.format(title="Test Movie", year=2020)
        assert movie_formatted == "Test Movie (2020)"

        # Test TV pattern
        tv_formatted = config.tv_pattern.format(
            title="Test Show", season=1, episode=5, episode_title="Test Episode"
        )
        assert tv_formatted == "Test Show - S01E05 - Test Episode"

    def test_config_equality(self):
        """Test config equality comparison"""
        config1 = Config(tmdb_api_key="test_key", dry_run=True, verbose=False)

        config2 = Config(tmdb_api_key="test_key", dry_run=True, verbose=False)

        config3 = Config(tmdb_api_key="different_key", dry_run=True, verbose=False)

        assert config1 == config2
        assert config1 != config3

    def test_config_repr(self):
        """Test config string representation"""
        config = Config(tmdb_api_key="test_key", dry_run=True)

        repr_str = repr(config)
        assert "Config" in repr_str
        assert "tmdb_api_key=" in repr_str
        assert "dry_run=True" in repr_str
