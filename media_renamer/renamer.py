import logging
import re
import shutil
from pathlib import Path
from typing import List, Optional

from media_renamer.config import Config
from media_renamer.models import MediaInfo, RenameResult
from media_renamer.quality_extractor import QualityExtractor


class FileRenamer:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.quality_extractor = QualityExtractor()

    def rename_file(self, media_info: MediaInfo) -> RenameResult:
        try:
            new_filename = self._generate_filename(media_info)
            if not new_filename:
                return RenameResult(
                    original_path=media_info.original_path,
                    new_path=media_info.original_path,
                    success=False,
                    error="Could not generate filename",
                )

            new_path = media_info.original_path.parent / new_filename

            if media_info.original_path == new_path:
                return RenameResult(
                    original_path=media_info.original_path,
                    new_path=new_path,
                    success=True,
                    error=None,
                )

            if self.config.dry_run:
                self.logger.info(
                    f"DRY RUN: Would rename {media_info.original_path} -> {new_path}"
                )
                return RenameResult(
                    original_path=media_info.original_path,
                    new_path=new_path,
                    success=True,
                    error=None,
                )

            if new_path.exists():
                return RenameResult(
                    original_path=media_info.original_path,
                    new_path=new_path,
                    success=False,
                    error=f"Target file already exists: {new_path}",
                )

            shutil.move(str(media_info.original_path), str(new_path))

            return RenameResult(
                original_path=media_info.original_path,
                new_path=new_path,
                success=True,
                error=None,
            )

        except Exception as e:
            return RenameResult(
                original_path=media_info.original_path,
                new_path=media_info.original_path,
                success=False,
                error=str(e),
            )

    def _generate_filename(self, media_info: MediaInfo) -> Optional[str]:
        if media_info.is_movie:
            return self._generate_movie_filename(media_info)
        elif media_info.is_tv_show:
            return self._generate_tv_filename(media_info)

        return None

    def _generate_movie_filename(self, media_info: MediaInfo) -> str:
        pattern = self.config.movie_pattern

        title = self._sanitize_filename(media_info.title)
        year = media_info.year or ""

        filename = pattern.format(title=title, year=year)

        return f"{filename}{media_info.extension}"

    def _generate_tv_filename(self, media_info: MediaInfo) -> str:
        pattern = self.config.tv_pattern

        title = self._sanitize_filename(media_info.title)
        year = media_info.year or ""
        season = media_info.season or 1
        episode = media_info.episode or 1
        episode_title = self._sanitize_filename(media_info.episode_title or "")

        # Generate quality string
        quality_string = ""
        if media_info.quality_info:
            quality_string = self.quality_extractor.format_quality_string(
                media_info.quality_info
            )

        filename = pattern.format(
            title=title,
            year=year,
            season=season,
            episode=episode,
            episode_title=episode_title,
            quality_string=quality_string,
        )

        return f"{filename}{media_info.extension}"

    def _sanitize_filename(self, filename: str) -> str:
        if not filename:
            return ""

        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, "", filename)

        sanitized = re.sub(r"\s+", " ", sanitized)

        sanitized = sanitized.strip()

        return sanitized

    def process_directory(self, directory: Path) -> List[RenameResult]:
        results: List[RenameResult] = []

        if not directory.exists() or not directory.is_dir():
            return results

        for file_path in directory.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.config.supported_extensions
            ):
                from media_renamer.api_clients import APIClientManager
                from media_renamer.metadata_extractor import MetadataExtractor

                extractor = MetadataExtractor()
                api_manager = APIClientManager(
                    tmdb_key=self.config.tmdb_api_key, tvdb_key=self.config.tvdb_api_key
                )

                media_info = extractor.extract_from_filename(file_path)

                media_info = api_manager.enhance_media_info(media_info)

                result = self.rename_file(media_info)
                results.append(result)

                if self.config.verbose:
                    if result.success:
                        self.logger.info(
                            f"Renamed: {result.original_path} -> {result.new_path}"
                        )
                    else:
                        self.logger.error(
                            f"Failed to rename {result.original_path}: {result.error}"
                        )

        return results
