from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from media_renamer.quality_extractor import QualityExtractor, QualityInfo


class TestQualityExtractor:

    @pytest.fixture
    def extractor(self):
        return QualityExtractor()

    def test_extract_supernatural_example(self, extractor):
        """Test extraction from Supernatural filename example"""
        filename = Path(
            "Supernatural (2005) - S01E01 - Pilot [AMZN WEBDL-1080p Proper][EAC3 2.0][h264]-Kitsune.mkv"
        )

        quality_info = extractor.extract_from_filename(filename)

        assert quality_info.resolution == "1080p"
        assert quality_info.video_codec == "h264"
        assert quality_info.audio_codec == "EAC3"
        assert quality_info.audio_channels == "2.0"
        assert quality_info.source == "AMZN WEBDL"
        assert "Proper" in quality_info.quality_tags
        assert quality_info.release_group == "Kitsune"

    def test_extract_resolution_patterns(self, extractor):
        """Test resolution extraction patterns"""
        test_cases = [
            ("Movie.2020.1080p.BluRay.x264.mkv", "1080p"),
            ("Show.S01E01.720p.HDTV.x265.mp4", "720p"),
            ("Film.2019.4K.UHD.HDR.mkv", "4K"),
            ("Episode.480p.WEB.h264.avi", "480p"),
            ("Movie.2160p.UHD.mkv", "2160p"),
        ]

        for filename, expected_resolution in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            assert quality_info.resolution == expected_resolution

    def test_extract_video_codec_patterns(self, extractor):
        """Test video codec extraction patterns"""
        test_cases = [
            ("Movie.2020.1080p.BluRay.x264.mkv", "h264"),
            ("Show.S01E01.720p.HDTV.h265.mp4", "h265"),
            ("Film.2019.x265.HDR.mkv", "h265"),
            ("Episode.h264.WEB.avi", "h264"),
            ("Movie.XviD.DVDRip.avi", "XviD"),
        ]

        for filename, expected_codec in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            assert quality_info.video_codec == expected_codec

    def test_extract_audio_patterns(self, extractor):
        """Test audio codec and channel extraction"""
        test_cases = [
            ("Movie.2020.DTS.5.1.mkv", "DTS", "5.1"),
            ("Show.AC3.2.0.mp4", "AC3", "2.0"),
            ("Film.EAC3.7.1.mkv", "EAC3", "7.1"),
            ("Episode.AAC.Stereo.mp4", "AAC", "Stereo"),
            ("Movie.TrueHD.Atmos.mkv", "TrueHD", None),
        ]

        for filename, expected_audio_codec, expected_channels in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            assert quality_info.audio_codec == expected_audio_codec
            if expected_channels:
                assert quality_info.audio_channels == expected_channels

    def test_extract_source_patterns(self, extractor):
        """Test source extraction patterns"""
        test_cases = [
            ("Movie.2020.1080p.BluRay.x264.mkv", "BluRay"),
            ("Show.S01E01.720p.HDTV.x265.mp4", "HDTV"),
            ("Film.2019.WEB-DL.1080p.mkv", "WEBDL"),
            ("Episode.WEBRip.720p.h264.mp4", "WEBRip"),
            ("Movie.DVDRip.XviD.avi", "DVD"),
        ]

        for filename, expected_source in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            assert quality_info.source == expected_source

    def test_extract_quality_tags(self, extractor):
        """Test quality tag extraction"""
        test_cases = [
            ("Movie.2020.1080p.BluRay.Proper.x264.mkv", ["Proper"]),
            ("Show.S01E01.REPACK.720p.HDTV.mp4", ["REPACK"]),
            ("Film.Extended.Directors.Cut.mkv", ["Extended"]),
            ("Movie.INTERNAL.1080p.WEB.mkv", ["INTERNAL"]),
        ]

        for filename, expected_tags in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            for tag in expected_tags:
                assert tag in quality_info.quality_tags

    def test_extract_release_group(self, extractor):
        """Test release group extraction"""
        test_cases = [
            ("Movie.2020.1080p.BluRay.x264-GROUP.mkv", "GROUP"),
            ("Show.S01E01.720p.HDTV.x265-TEAM.mp4", "TEAM"),
            ("Film.2019.WEB-DL.1080p-RELEASE.mkv", "RELEASE"),
            ("Movie.[ReleaseGroup].1080p.mkv", "ReleaseGroup"),
        ]

        for filename, expected_group in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            assert quality_info.release_group == expected_group

    def test_extract_platform_source(self, extractor):
        """Test platform/network source extraction"""
        test_cases = [
            ("Show.S01E01.AMZN.WEB-DL.1080p.mkv", "AMZN WEBDL"),
            ("Movie.Netflix.WEBRip.720p.mp4", "Netflix WEBRip"),
            ("Episode.HULU.WEBDL.1080p.mkv", "HULU WEBDL"),
            ("Film.HBO.WEB-DL.4K.mkv", "HBO WEBDL"),
        ]

        for filename, expected_source in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            assert quality_info.source == expected_source

    def test_format_quality_string_complete(self, extractor):
        """Test formatting complete quality information"""
        quality_info = QualityInfo(
            resolution="1080p",
            video_codec="h264",
            audio_codec="EAC3",
            audio_channels="2.0",
            source="AMZN WEBDL",
            quality_tags=["Proper"],
            release_group="Kitsune",
        )

        result = extractor.format_quality_string(quality_info)
        expected = "[AMZN WEBDL-1080p Proper][EAC3 2.0][h264]-Kitsune"
        assert result == expected

    def test_format_quality_string_minimal(self, extractor):
        """Test formatting minimal quality information"""
        quality_info = QualityInfo(resolution="720p", source="HDTV")

        result = extractor.format_quality_string(quality_info)
        expected = "[HDTV-720p]"
        assert result == expected

    def test_format_quality_string_empty(self, extractor):
        """Test formatting empty quality information"""
        quality_info = QualityInfo()

        result = extractor.format_quality_string(quality_info)
        assert result == ""

    @patch("media_renamer.quality_extractor.PYMEDIAINFO_AVAILABLE", True)
    @patch("media_renamer.quality_extractor.MediaInfo")
    def test_extract_from_mediainfo(self, mock_mediainfo, extractor, tmp_path):
        """Test MediaInfo extraction (when PyMediaInfo is available)"""
        test_file = tmp_path / "test.mkv"
        test_file.touch()

        # Mock MediaInfo response
        mock_media = Mock()
        mock_track1 = Mock()
        mock_track1.track_type = "Video"
        mock_track1.height = 1080
        mock_track1.codec = "AVC"

        mock_track2 = Mock()
        mock_track2.track_type = "Audio"
        mock_track2.codec = "E-AC-3"
        mock_track2.channel_s = 2

        mock_media.tracks = [mock_track1, mock_track2]
        mock_mediainfo.parse.return_value = mock_media

        quality_info = extractor.extract_from_mediainfo(test_file)

        assert quality_info.resolution == "1080p"
        assert quality_info.video_codec == "h264"  # Normalized from AVC
        assert quality_info.audio_codec == "E-AC-3"
        assert quality_info.audio_channels == "2.0"

    @patch("media_renamer.quality_extractor.PYMEDIAINFO_AVAILABLE", False)
    def test_extract_from_mediainfo_unavailable(self, extractor, tmp_path):
        """Test MediaInfo extraction when PyMediaInfo is not available"""
        test_file = tmp_path / "test.mkv"
        test_file.touch()

        quality_info = extractor.extract_from_mediainfo(test_file)

        # Should return empty QualityInfo when PyMediaInfo is not available
        assert quality_info.resolution is None
        assert quality_info.video_codec is None
        assert quality_info.audio_codec is None

    def test_hybrid_extraction_complete_filename(self, extractor, tmp_path):
        """Test hybrid extraction when filename has complete info"""
        test_file = tmp_path / "Movie.2020.1080p.BluRay.DTS.5.1.x264-GROUP.mkv"
        test_file.touch()

        # Should use filename info since it's complete
        quality_info = extractor.extract_quality_info(test_file)

        assert quality_info.resolution == "1080p"
        assert quality_info.source == "BluRay"
        assert quality_info.video_codec == "h264"
        assert quality_info.audio_codec == "DTS"
        assert quality_info.audio_channels == "5.1"
        assert quality_info.release_group == "GROUP"

    @patch("media_renamer.quality_extractor.PYMEDIAINFO_AVAILABLE", True)
    @patch("media_renamer.quality_extractor.MediaInfo")
    def test_hybrid_extraction_merge_results(self, mock_mediainfo, extractor, tmp_path):
        """Test hybrid extraction merging filename and MediaInfo results"""
        test_file = tmp_path / "Movie.2020.mkv"  # Minimal filename info
        test_file.touch()

        # Mock MediaInfo response
        mock_media = Mock()
        mock_track = Mock()
        mock_track.track_type = "Video"
        mock_track.height = 1080
        mock_track.codec = "HEVC"
        mock_media.tracks = [mock_track]
        mock_mediainfo.parse.return_value = mock_media

        quality_info = extractor.extract_quality_info(test_file)

        # Should merge both sources
        assert quality_info.resolution == "1080p"  # From MediaInfo
        assert quality_info.video_codec == "h265"  # From MediaInfo, normalized

    def test_dot_separated_to_bracket_format(self, extractor):
        """Test conversion from dot-separated filenames to Sonarr bracket format"""
        test_cases = [
            ("Breaking.Bad.S01E01.720p.HDTV.x264-CTU.mkv", "[HDTV-720p][h264]-CTU"),
            (
                "Game.of.Thrones.S08E06.2160p.WEB-DL.DDP5.1.HDR.HEVC-TOMMY.mkv",
                "[WEBDL-2160p HDR][DDP 5.1][h265]-TOMMY",
            ),
            (
                "The.Mandalorian.S01E01.1080p.DSNP.WEB-DL.DDP5.1.H.264-TOMMY.mkv",
                "[DSNP WEBDL-1080p][DDP 5.1]-TOMMY",
            ),
            (
                "Stranger.Things.S04E01.HDR.2160p.NF.WEB-DL.x265.DDP5.1-TOMMY.mkv",
                "[NF WEBDL-2160p HDR][DDP 5.1][h265]-TOMMY",
            ),
        ]

        for filename, expected_format in test_cases:
            quality_info = extractor.extract_from_filename(Path(filename))
            result = extractor.format_quality_string(quality_info)
            assert (
                result == expected_format
            ), f"Failed for {filename}: got {result}, expected {expected_format}"
