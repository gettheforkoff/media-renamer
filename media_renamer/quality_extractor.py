import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

try:
    from pymediainfo import MediaInfo

    PYMEDIAINFO_AVAILABLE = True
except ImportError:
    PYMEDIAINFO_AVAILABLE = False


@dataclass
class QualityInfo:
    """Information about media quality, codecs, and source"""

    # Video info
    resolution: Optional[str] = None  # "1080p", "720p", "480p", "4K"
    video_codec: Optional[str] = None  # "h264", "h265", "x264", "x265"

    # Audio info
    audio_codec: Optional[str] = None  # "EAC3", "DTS", "AAC", "AC3"
    audio_channels: Optional[str] = None  # "2.0", "5.1", "7.1"

    # Source/Quality
    source: Optional[str] = None  # "WEBDL", "BluRay", "HDTV", "DVD"
    quality_tags: Optional[List[str]] = None  # ["Proper", "REPACK", etc.]

    # Release info
    release_group: Optional[str] = None  # "Kitsune", "AMZN", etc.

    def __post_init__(self) -> None:
        if self.quality_tags is None:
            self.quality_tags = []


class QualityExtractor:
    """Extract quality information from filenames and media files"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        # Resolution patterns
        self.resolution_patterns = [
            r"\b(2160p|4K)\b",
            r"\b(1080p)\b",
            r"\b(720p)\b",
            r"\b(480p)\b",
            r"\b(360p)\b",
        ]

        # Video codec patterns
        self.video_codec_patterns = [
            r"\b(h264|x264|AVC)\b",
            r"\b(h265|x265|HEVC)\b",
            r"\b(XviD)\b",
            r"\b(DivX)\b",
        ]

        # Audio codec patterns
        self.audio_codec_patterns = [
            r"\b(DTS-HD|DTS-X|DTS)\b",
            r"\b(TrueHD|Atmos)\b",
            r"\b(EAC3|E-AC-3)\b",
            r"\b(AC3|AC-3)\b",
            r"\b(AAC)\b",
            r"\b(MP3)\b",
            r"\b(FLAC)\b",
            r"(DDP)",  # Dolby Digital Plus
            r"(DD)(?![0-9])",  # Dolby Digital (but not DD5.1)
        ]

        # Audio channel patterns
        self.audio_channel_patterns = [
            r"\b(7\.1|7\.0)\b",
            r"\b(5\.1|5\.0)\b",
            r"\b(2\.1|2\.0)\b",
            r"\b(Stereo)\b",
            r"\b(Mono)\b",
            r"DDP(5\.1|7\.1|2\.0)",  # DDP5.1, DDP7.1, etc.
            r"DD(5\.1|7\.1|2\.0)",  # DD5.1, DD7.1, etc.
        ]

        # Source patterns
        self.source_patterns = [
            r"\b(WEBDL|WEB-DL|WEB\.DL)\b",
            r"\b(WEBRip|WEB-Rip|WEB\.Rip)\b",
            r"\b(WEB)\b",  # Generic WEB source
            r"\b(BluRay|Blu-Ray|BDRip|BD)\b",
            r"\b(HDTV|HDTVRip)\b",
            r"\b(DVDRip|DVD)\b",
            r"\b(CAM|TS|TC)\b",
            r"\b(HDRIP)\b",
        ]

        # Quality tag patterns
        self.quality_tag_patterns = [
            r"\b(Proper|PROPER)\b",
            r"\b(Repack|REPACK)\b",
            r"\b(Extended|EXTENDED)\b",
            r"\b(Director\'?s?\.?Cut|DIRECTORS?\.?CUT)\b",
            r"\b(Uncut|UNCUT)\b",
            r"\b(Internal|INTERNAL)\b",
            r"\b(HDR|HDR10|DV|Dolby\.?Vision)\b",
            r"\b(Atmos)\b",
            r"\b(IMAX)\b",
        ]

        # Release group patterns (typically at the end)
        self.release_group_patterns = [
            r"-([A-Za-z0-9]+)(?:\.[a-z0-9]+)?$",  # -GroupName.ext
            r"\[([A-Za-z][A-Za-z0-9]*)\](?!\s*(?:1080p|720p|480p|4K|WEBDL|BluRay|HDTV|h264|h265|DTS|EAC3|AC3|\d+\.\d+))",  # [GroupName] but not quality tags
        ]

        # Platform/Network patterns
        self.platform_patterns = [
            r"\b(AMZN|Amazon)\b",
            r"\b(NF|Netflix)\b",
            r"\b(HULU)\b",
            r"\b(HBO|Max)\b",
            r"\b(DSNP|Disney)\b",
            r"\b(ATVP|AppleTV)\b",
        ]

    def extract_from_filename(self, file_path: Path) -> QualityInfo:
        """Extract quality information from filename using regex patterns"""
        filename = file_path.name
        self.logger.debug(f"Extracting quality info from: {filename}")

        quality_info = QualityInfo()

        # Extract resolution
        quality_info.resolution = self._extract_pattern(
            filename, self.resolution_patterns
        )

        # Extract video codec
        quality_info.video_codec = self._extract_pattern(
            filename, self.video_codec_patterns
        )
        if quality_info.video_codec:
            quality_info.video_codec = self._normalize_video_codec(
                quality_info.video_codec
            )

        # Extract audio codec
        quality_info.audio_codec = self._extract_pattern(
            filename, self.audio_codec_patterns
        )

        # Extract audio channels
        quality_info.audio_channels = self._extract_pattern(
            filename, self.audio_channel_patterns
        )

        # Extract source
        quality_info.source = self._extract_pattern(filename, self.source_patterns)
        if quality_info.source:
            quality_info.source = self._normalize_source(quality_info.source)

        # Extract quality tags
        quality_info.quality_tags = self._extract_all_patterns(
            filename, self.quality_tag_patterns
        )

        # Extract release group
        quality_info.release_group = self._extract_pattern(
            filename, self.release_group_patterns
        )

        # Check for platform info and merge with source
        platform = self._extract_pattern(filename, self.platform_patterns)
        if platform and quality_info.source:
            quality_info.source = f"{platform} {quality_info.source}"
        elif platform:
            quality_info.source = platform

        self.logger.debug(f"Extracted quality info: {quality_info}")
        return quality_info

    def extract_from_mediainfo(self, file_path: Path) -> QualityInfo:
        """Extract quality information using PyMediaInfo (fallback method)"""
        if not PYMEDIAINFO_AVAILABLE:
            self.logger.warning(
                "PyMediaInfo not available, cannot analyze file directly"
            )
            return QualityInfo()

        if not file_path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return QualityInfo()

        try:
            media_info = MediaInfo.parse(str(file_path))
            quality_info = QualityInfo()

            # Get video track info
            for track in media_info.tracks:
                if track.track_type == "Video":
                    # Resolution
                    if track.height:
                        if track.height >= 2160:
                            quality_info.resolution = "4K"
                        elif track.height >= 1080:
                            quality_info.resolution = "1080p"
                        elif track.height >= 720:
                            quality_info.resolution = "720p"
                        elif track.height >= 480:
                            quality_info.resolution = "480p"

                    # Video codec
                    if track.codec:
                        quality_info.video_codec = self._normalize_video_codec(
                            track.codec
                        )

                elif track.track_type == "Audio":
                    # Audio codec (use first audio track)
                    if track.codec and not quality_info.audio_codec:
                        quality_info.audio_codec = track.codec

                    # Audio channels
                    if track.channel_s and not quality_info.audio_channels:
                        channels = track.channel_s
                        if channels == 8:
                            quality_info.audio_channels = "7.1"
                        elif channels == 6:
                            quality_info.audio_channels = "5.1"
                        elif channels == 2:
                            quality_info.audio_channels = "2.0"
                        elif channels == 1:
                            quality_info.audio_channels = "Mono"

            self.logger.debug(f"MediaInfo extracted quality info: {quality_info}")
            return quality_info

        except Exception as e:
            self.logger.error(f"Error analyzing file with MediaInfo: {e}")
            return QualityInfo()

    def extract_quality_info(self, file_path: Path) -> QualityInfo:
        """Hybrid approach: try filename parsing first, fallback to MediaInfo"""
        # Try filename parsing first
        filename_info = self.extract_from_filename(file_path)

        # If we got most info from filename, return it
        if self._is_quality_info_complete(filename_info):
            return filename_info

        # Otherwise, try MediaInfo and merge results
        mediainfo_info = self.extract_from_mediainfo(file_path)

        # Merge the two results, preferring filename info when available
        merged_info = QualityInfo(
            resolution=filename_info.resolution or mediainfo_info.resolution,
            video_codec=filename_info.video_codec or mediainfo_info.video_codec,
            audio_codec=filename_info.audio_codec or mediainfo_info.audio_codec,
            audio_channels=filename_info.audio_channels
            or mediainfo_info.audio_channels,
            source=filename_info.source or mediainfo_info.source,
            quality_tags=filename_info.quality_tags or mediainfo_info.quality_tags,
            release_group=filename_info.release_group or mediainfo_info.release_group,
        )

        return merged_info

    def _extract_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract first matching pattern from text"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return None

    def _extract_all_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Extract all matching patterns from text"""
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            results.extend(matches)
        return results

    def _normalize_video_codec(self, codec: str) -> str:
        """Normalize video codec names"""
        codec_lower = codec.lower()
        if codec_lower in ["h264", "x264", "avc"]:
            return "h264"
        elif codec_lower in ["h265", "x265", "hevc"]:
            return "h265"
        return codec

    def _normalize_source(self, source: str) -> str:
        """Normalize source names"""
        source_lower = source.lower()
        if "webdl" in source_lower or "web-dl" in source_lower:
            return "WEBDL"
        elif "webrip" in source_lower:
            return "WEBRip"
        elif "bluray" in source_lower or "blu-ray" in source_lower:
            return "BluRay"
        elif "hdtv" in source_lower:
            return "HDTV"
        elif "dvd" in source_lower:
            return "DVD"
        return source.upper()

    def _is_quality_info_complete(self, quality_info: QualityInfo) -> bool:
        """Check if quality info has most essential information"""
        essential_fields = [
            quality_info.resolution,
            quality_info.video_codec,
            quality_info.source,
        ]
        return sum(1 for field in essential_fields if field) >= 2

    def format_quality_string(self, quality_info: QualityInfo) -> str:
        """Format quality info into a string for filename"""
        parts = []

        # Source and resolution
        if quality_info.source and quality_info.resolution:
            source_part = f"{quality_info.source}-{quality_info.resolution}"
            if quality_info.quality_tags:
                source_part += f" {' '.join(quality_info.quality_tags)}"
            parts.append(f"[{source_part}]")
        elif quality_info.source:
            parts.append(f"[{quality_info.source}]")
        elif quality_info.resolution:
            parts.append(f"[{quality_info.resolution}]")

        # Audio info (avoid duplicating Atmos if it's also in quality_tags)
        if quality_info.audio_codec and quality_info.audio_channels:
            audio_part = f"{quality_info.audio_codec} {quality_info.audio_channels}"
            # Don't add Atmos separately if it's already in quality tags
            if (
                quality_info.audio_codec.lower() == "atmos"
                and quality_info.quality_tags
                and any(tag.lower() == "atmos" for tag in quality_info.quality_tags)
            ):
                # Use just the channels if Atmos is already in quality tags
                if quality_info.audio_channels:
                    parts.append(f"[{quality_info.audio_channels}]")
            else:
                parts.append(f"[{audio_part}]")
        elif quality_info.audio_codec and quality_info.audio_codec.lower() != "atmos":
            parts.append(f"[{quality_info.audio_codec}]")
        elif quality_info.audio_codec == "Atmos" and (
            not quality_info.quality_tags
            or not any(tag.lower() == "atmos" for tag in quality_info.quality_tags)
        ):
            parts.append(f"[{quality_info.audio_codec}]")

        # Video codec
        if quality_info.video_codec:
            parts.append(f"[{quality_info.video_codec}]")

        # Release group
        if quality_info.release_group:
            parts.append(f"-{quality_info.release_group}")

        return "".join(parts)
