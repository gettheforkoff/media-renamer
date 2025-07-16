import re
from pathlib import Path
from typing import Optional

import guessit
from pymediainfo import MediaInfo as PyMediaInfo

from media_renamer.models import MediaInfo, MediaType
from media_renamer.quality_extractor import QualityExtractor


class MetadataExtractor:
    def __init__(self) -> None:
        self.season_episode_patterns = [
            r"[Ss](\d+)[Ee](\d+)",
            r"Season[\s\.]*(\d+).*Episode[\s\.]*(\d+)",
            r"(\d+)x(\d+)",
        ]
        self.year_pattern = r"\b(19|20)\d{2}\b"
        self.quality_extractor = QualityExtractor()

    def extract_from_filename(self, file_path: Path) -> MediaInfo:
        filename = file_path.stem
        extension = file_path.suffix.lower()

        guess = guessit.guessit(filename)

        media_type = MediaType.UNKNOWN
        if guess.get("type") == "movie":
            media_type = MediaType.MOVIE
        elif guess.get("type") == "episode":
            media_type = MediaType.TV_SHOW
        else:
            media_type = self._guess_media_type(filename)

        title = guess.get("title", filename)
        year = guess.get("year")
        season = guess.get("season")
        episode = guess.get("episode")
        episode_title = guess.get("episode_title")

        if media_type == MediaType.UNKNOWN:
            if season is not None and episode is not None:
                media_type = MediaType.TV_SHOW
            elif year is not None:
                media_type = MediaType.MOVIE

        # Extract quality information
        quality_info = self.quality_extractor.extract_quality_info(file_path)

        return MediaInfo(
            original_path=file_path,
            media_type=media_type,
            title=title,
            year=year,
            season=season,
            episode=episode,
            episode_title=episode_title,
            extension=extension,
            quality_info=quality_info,
        )

    def extract_from_mediainfo(self, file_path: Path) -> Optional[dict]:
        try:
            media_info = PyMediaInfo.parse(str(file_path))

            metadata = {}
            for track in media_info.tracks:
                if track.track_type == "General":
                    if hasattr(track, "title") and track.title:
                        metadata["title"] = track.title
                    if hasattr(track, "recorded_date") and track.recorded_date:
                        metadata["year"] = int(track.recorded_date[:4])
                    if hasattr(track, "season") and track.season:
                        metadata["season"] = int(track.season)
                    if hasattr(track, "episode") and track.episode:
                        metadata["episode"] = int(track.episode)

            return metadata
        except Exception:
            return None

    def _guess_media_type(self, filename: str) -> MediaType:
        for pattern in self.season_episode_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return MediaType.TV_SHOW

        if re.search(self.year_pattern, filename):
            return MediaType.MOVIE

        return MediaType.UNKNOWN
