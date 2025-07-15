import logging
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

from media_renamer.api_clients import APIClientManager
from media_renamer.config import Config
from media_renamer.metadata_extractor import MetadataExtractor
from media_renamer.models import MediaInfo, MediaType


@dataclass
class TVShowDirectory:
    """Represents a directory containing TV show content"""
    path: Path
    show_title: str
    season: Optional[int] = None
    year: Optional[int] = None
    tvdb_id: Optional[str] = None
    normalized_title: str = ""
    confidence: float = 0.0


@dataclass
class TVShowGroup:
    """Represents a group of directories for the same TV show"""
    show_title: str
    year: Optional[int] = None
    tvdb_id: Optional[str] = None
    directories: List[TVShowDirectory] = None
    
    def __post_init__(self):
        if self.directories is None:
            self.directories = []


class TVShowConsolidator:
    """Consolidates multiple directories of the same TV show into unified structure"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.extractor = MetadataExtractor()
        self.api_manager = APIClientManager(
            tmdb_key=config.tmdb_api_key,
            tvdb_key=config.tvdb_api_key
        )
        
        # Season detection patterns
        self.season_patterns = [
            r"[Ss]eason\s*(\d+)",
            r"[Ss](\d+)",
            r"Season\s*(\d+)",
            r"^(\d+)$",  # Just a number
        ]
        
        # Year to season mapping patterns for shows that use years
        self.year_season_patterns = [
            r"(\d{4})",  # Extract year
        ]
        
        # Common TV show name normalizations
        self.show_normalizations = {
            "smackdown": ["wwe smackdown", "smackdown live", "friday night smackdown"],
            "raw": ["wwe raw", "monday night raw"],
            "nxt": ["wwe nxt", "nxt wrestling"],
        }

    def consolidate_tv_shows(self, root_directory: Path) -> List[Dict]:
        """Main entry point to consolidate TV show directories"""
        if not root_directory.exists() or not root_directory.is_dir():
            return []
            
        self.logger.info(f"Scanning directory: {root_directory}")
        
        # Step 1: Discover TV show directories
        tv_directories = self._discover_tv_directories(root_directory)
        
        if not tv_directories:
            self.logger.info("No TV show directories found")
            return []
            
        # Step 2: Group directories by TV show
        show_groups = self._group_directories_by_show(tv_directories)
        
        # Step 3: Enhance groups with API data
        enhanced_groups = self._enhance_groups_with_api_data(show_groups)
        
        # Step 4: Consolidate each group
        results = []
        for group in enhanced_groups:
            if len(group.directories) > 1:  # Only consolidate if multiple directories
                result = self._consolidate_show_group(group, root_directory)
                results.append(result)
                
        return results

    def _discover_tv_directories(self, root_directory: Path) -> List[TVShowDirectory]:
        """Discover directories that contain TV show content"""
        tv_directories = []
        
        for directory in root_directory.iterdir():
            if not directory.is_dir():
                continue
                
            tv_dir = self._analyze_directory_for_tv_content(directory)
            if tv_dir:
                tv_directories.append(tv_dir)
                
        self.logger.info(f"Found {len(tv_directories)} potential TV show directories")
        return tv_directories

    def _analyze_directory_for_tv_content(self, directory: Path) -> Optional[TVShowDirectory]:
        """Analyze a directory to determine if it contains TV show content"""
        dir_name = directory.name
        
        # Extract basic info from directory name
        show_title = self._extract_show_title(dir_name)
        season = self._extract_season_from_name(dir_name)
        year = self._extract_year_from_name(dir_name)
        
        # Check if directory contains video files
        has_video_files = self._has_video_files(directory)
        
        if not has_video_files:
            return None
            
        # If no season detected from name, try to infer from files
        if season is None:
            season = self._infer_season_from_files(directory)
            
        # Create TV directory object
        tv_dir = TVShowDirectory(
            path=directory,
            show_title=show_title,
            season=season,
            year=year,
            normalized_title=self._normalize_show_title(show_title)
        )
        
        self.logger.debug(f"TV directory: {tv_dir}")
        return tv_dir

    def _extract_show_title(self, dir_name: str) -> str:
        """Extract show title from directory name"""
        # Remove common patterns
        cleaned = dir_name
        
        # Remove year patterns
        cleaned = re.sub(r'\b(19|20)\d{2}\b', '', cleaned)
        
        # Remove season patterns
        cleaned = re.sub(r'[Ss]eason\s*\d+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'[Ss]\d+', '', cleaned)
        
        # Remove quality indicators
        cleaned = re.sub(r'\b(720p|1080p|480p|4K|WEB|BluRay|DVD|h264|x264|h265|x265)\b', '', cleaned, flags=re.IGNORECASE)
        
        # Remove release group patterns
        cleaned = re.sub(r'-[A-Z0-9]+$', '', cleaned)
        
        # Remove pack indicators
        cleaned = re.sub(r'\bPack\b', '', cleaned, flags=re.IGNORECASE)
        
        # Remove extra whitespace and special characters
        cleaned = re.sub(r'[.\-_]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned or dir_name

    def _extract_season_from_name(self, dir_name: str) -> Optional[int]:
        """Extract season number from directory name"""
        for pattern in self.season_patterns:
            match = re.search(pattern, dir_name, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None

    def _extract_year_from_name(self, dir_name: str) -> Optional[int]:
        """Extract year from directory name"""
        for pattern in self.year_season_patterns:
            match = re.search(pattern, dir_name)
            if match:
                try:
                    year = int(match.group(1))
                    if 1980 <= year <= 2030:  # Reasonable year range
                        return year
                except (ValueError, IndexError):
                    continue
        return None

    def _has_video_files(self, directory: Path) -> bool:
        """Check if directory contains video files"""
        video_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                return True
        return False

    def _infer_season_from_files(self, directory: Path) -> Optional[int]:
        """Infer season from file names in directory"""
        seasons = set()
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.config.supported_extensions:
                media_info = self.extractor.extract_from_filename(file_path)
                if media_info.season:
                    seasons.add(media_info.season)
                    
        # If all files indicate the same season, use it
        if len(seasons) == 1:
            return seasons.pop()
            
        return None

    def _normalize_show_title(self, title: str) -> str:
        """Normalize show title for comparison"""
        normalized = title.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Apply known normalizations
        for base_name, variants in self.show_normalizations.items():
            if any(variant in normalized for variant in variants) or base_name in normalized:
                return base_name
                
        return normalized

    def _group_directories_by_show(self, tv_directories: List[TVShowDirectory]) -> List[TVShowGroup]:
        """Group directories that belong to the same TV show"""
        groups = []
        used_directories = set()
        
        for i, tv_dir in enumerate(tv_directories):
            if i in used_directories:
                continue
                
            # Create new group
            group = TVShowGroup(
                show_title=tv_dir.show_title,
                year=tv_dir.year,
                directories=[tv_dir]
            )
            used_directories.add(i)
            
            # Find similar directories
            for j, other_dir in enumerate(tv_directories):
                if j in used_directories or i == j:
                    continue
                    
                if self._are_same_show(tv_dir, other_dir):
                    group.directories.append(other_dir)
                    used_directories.add(j)
                    
            groups.append(group)
            
        self.logger.info(f"Grouped directories into {len(groups)} TV shows")
        return groups

    def _are_same_show(self, dir1: TVShowDirectory, dir2: TVShowDirectory) -> bool:
        """Determine if two directories belong to the same TV show"""
        # Exact normalized title match
        if dir1.normalized_title == dir2.normalized_title:
            return True
            
        # High similarity match
        similarity = SequenceMatcher(None, dir1.normalized_title, dir2.normalized_title).ratio()
        if similarity > 0.8:
            return True
            
        # Check for partial matches in original titles
        title1_words = set(dir1.show_title.lower().split())
        title2_words = set(dir2.show_title.lower().split())
        
        if title1_words and title2_words:
            common_words = title1_words.intersection(title2_words)
            union_words = title1_words.union(title2_words)
            
            if len(common_words) / len(union_words) > 0.6:
                return True
                
        return False

    def _enhance_groups_with_api_data(self, groups: List[TVShowGroup]) -> List[TVShowGroup]:
        """Enhance groups with data from TVDB/TMDB APIs"""
        for group in groups:
            # Use the first directory's info as a starting point
            representative_dir = group.directories[0]
            
            # Create a temporary MediaInfo object for API lookup
            temp_media = MediaInfo(
                original_path=representative_dir.path,
                media_type=MediaType.TV_SHOW,
                title=representative_dir.show_title,
                year=representative_dir.year,
                extension=""
            )
            
            # Enhance with API data
            enhanced_media = self.api_manager.enhance_media_info(temp_media)
            
            # Update group with enhanced data
            group.show_title = enhanced_media.title
            group.year = enhanced_media.year
            group.tvdb_id = enhanced_media.tvdb_id
            
            self.logger.info(f"Enhanced group: {group.show_title} ({group.year}) [tvdb-{group.tvdb_id}]")
            
        return groups

    def _consolidate_show_group(self, group: TVShowGroup, root_directory: Path) -> Dict:
        """Consolidate a group of directories into unified structure"""
        # Create unified directory name
        unified_name = self._generate_unified_directory_name(group)
        unified_path = root_directory / unified_name
        
        self.logger.info(f"Consolidating {len(group.directories)} directories into: {unified_name}")
        
        operations = []
        
        if self.config.dry_run:
            self.logger.info(f"DRY RUN: Would create directory: {unified_path}")
        else:
            unified_path.mkdir(exist_ok=True)
        
        # Process each directory in the group
        for tv_dir in group.directories:
            season_num = tv_dir.season or self._map_year_to_season(tv_dir.year, group)
            
            if season_num:
                season_dir = unified_path / f"Season {season_num:02d}"
                
                if self.config.dry_run:
                    self.logger.info(f"DRY RUN: Would create season directory: {season_dir}")
                    self.logger.info(f"DRY RUN: Would move contents from {tv_dir.path} to {season_dir}")
                else:
                    season_dir.mkdir(exist_ok=True)
                    self._move_directory_contents(tv_dir.path, season_dir)
                
                operations.append({
                    "source": str(tv_dir.path),
                    "destination": str(season_dir),
                    "season": season_num,
                    "success": True
                })
            else:
                self.logger.warning(f"Could not determine season for {tv_dir.path}")
                operations.append({
                    "source": str(tv_dir.path),
                    "destination": None,
                    "season": None,
                    "success": False,
                    "error": "Could not determine season"
                })
        
        return {
            "show_title": group.show_title,
            "unified_directory": str(unified_path),
            "tvdb_id": group.tvdb_id,
            "operations": operations
        }

    def _generate_unified_directory_name(self, group: TVShowGroup) -> str:
        """Generate unified directory name with TVDB ID"""
        title = self._sanitize_directory_name(group.show_title)
        year = f" ({group.year})" if group.year else ""
        tvdb_id = f" [tvdb-{group.tvdb_id}]" if group.tvdb_id else ""
        
        return f"{title}{year}{tvdb_id}"

    def _sanitize_directory_name(self, name: str) -> str:
        """Sanitize directory name for filesystem compatibility"""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        return sanitized

    def _map_year_to_season(self, year: Optional[int], group: TVShowGroup) -> Optional[int]:
        """Map year to season number for shows that use yearly structure"""
        if not year or not group.year:
            return None
            
        # Calculate season based on year offset from show's start year
        season = year - group.year + 1
        
        # Sanity check
        if 1 <= season <= 50:  # Reasonable season range
            return season
            
        return None

    def _move_directory_contents(self, source_dir: Path, dest_dir: Path) -> None:
        """Move all contents from source directory to destination directory"""
        try:
            for item in source_dir.iterdir():
                dest_item = dest_dir / item.name
                
                if item.is_file():
                    if dest_item.exists():
                        self.logger.warning(f"File already exists, skipping: {dest_item}")
                        continue
                    shutil.move(str(item), str(dest_item))
                elif item.is_dir():
                    if dest_item.exists():
                        # Recursively merge directories
                        self._move_directory_contents(item, dest_item)
                        # Remove empty source directory
                        if not any(item.iterdir()):
                            item.rmdir()
                    else:
                        shutil.move(str(item), str(dest_item))
            
            # Remove empty source directory
            if not any(source_dir.iterdir()):
                source_dir.rmdir()
                self.logger.info(f"Removed empty directory: {source_dir}")
                
        except Exception as e:
            self.logger.error(f"Error moving contents from {source_dir} to {dest_dir}: {e}")