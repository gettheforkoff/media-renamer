import pytest

from media_renamer.models import MediaInfo, MediaType, RenameResult


class TestMediaType:
    """Test cases for MediaType enum"""

    def test_media_type_values(self):
        """Test MediaType enum values"""
        assert MediaType.MOVIE == "movie"
        assert MediaType.TV_SHOW == "tv_show"
        assert MediaType.UNKNOWN == "unknown"

    def test_media_type_string_representation(self):
        """Test string representation of MediaType"""
        assert str(MediaType.MOVIE) == "movie"
        assert str(MediaType.TV_SHOW) == "tv_show"
        assert str(MediaType.UNKNOWN) == "unknown"

    def test_media_type_equality(self):
        """Test MediaType equality"""
        assert MediaType.MOVIE == MediaType.MOVIE
        assert MediaType.TV_SHOW == MediaType.TV_SHOW
        assert MediaType.UNKNOWN == MediaType.UNKNOWN

        assert MediaType.MOVIE != MediaType.TV_SHOW
        assert MediaType.MOVIE != MediaType.UNKNOWN
        assert MediaType.TV_SHOW != MediaType.UNKNOWN


class TestMediaInfo:
    """Test cases for MediaInfo model"""

    def test_movie_media_info_creation(self, temp_dir):
        """Test creating MediaInfo for a movie"""
        movie_path = temp_dir / "movie.mkv"
        movie_path.touch()

        media_info = MediaInfo(
            original_path=movie_path,
            media_type=MediaType.MOVIE,
            title="Test Movie",
            year=2020,
            extension=".mkv",
            tmdb_id=12345,
            imdb_id="tt1234567",
        )

        assert media_info.original_path == movie_path
        assert media_info.media_type == MediaType.MOVIE
        assert media_info.title == "Test Movie"
        assert media_info.year == 2020
        assert media_info.extension == ".mkv"
        assert media_info.tmdb_id == "12345"
        assert media_info.imdb_id == "tt1234567"

        # Optional fields should be None
        assert media_info.season is None
        assert media_info.episode is None
        assert media_info.episode_title is None
        assert media_info.tvdb_id is None

    def test_tv_show_media_info_creation(self, temp_dir):
        """Test creating MediaInfo for a TV show"""
        tv_path = temp_dir / "show.mkv"
        tv_path.touch()

        media_info = MediaInfo(
            original_path=tv_path,
            media_type=MediaType.TV_SHOW,
            title="Test Show",
            year=2020,
            season=1,
            episode=5,
            episode_title="Test Episode",
            extension=".mkv",
            tvdb_id=81189,
            tmdb_id=1396,
        )

        assert media_info.original_path == tv_path
        assert media_info.media_type == MediaType.TV_SHOW
        assert media_info.title == "Test Show"
        assert media_info.year == 2020
        assert media_info.season == 1
        assert media_info.episode == 5
        assert media_info.episode_title == "Test Episode"
        assert media_info.extension == ".mkv"
        assert media_info.tvdb_id == "81189"
        assert media_info.tmdb_id == "1396"

        # Movie-specific field should be None
        assert media_info.imdb_id is None

    def test_unknown_media_info_creation(self, temp_dir):
        """Test creating MediaInfo for unknown media"""
        unknown_path = temp_dir / "unknown.mkv"
        unknown_path.touch()

        media_info = MediaInfo(
            original_path=unknown_path,
            media_type=MediaType.UNKNOWN,
            title="Unknown File",
            extension=".mkv",
        )

        assert media_info.original_path == unknown_path
        assert media_info.media_type == MediaType.UNKNOWN
        assert media_info.title == "Unknown File"
        assert media_info.extension == ".mkv"

        # All optional fields should be None
        assert media_info.year is None
        assert media_info.season is None
        assert media_info.episode is None
        assert media_info.episode_title is None
        assert media_info.tmdb_id is None
        assert media_info.tvdb_id is None
        assert media_info.imdb_id is None

    def test_is_movie_property(self, temp_dir):
        """Test is_movie property"""
        movie_path = temp_dir / "movie.mkv"
        movie_path.touch()

        movie_info = MediaInfo(
            original_path=movie_path,
            media_type=MediaType.MOVIE,
            title="Movie",
            extension=".mkv",
        )

        tv_info = MediaInfo(
            original_path=movie_path,
            media_type=MediaType.TV_SHOW,
            title="Show",
            extension=".mkv",
        )

        unknown_info = MediaInfo(
            original_path=movie_path,
            media_type=MediaType.UNKNOWN,
            title="Unknown",
            extension=".mkv",
        )

        assert movie_info.is_movie is True
        assert tv_info.is_movie is False
        assert unknown_info.is_movie is False

    def test_is_tv_show_property(self, temp_dir):
        """Test is_tv_show property"""
        tv_path = temp_dir / "show.mkv"
        tv_path.touch()

        movie_info = MediaInfo(
            original_path=tv_path,
            media_type=MediaType.MOVIE,
            title="Movie",
            extension=".mkv",
        )

        tv_info = MediaInfo(
            original_path=tv_path,
            media_type=MediaType.TV_SHOW,
            title="Show",
            extension=".mkv",
        )

        unknown_info = MediaInfo(
            original_path=tv_path,
            media_type=MediaType.UNKNOWN,
            title="Unknown",
            extension=".mkv",
        )

        assert movie_info.is_tv_show is False
        assert tv_info.is_tv_show is True
        assert unknown_info.is_tv_show is False

    def test_media_info_with_all_fields(self, temp_dir):
        """Test MediaInfo with all possible fields"""
        file_path = temp_dir / "complete.mkv"
        file_path.touch()

        media_info = MediaInfo(
            original_path=file_path,
            media_type=MediaType.TV_SHOW,
            title="Complete Show",
            year=2020,
            season=2,
            episode=10,
            episode_title="Complete Episode",
            imdb_id="tt1234567",
            tmdb_id=1396,
            tvdb_id=81189,
            extension=".mkv",
        )

        assert media_info.original_path == file_path
        assert media_info.media_type == MediaType.TV_SHOW
        assert media_info.title == "Complete Show"
        assert media_info.year == 2020
        assert media_info.season == 2
        assert media_info.episode == 10
        assert media_info.episode_title == "Complete Episode"
        assert media_info.imdb_id == "tt1234567"
        assert media_info.tmdb_id == "1396"
        assert media_info.tvdb_id == "81189"
        assert media_info.extension == ".mkv"

    def test_media_info_validation(self, temp_dir):
        """Test MediaInfo validation"""
        file_path = temp_dir / "test.mkv"
        file_path.touch()

        # Valid MediaInfo
        media_info = MediaInfo(
            original_path=file_path,
            media_type=MediaType.MOVIE,
            title="Valid Movie",
            extension=".mkv",
        )

        assert media_info.title == "Valid Movie"

        # Test with invalid media type (should raise error)
        with pytest.raises(ValueError):
            MediaInfo(
                original_path=file_path,
                media_type="invalid_type",
                title="Invalid Movie",
                extension=".mkv",
            )

    def test_media_info_equality(self, temp_dir):
        """Test MediaInfo equality"""
        file_path = temp_dir / "test.mkv"
        file_path.touch()

        media_info1 = MediaInfo(
            original_path=file_path,
            media_type=MediaType.MOVIE,
            title="Test Movie",
            year=2020,
            extension=".mkv",
        )

        media_info2 = MediaInfo(
            original_path=file_path,
            media_type=MediaType.MOVIE,
            title="Test Movie",
            year=2020,
            extension=".mkv",
        )

        media_info3 = MediaInfo(
            original_path=file_path,
            media_type=MediaType.MOVIE,
            title="Different Movie",
            year=2020,
            extension=".mkv",
        )

        assert media_info1 == media_info2
        assert media_info1 != media_info3

    def test_media_info_serialization(self, temp_dir):
        """Test MediaInfo serialization"""
        file_path = temp_dir / "test.mkv"
        file_path.touch()

        media_info = MediaInfo(
            original_path=file_path,
            media_type=MediaType.MOVIE,
            title="Test Movie",
            year=2020,
            extension=".mkv",
            tmdb_id=12345,
        )

        # Test model dump
        data = media_info.model_dump()
        assert isinstance(data, dict)
        assert data["title"] == "Test Movie"
        assert data["year"] == 2020
        assert data["media_type"] == MediaType.MOVIE
        assert data["tmdb_id"] == "12345"

        # Test model validation
        new_media_info = MediaInfo.model_validate(data)
        assert new_media_info.title == media_info.title
        assert new_media_info.year == media_info.year
        assert new_media_info.media_type == media_info.media_type


class TestRenameResult:
    """Test cases for RenameResult model"""

    def test_successful_rename_result(self, temp_dir):
        """Test successful rename result"""
        original_path = temp_dir / "original.mkv"
        new_path = temp_dir / "new.mkv"

        result = RenameResult(
            original_path=original_path, new_path=new_path, success=True, error=None
        )

        assert result.original_path == original_path
        assert result.new_path == new_path
        assert result.success is True
        assert result.error is None

    def test_failed_rename_result(self, temp_dir):
        """Test failed rename result"""
        original_path = temp_dir / "original.mkv"
        error_message = "File already exists"

        result = RenameResult(
            original_path=original_path,
            new_path=original_path,
            success=False,
            error=error_message,
        )

        assert result.original_path == original_path
        assert result.new_path == original_path
        assert result.success is False
        assert result.error == error_message

    def test_rename_result_with_different_paths(self, temp_dir):
        """Test rename result with different original and new paths"""
        original_path = temp_dir / "Movie.2020.mkv"
        new_path = temp_dir / "Movie (2020).mkv"

        result = RenameResult(
            original_path=original_path, new_path=new_path, success=True
        )

        assert result.original_path == original_path
        assert result.new_path == new_path
        assert result.success is True
        assert result.error is None

    def test_rename_result_validation(self, temp_dir):
        """Test RenameResult validation"""
        original_path = temp_dir / "test.mkv"
        new_path = temp_dir / "new.mkv"

        # Valid result
        result = RenameResult(
            original_path=original_path, new_path=new_path, success=True
        )

        assert result.success is True

        # Test with invalid success value
        with pytest.raises(ValueError):
            RenameResult(
                original_path=original_path,
                new_path=new_path,
                success="invalid_boolean",
            )

    def test_rename_result_equality(self, temp_dir):
        """Test RenameResult equality"""
        original_path = temp_dir / "test.mkv"
        new_path = temp_dir / "new.mkv"

        result1 = RenameResult(
            original_path=original_path, new_path=new_path, success=True, error=None
        )

        result2 = RenameResult(
            original_path=original_path, new_path=new_path, success=True, error=None
        )

        result3 = RenameResult(
            original_path=original_path,
            new_path=new_path,
            success=False,
            error="Different error",
        )

        assert result1 == result2
        assert result1 != result3

    def test_rename_result_serialization(self, temp_dir):
        """Test RenameResult serialization"""
        original_path = temp_dir / "test.mkv"
        new_path = temp_dir / "new.mkv"

        result = RenameResult(
            original_path=original_path, new_path=new_path, success=True, error=None
        )

        # Test model dump
        data = result.model_dump()
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["error"] is None

        # Test model validation
        new_result = RenameResult.model_validate(data)
        assert new_result.success == result.success
        assert new_result.error == result.error

    def test_rename_result_with_long_error_message(self, temp_dir):
        """Test RenameResult with long error message"""
        original_path = temp_dir / "test.mkv"
        long_error = "This is a very long error message that describes in detail what went wrong during the file renaming process including specific details about the failure mode and potential solutions."

        result = RenameResult(
            original_path=original_path,
            new_path=original_path,
            success=False,
            error=long_error,
        )

        assert result.error == long_error
        assert result.success is False

    def test_rename_result_default_values(self, temp_dir):
        """Test RenameResult default values"""
        original_path = temp_dir / "test.mkv"
        new_path = temp_dir / "new.mkv"

        result = RenameResult(
            original_path=original_path, new_path=new_path, success=True
        )

        # error should default to None
        assert result.error is None
        assert result.success is True

    def test_rename_result_string_representation(self, temp_dir):
        """Test RenameResult string representation"""
        original_path = temp_dir / "test.mkv"
        new_path = temp_dir / "new.mkv"

        result = RenameResult(
            original_path=original_path, new_path=new_path, success=True, error=None
        )

        repr_str = repr(result)
        assert "RenameResult" in repr_str
        assert "success=True" in repr_str
