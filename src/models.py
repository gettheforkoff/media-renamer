from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from enum import Enum


class MediaType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    UNKNOWN = "unknown"


class MediaInfo(BaseModel):
    original_path: Path
    media_type: MediaType
    title: str
    year: Optional[int] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    episode_title: Optional[str] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None
    tvdb_id: Optional[str] = None
    extension: str
    
    @property
    def is_movie(self) -> bool:
        return self.media_type == MediaType.MOVIE
    
    @property
    def is_tv_show(self) -> bool:
        return self.media_type == MediaType.TV_SHOW


class RenameResult(BaseModel):
    original_path: Path
    new_path: Path
    success: bool
    error: Optional[str] = None