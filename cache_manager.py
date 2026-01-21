"""
Cache Manager for Historical Data

This module provides caching functionality for scraped Wikipedia data
and LLM-processed events to avoid redundant processing.
"""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime


class CacheManager:
    """Manager for caching scraped and processed historical data."""

    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize cache manager.

        Args:
            cache_dir: Root directory for cache files
        """
        self.cache_dir = cache_dir

    def _get_cache_path(self, region: str, year: int, cache_type: str) -> str:
        """
        Get cache file path for specific data.

        Args:
            region: Region name (e.g., "Chinese", "European")
            year: Year number
            cache_type: Cache type ("Raw" or "LLM")

        Returns:
            Full path to cache file
        """
        region_dir = os.path.join(self.cache_dir, region)
        os.makedirs(region_dir, exist_ok=True)

        filename = f"{region}_{year}_{cache_type}.json"
        return os.path.join(region_dir, filename)

    def save_raw_data(self, region: str, year: int, data: Dict) -> None:
        """
        Save raw scraped data to cache.

        Args:
            region: Region name
            year: Year number
            data: Raw data dictionary
        """
        cache_file = self._get_cache_path(region, year, "Raw")

        cache_data = {
            "region": region,
            "year": year,
            "title": data.get("title", ""),
            "extract": data.get("extract", ""),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    def load_raw_data(self, region: str, year: int) -> Optional[Dict]:
        """
        Load raw scraped data from cache.

        Args:
            region: Region name
            year: Year number

        Returns:
            Cached raw data dictionary or None
        """
        cache_file = self._get_cache_path(region, year, "Raw")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading raw cache for {region}_{year}: {e}")
            return None

    def save_llm_data(self, region: str, year: int, events: List[Dict]) -> None:
        """
        Save LLM-processed events to cache.

        Args:
            region: Region name
            year: Year number
            events: List of processed event dictionaries
        """
        cache_file = self._get_cache_path(region, year, "LLM")

        cache_data = {
            "region": region,
            "year": year,
            "events": events,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    def load_llm_data(self, region: str, year: int) -> Optional[List[Dict]]:
        """
        Load LLM-processed events from cache.

        Args:
            region: Region name
            year: Year number

        Returns:
            List of cached event dictionaries or None
        """
        cache_file = self._get_cache_path(region, year, "LLM")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return cache_data.get("events", [])
        except Exception as e:
            print(f"Error loading LLM cache for {region}_{year}: {e}")
            return None

    def is_cached(self, region: str, year: int) -> bool:
        """
        Check if data is cached (either Raw or LLM).

        Args:
            region: Region name
            year: Year number

        Returns:
            True if any cache exists
        """
        raw_cache = self._get_cache_path(region, year, "Raw")
        llm_cache = self._get_cache_path(region, year, "LLM")
        return os.path.exists(raw_cache) or os.path.exists(llm_cache)

    def clear_cache(self, region: str = None, year: int = None) -> None:
        """
        Clear cache files.

        Args:
            region: Region to clear (None for all regions)
            year: Year to clear (None for all years)
        """
        if region is None:
            # Clear all cache
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isdir(file_path):
                        for cache_file in os.listdir(file_path):
                            os.remove(os.path.join(file_path, cache_file))
                        os.rmdir(file_path)
        else:
            # Clear specific region
            region_dir = os.path.join(self.cache_dir, region)
            if not os.path.exists(region_dir):
                return

            if year is None:
                # Clear all years for region
                for cache_file in os.listdir(region_dir):
                    os.remove(os.path.join(region_dir, cache_file))
                os.rmdir(region_dir)
            else:
                # Clear specific year
                raw_file = self._get_cache_path(region, year, "Raw")
                llm_file = self._get_cache_path(region, year, "LLM")

                if os.path.exists(raw_file):
                    os.remove(raw_file)
                if os.path.exists(llm_file):
                    os.remove(llm_file)

    def get_cache_info(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not os.path.exists(self.cache_dir):
            return {
                "regions": 0,
                "raw_files": 0,
                "llm_files": 0,
                "total_files": 0
            }

        regions = set()
        raw_count = 0
        llm_count = 0

        for region_name in os.listdir(self.cache_dir):
            region_dir = os.path.join(self.cache_dir, region_name)
            if os.path.isdir(region_dir):
                regions.add(region_name)
                for cache_file in os.listdir(region_dir):
                    if cache_file.endswith("_Raw.json"):
                        raw_count += 1
                    elif cache_file.endswith("_LLM.json"):
                        llm_count += 1

        return {
            "regions": len(regions),
            "raw_files": raw_count,
            "llm_files": llm_count,
            "total_files": raw_count + llm_count
        }



