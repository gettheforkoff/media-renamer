from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests  # type: ignore

from media_renamer.models import MediaInfo


class BaseAPIClient(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    @abstractmethod
    def search_movie(
        self, title: str, year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def search_tv_show(
        self, title: str, season: Optional[int] = None, episode: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        pass


class TMDBClient(BaseAPIClient):
    BASE_URL = "https://api.themoviedb.org/3"

    def search_movie(
        self, title: str, year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        params = {"api_key": self.api_key, "query": title, "language": "en-US"}

        if year:
            params["year"] = str(year)

        try:
            response = self.session.get(f"{self.BASE_URL}/search/movie", params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if results:
                movie = results[0]
                return {
                    "title": movie.get("title"),
                    "year": (
                        int(movie.get("release_date", "0000")[:4])
                        if movie.get("release_date")
                        else None
                    ),
                    "tmdb_id": movie.get("id"),
                    "imdb_id": movie.get("imdb_id"),
                }
        except requests.RequestException:
            pass

        return None

    def search_tv_show(
        self, title: str, season: Optional[int] = None, episode: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        params = {"api_key": self.api_key, "query": title, "language": "en-US"}

        try:
            response = self.session.get(f"{self.BASE_URL}/search/tv", params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if results:
                show = results[0]
                result = {
                    "title": show.get("name"),
                    "year": (
                        int(show.get("first_air_date", "0000")[:4])
                        if show.get("first_air_date")
                        else None
                    ),
                    "tmdb_id": show.get("id"),
                    "season": season,
                    "episode": episode,
                }

                if season and episode:
                    episode_info = self._get_episode_info(
                        show.get("id"), season, episode
                    )
                    if episode_info:
                        result["episode_title"] = episode_info.get("name")

                return result
        except requests.RequestException:
            pass

        return None

    def _get_episode_info(
        self, series_id: int, season: int, episode: int
    ) -> Optional[Dict[str, Any]]:
        params = {"api_key": self.api_key, "language": "en-US"}

        try:
            response = self.session.get(
                f"{self.BASE_URL}/tv/{series_id}/season/{season}/episode/{episode}",
                params=params,
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            return data
        except requests.RequestException:
            return None


class TVDBClient(BaseAPIClient):
    BASE_URL = "https://api4.thetvdb.com/v4"

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.token = None
        self._authenticate()

    def _authenticate(self) -> None:
        try:
            response = self.session.post(
                f"{self.BASE_URL}/login", json={"apikey": self.api_key}
            )
            response.raise_for_status()
            self.token = response.json().get("data", {}).get("token")

            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})  # type: ignore
        except requests.RequestException:
            pass

    def search_movie(
        self, title: str, year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        params = {"query": title, "type": "movie"}

        try:
            response = self.session.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get("data", [])

            for result in results:
                movie = result.get("movie")
                if movie:
                    movie_year = None
                    if movie.get("year"):
                        movie_year = int(movie.get("year"))

                    if not year or movie_year == year:
                        return {
                            "title": movie.get("name"),
                            "year": movie_year,
                            "tvdb_id": movie.get("id"),
                        }
        except requests.RequestException:
            pass

        return None

    def search_tv_show(
        self, title: str, season: Optional[int] = None, episode: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        params = {"query": title, "type": "series"}

        try:
            response = self.session.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get("data", [])

            for result in results:
                series = result.get("series")
                if series:
                    result_data = {
                        "title": series.get("name"),
                        "year": int(series.get("year")) if series.get("year") else None,
                        "tvdb_id": series.get("id"),
                        "season": season,
                        "episode": episode,
                    }

                    if season and episode:
                        episode_info = self._get_episode_info(
                            series.get("id"), season, episode
                        )
                        if episode_info:
                            result_data["episode_title"] = episode_info.get("name")

                    return result_data
        except requests.RequestException:
            pass

        return None

    def _get_episode_info(
        self, series_id: int, season: int, episode: int
    ) -> Optional[Dict[str, Any]]:
        params = {"season": season, "episode": episode}

        try:
            response = self.session.get(
                f"{self.BASE_URL}/series/{series_id}/episodes", params=params
            )
            response.raise_for_status()

            data = response.json()
            episodes = data.get("data", {}).get("episodes", [])

            for ep in episodes:
                if ep.get("seasonNumber") == season and ep.get("number") == episode:
                    return ep  # type: ignore
        except requests.RequestException:
            pass

        return None


class APIClientManager:
    def __init__(self, tmdb_key: Optional[str] = None, tvdb_key: Optional[str] = None):
        self.tmdb = TMDBClient(tmdb_key) if tmdb_key else None
        self.tvdb = TVDBClient(tvdb_key) if tvdb_key else None

    def enhance_media_info(self, media_info: MediaInfo) -> MediaInfo:
        if media_info.is_movie:
            return self._enhance_movie_info(media_info)
        elif media_info.is_tv_show:
            return self._enhance_tv_info(media_info)

        return media_info

    def _enhance_movie_info(self, media_info: MediaInfo) -> MediaInfo:
        for client in [self.tmdb, self.tvdb]:
            if client:
                result = client.search_movie(media_info.title, media_info.year)
                if result:
                    media_info.title = result.get("title", media_info.title)
                    media_info.year = result.get("year", media_info.year)
                    media_info.tmdb_id = result.get("tmdb_id", media_info.tmdb_id)
                    media_info.tvdb_id = result.get("tvdb_id", media_info.tvdb_id)
                    media_info.imdb_id = result.get("imdb_id", media_info.imdb_id)
                    break

        return media_info

    def _enhance_tv_info(self, media_info: MediaInfo) -> MediaInfo:
        for client in [self.tvdb, self.tmdb]:
            if client:
                result = client.search_tv_show(
                    media_info.title, media_info.season, media_info.episode
                )
                if result:
                    media_info.title = result.get("title", media_info.title)
                    media_info.year = result.get("year", media_info.year)
                    media_info.episode_title = result.get(
                        "episode_title", media_info.episode_title
                    )
                    media_info.tmdb_id = result.get("tmdb_id", media_info.tmdb_id)
                    media_info.tvdb_id = result.get("tvdb_id", media_info.tvdb_id)
                    break

        return media_info
