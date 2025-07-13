import os
from typing import List, Optional

from pydantic import BaseModel


class Config(BaseModel):
    tvdb_api_key: Optional[str] = None
    tmdb_api_key: Optional[str] = None
    imdb_api_key: Optional[str] = None

    movie_pattern: str = "{title} ({year})"
    tv_pattern: str = "{title} - S{season:02d}E{episode:02d} - {episode_title}"

    dry_run: bool = False
    verbose: bool = False

    supported_extensions: List[str] = [
        ".mkv",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
    ]

    @classmethod
    def load_from_env(cls) -> "Config":
        return cls(
            tvdb_api_key=os.getenv("TVDB_API_KEY"),
            tmdb_api_key=os.getenv("TMDB_API_KEY"),
            imdb_api_key=os.getenv("IMDB_API_KEY"),
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
            verbose=os.getenv("VERBOSE", "false").lower() == "true",
        )
