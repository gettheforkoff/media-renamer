from enum import Enum
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, field_validator


class MediaType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value


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

    @field_validator("tmdb_id", "tvdb_id", mode="before")
    @classmethod
    def validate_ids(cls, v: Union[str, int, None]) -> Optional[str]:
        if v is None:
            return None
        return str(v)

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
