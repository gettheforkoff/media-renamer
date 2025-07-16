from unittest.mock import Mock, patch

import requests

from media_renamer.api_clients import APIClientManager, TMDBClient, TVDBClient
from media_renamer.models import MediaInfo, MediaType
from tests.fixtures.sample_responses import (
    TMDB_EPISODE_RESPONSE,
    TMDB_MOVIE_RESPONSE,
    TMDB_TV_RESPONSE,
)


class TestTMDBClient:
    """Test cases for TMDBClient"""

    def setup_method(self):
        """Setup test fixtures"""
        self.client = TMDBClient("test_api_key")

    @patch("requests.Session.get")
    def test_search_movie_success(self, mock_get):
        """Test successful movie search"""
        mock_response = Mock()
        mock_response.json.return_value = TMDB_MOVIE_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_movie("The Matrix", 1999)

        assert result is not None
        assert result["title"] == "The Matrix"
        assert result["year"] == 1999
        assert result["tmdb_id"] == 603

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/search/movie" in args[0]
        assert kwargs["params"]["query"] == "The Matrix"
        assert kwargs["params"]["year"] == "1999"

    @patch("requests.Session.get")
    def test_search_movie_without_year(self, mock_get):
        """Test movie search without year"""
        mock_response = Mock()
        mock_response.json.return_value = TMDB_MOVIE_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_movie("The Matrix")

        assert result is not None
        assert result["title"] == "The Matrix"

        args, kwargs = mock_get.call_args
        assert "year" not in kwargs["params"]

    @patch("requests.Session.get")
    def test_search_movie_no_results(self, mock_get):
        """Test movie search with no results"""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_movie("Nonexistent Movie")

        assert result is None

    @patch("requests.Session.get")
    def test_search_movie_request_exception(self, mock_get):
        """Test movie search with request exception"""
        mock_get.side_effect = requests.RequestException("Network error")

        result = self.client.search_movie("The Matrix")

        assert result is None

    @patch("requests.Session.get")
    def test_search_movie_http_error(self, mock_get):
        """Test movie search with HTTP error"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = self.client.search_movie("The Matrix")

        assert result is None

    @patch("requests.Session.get")
    def test_search_tv_show_success(self, mock_get):
        """Test successful TV show search"""
        mock_response = Mock()
        mock_response.json.return_value = TMDB_TV_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_tv_show("Breaking Bad")

        assert result is not None
        assert result["title"] == "Breaking Bad"
        assert result["year"] == 2008
        assert result["tmdb_id"] == 1396

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/search/tv" in args[0]
        assert kwargs["params"]["query"] == "Breaking Bad"

    @patch("requests.Session.get")
    def test_search_tv_show_with_episode_info(self, mock_get):
        """Test TV show search with episode information"""
        # First call returns TV show search results
        tv_response = Mock()
        tv_response.json.return_value = TMDB_TV_RESPONSE
        tv_response.raise_for_status.return_value = None

        # Second call returns episode information
        episode_response = Mock()
        episode_response.json.return_value = TMDB_EPISODE_RESPONSE
        episode_response.raise_for_status.return_value = None

        mock_get.side_effect = [tv_response, episode_response]

        result = self.client.search_tv_show("Breaking Bad", 1, 1)

        assert result is not None
        assert result["title"] == "Breaking Bad"
        assert result["season"] == 1
        assert result["episode"] == 1
        assert result["episode_title"] == "Pilot"

        assert mock_get.call_count == 2

    @patch("requests.Session.get")
    def test_search_tv_show_episode_fetch_failure(self, mock_get):
        """Test TV show search with episode fetch failure"""
        # First call returns TV show search results
        tv_response = Mock()
        tv_response.json.return_value = TMDB_TV_RESPONSE
        tv_response.raise_for_status.return_value = None

        # Second call fails
        mock_get.side_effect = [
            tv_response,
            requests.RequestException("Episode fetch failed"),
        ]

        result = self.client.search_tv_show("Breaking Bad", 1, 1)

        assert result is not None
        assert result["title"] == "Breaking Bad"
        assert result["season"] == 1
        assert result["episode"] == 1
        assert "episode_title" not in result

    @patch("requests.Session.get")
    def test_get_episode_info_success(self, mock_get):
        """Test successful episode info retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = TMDB_EPISODE_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._get_episode_info(1396, 1, 1)

        assert result is not None
        assert result["name"] == "Pilot"
        assert result["episode_number"] == 1
        assert result["season_number"] == 1

        args, kwargs = mock_get.call_args
        assert "/tv/1396/season/1/episode/1" in args[0]

    @patch("requests.Session.get")
    def test_get_episode_info_failure(self, mock_get):
        """Test episode info retrieval failure"""
        mock_get.side_effect = requests.RequestException("Network error")

        result = self.client._get_episode_info(1396, 1, 1)

        assert result is None


class TestTVDBClient:
    """Test cases for TVDBClient"""

    def setup_method(self, method):
        """Setup test fixtures"""
        # Mock authentication
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"data": {"token": "test_token"}}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            self.client = TVDBClient("test_api_key")

    @patch("requests.Session.post")
    def test_authentication_success(self, mock_post):
        """Test successful authentication"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"token": "test_token"}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = TVDBClient("test_api_key")

        assert client.token == "test_token"
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test_token"

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "/login" in args[0]
        assert kwargs["json"]["apikey"] == "test_api_key"

    @patch("requests.Session.post")
    def test_authentication_failure(self, mock_post):
        """Test authentication failure"""
        mock_post.side_effect = requests.RequestException("Auth failed")

        client = TVDBClient("test_api_key")

        assert client.token is None
        assert "Authorization" not in client.session.headers

    @patch("requests.Session.get")
    def test_search_movie_success(self, mock_get):
        """Test successful movie search"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"movie": {"id": 12345, "name": "The Matrix", "year": "1999"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_movie("The Matrix", 1999)

        assert result is not None
        assert result["title"] == "The Matrix"
        assert result["year"] == 1999
        assert result["tvdb_id"] == 12345

        args, kwargs = mock_get.call_args
        assert "/search" in args[0]
        assert kwargs["params"]["query"] == "The Matrix"
        assert kwargs["params"]["type"] == "movie"

    @patch("requests.Session.get")
    def test_search_movie_year_mismatch(self, mock_get):
        """Test movie search with year mismatch"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "movie": {
                        "id": 12345,
                        "name": "The Matrix",
                        "year": "2000",  # Different year
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_movie("The Matrix", 1999)

        assert result is None

    @patch("requests.Session.get")
    def test_search_movie_no_year_provided(self, mock_get):
        """Test movie search without year provided"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"movie": {"id": 12345, "name": "The Matrix", "year": "1999"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_movie("The Matrix")

        assert result is not None
        assert result["title"] == "The Matrix"
        assert result["year"] == 1999

    @patch("requests.Session.get")
    def test_search_tv_show_success(self, mock_get):
        """Test successful TV show search"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"series": {"id": 81189, "name": "Breaking Bad", "year": "2008"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.search_tv_show("Breaking Bad")

        assert result is not None
        assert result["title"] == "Breaking Bad"
        assert result["year"] == 2008
        assert result["tvdb_id"] == 81189

        args, kwargs = mock_get.call_args
        assert "/search" in args[0]
        assert kwargs["params"]["query"] == "Breaking Bad"
        assert kwargs["params"]["type"] == "series"

    @patch("requests.Session.get")
    def test_search_tv_show_with_episode_info(self, mock_get):
        """Test TV show search with episode information"""
        # First call returns series search results
        series_response = Mock()
        series_response.json.return_value = {
            "data": [{"series": {"id": 81189, "name": "Breaking Bad", "year": "2008"}}]
        }
        series_response.raise_for_status.return_value = None

        # Second call returns episode information
        episode_response = Mock()
        episode_response.json.return_value = {
            "data": {
                "episodes": [
                    {"id": 349232, "name": "Pilot", "seasonNumber": 1, "number": 1}
                ]
            }
        }
        episode_response.raise_for_status.return_value = None

        mock_get.side_effect = [series_response, episode_response]

        result = self.client.search_tv_show("Breaking Bad", 1, 1)

        assert result is not None
        assert result["title"] == "Breaking Bad"
        assert result["season"] == 1
        assert result["episode"] == 1
        assert result["episode_title"] == "Pilot"

        assert mock_get.call_count == 2

    @patch("requests.Session.get")
    def test_get_episode_info_success(self, mock_get):
        """Test successful episode info retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "episodes": [
                    {"id": 349232, "name": "Pilot", "seasonNumber": 1, "number": 1}
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._get_episode_info(81189, 1, 1)

        assert result is not None
        assert result["name"] == "Pilot"
        assert result["seasonNumber"] == 1
        assert result["number"] == 1

        args, kwargs = mock_get.call_args
        assert "/series/81189/episodes" in args[0]
        assert kwargs["params"]["season"] == 1
        assert kwargs["params"]["episode"] == 1

    @patch("requests.Session.get")
    def test_get_episode_info_no_matching_episode(self, mock_get):
        """Test episode info retrieval with no matching episode"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "episodes": [
                    {
                        "id": 349232,
                        "name": "Different Episode",
                        "seasonNumber": 2,  # Different season
                        "number": 1,
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client._get_episode_info(81189, 1, 1)

        assert result is None

    @patch("requests.Session.get")
    def test_request_exception_handling(self, mock_get):
        """Test handling of request exceptions"""
        mock_get.side_effect = requests.RequestException("Network error")

        movie_result = self.client.search_movie("The Matrix")
        tv_result = self.client.search_tv_show("Breaking Bad")
        episode_result = self.client._get_episode_info(81189, 1, 1)

        assert movie_result is None
        assert tv_result is None
        assert episode_result is None


class TestAPIClientManager:
    """Test cases for APIClientManager"""

    def test_init_with_keys(self):
        """Test initialization with API keys"""
        manager = APIClientManager("tmdb_key", "tvdb_key")

        assert manager.tmdb is not None
        assert manager.tvdb is not None
        assert isinstance(manager.tmdb, TMDBClient)
        assert isinstance(manager.tvdb, TVDBClient)

    def test_init_without_keys(self):
        """Test initialization without API keys"""
        manager = APIClientManager()

        assert manager.tmdb is None
        assert manager.tvdb is None

    def test_init_with_partial_keys(self):
        """Test initialization with partial API keys"""
        manager = APIClientManager(tmdb_key="tmdb_key")

        assert manager.tmdb is not None
        assert manager.tvdb is None

    def test_enhance_movie_info_with_tmdb(self, temp_dir):
        """Test enhancing movie info with TMDB"""
        with patch("media_renamer.api_clients.TMDBClient") as mock_tmdb_class:
            mock_tmdb = Mock()
            mock_tmdb.search_movie.return_value = {
                "title": "Enhanced Movie Title",
                "year": 2020,
                "tmdb_id": 12345,
                "imdb_id": "tt1234567",
            }
            mock_tmdb_class.return_value = mock_tmdb

            manager = APIClientManager(tmdb_key="test_key")

            original_path = temp_dir / "movie.mkv"
            original_path.touch()

            media_info = MediaInfo(
                original_path=original_path,
                media_type=MediaType.MOVIE,
                title="Original Movie",
                year=2019,
                extension=".mkv",
            )

            enhanced_info = manager.enhance_media_info(media_info)

            assert enhanced_info.title == "Enhanced Movie Title"
            assert enhanced_info.year == 2020
            assert enhanced_info.tmdb_id == 12345
            assert enhanced_info.imdb_id == "tt1234567"

            mock_tmdb.search_movie.assert_called_once_with("Original Movie", 2019)

    def test_enhance_tv_info_with_tvdb(self, temp_dir):
        """Test enhancing TV info with TVDB"""
        with patch("media_renamer.api_clients.TVDBClient") as mock_tvdb_class:
            mock_tvdb = Mock()
            mock_tvdb.search_tv_show.return_value = {
                "title": "Enhanced TV Show",
                "year": 2008,
                "tvdb_id": 81189,
                "episode_title": "Enhanced Episode Title",
            }
            mock_tvdb_class.return_value = mock_tvdb

            manager = APIClientManager(tvdb_key="test_key")

            original_path = temp_dir / "show.mkv"
            original_path.touch()

            media_info = MediaInfo(
                original_path=original_path,
                media_type=MediaType.TV_SHOW,
                title="Original Show",
                season=1,
                episode=1,
                extension=".mkv",
            )

            enhanced_info = manager.enhance_media_info(media_info)

            assert enhanced_info.title == "Enhanced TV Show"
            assert enhanced_info.year == 2008
            assert enhanced_info.tvdb_id == 81189
            assert enhanced_info.episode_title == "Enhanced Episode Title"

            mock_tvdb.search_tv_show.assert_called_once_with("Original Show", 1, 1)

    def test_enhance_info_fallback_order(self, temp_dir):
        """Test fallback order for API clients"""
        with (
            patch("media_renamer.api_clients.TMDBClient") as mock_tmdb_class,
            patch("media_renamer.api_clients.TVDBClient") as mock_tvdb_class
        ):
            # TMDB fails, TVDB succeeds
            mock_tmdb = Mock()
            mock_tmdb.search_movie.return_value = None
            mock_tmdb_class.return_value = mock_tmdb

            mock_tvdb = Mock()
            mock_tvdb.search_movie.return_value = {
                "title": "TVDB Movie Title",
                "year": 2020,
                "tvdb_id": 12345,
            }
            mock_tvdb_class.return_value = mock_tvdb

            manager = APIClientManager(tmdb_key="tmdb_key", tvdb_key="tvdb_key")

            original_path = temp_dir / "movie.mkv"
            original_path.touch()

            media_info = MediaInfo(
                original_path=original_path,
                media_type=MediaType.MOVIE,
                title="Original Movie",
                year=2019,
                extension=".mkv",
            )

            enhanced_info = manager.enhance_media_info(media_info)

            assert enhanced_info.title == "TVDB Movie Title"
            assert enhanced_info.tvdb_id == 12345

            # Both clients should be tried
            mock_tmdb.search_movie.assert_called_once()
            mock_tvdb.search_movie.assert_called_once()

    def test_enhance_info_no_api_results(self, temp_dir):
        """Test enhancing info when no API results are found"""
        with patch("media_renamer.api_clients.TMDBClient") as mock_tmdb_class:
            mock_tmdb = Mock()
            mock_tmdb.search_movie.return_value = None
            mock_tmdb_class.return_value = mock_tmdb

            manager = APIClientManager(tmdb_key="test_key")

            original_path = temp_dir / "movie.mkv"
            original_path.touch()

            media_info = MediaInfo(
                original_path=original_path,
                media_type=MediaType.MOVIE,
                title="Unknown Movie",
                year=2019,
                extension=".mkv",
            )

            enhanced_info = manager.enhance_media_info(media_info)

            # Should return original info unchanged
            assert enhanced_info.title == "Unknown Movie"
            assert enhanced_info.year == 2019
            assert enhanced_info.tmdb_id is None

    def test_enhance_unknown_media_type(self, temp_dir):
        """Test enhancing unknown media type"""
        manager = APIClientManager(tmdb_key="test_key")

        original_path = temp_dir / "unknown.mkv"
        original_path.touch()

        media_info = MediaInfo(
            original_path=original_path,
            media_type=MediaType.UNKNOWN,
            title="Unknown File",
            extension=".mkv",
        )

        enhanced_info = manager.enhance_media_info(media_info)

        # Should return original info unchanged
        assert enhanced_info == media_info

    def test_enhance_info_without_clients(self, temp_dir):
        """Test enhancing info without any API clients"""
        manager = APIClientManager()  # No API keys

        original_path = temp_dir / "movie.mkv"
        original_path.touch()

        media_info = MediaInfo(
            original_path=original_path,
            media_type=MediaType.MOVIE,
            title="Test Movie",
            year=2020,
            extension=".mkv",
        )

        enhanced_info = manager.enhance_media_info(media_info)

        # Should return original info unchanged
        assert enhanced_info == media_info
