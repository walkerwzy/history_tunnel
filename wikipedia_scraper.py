"""
Wikipedia API Scraper for Historical Events
 
This module provides functionality to scrape historical events from Wikipedia
for European Timeline project.
"""
 
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
from cache_manager import CacheManager


class WikipediaScraper:
    """Scraper for fetching historical events from Wikipedia API."""

    def __init__(self, language: str = "en", user_agent: str = "TimelineProject/1.0", region: str = "European"):
        """
        Initialize Wikipedia scraper.

        Args:
            language: Wikipedia language code (default: "en" for English)
            user_agent: User agent string for API requests
            region: Region name (e.g., "European", "Chinese")
        """
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.language = language
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.region = region
        self.cache = CacheManager()

    def search_pages(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search Wikipedia pages related to a query.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of page information dictionaries
        """
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': limit,
            'format': 'json',
            'origin': '*'
        }

        try:
            response = self.session.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('query', {}).get('search', [])
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return []

    def get_page_content(self, page_id: int) -> Optional[Dict]:
        """
        Get the full content of a Wikipedia page.

        Args:
            page_id: Wikipedia page ID

        Returns:
            Dictionary with page content including text, categories, etc.
        """
        params = {
            'action': 'query',
            'prop': 'extracts|categories|pageprops',
            'exintro': False,
            'explaintext': True,
            'exsectionformat': 'wiki',
            'cllimit': 500,
            'ppprop': 'wikibase_item',
            'pageids': page_id,
            'format': 'json',
            'origin': '*'
        }

        try:
            response = self.session.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            return pages.get(str(page_id))
        except requests.exceptions.Timeout:
            print(f"Timeout fetching page {page_id}")
            return None
        except Exception as e:
            print(f"Error fetching page {page_id}: {e}")
            return None

    def search_historical_periods(self, region: str = "European") -> List[Dict]:
        """
        Search for historical periods (e.g., "Middle Ages", "Renaissance").

        Args:
            region: Region to focus on (e.g., "European", "Chinese")

        Returns:
            List of period data dictionaries
        """
        queries = [
            f"{region} history timeline",
            f"{region} historical periods",
            f"{region} eras",
            f"Timeline of {region} history"
        ]

        all_periods = []
        for query in queries:
            results = self.search_pages(query, limit=10)
            all_periods.extend(results)
            time.sleep(0.5)  # Rate limiting

        # Remove duplicates
        seen = set()
        unique_periods = []
        for period in all_periods:
            if period['pageid'] not in seen:
                seen.add(period['pageid'])
                unique_periods.append(period)

        return unique_periods

    def search_historical_events(self, year_range: tuple, region: str = "European") -> List[Dict]:
        """
        Search for historical events within a year range.

        Args:
            year_range: Tuple of (start_year, end_year)
            region: Region to focus on

        Returns:
            List of event data dictionaries
        """
        start_year, end_year = year_range

        queries = [
            f"{region} events {start_year}",
            f"{region} events {end_year}",
            f"Timeline of {region} history {start_year}",
            f"History of {region} {abs(start_year)} {'BC' if start_year < 0 else 'AD'}"
        ]

        all_events = []
        for query in queries:
            results = self.search_pages(query, limit=10)
            all_events.extend(results)
            time.sleep(0.5)  # Rate limiting

        # Remove duplicates
        seen = set()
        unique_events = []
        for event in all_events:
            if event['pageid'] not in seen:
                seen.add(event['pageid'])
                unique_events.append(event)

        return unique_events

    def get_year_page(self, year: int, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get content for a specific year page (e.g., "1492" page).
        Uses cache to avoid redundant scraping.

        Args:
            year: Year to fetch (negative for BC)
            force_refresh: Force re-scraping even if cached

        Returns:
            Dictionary with year page content or None
        """
        # Check cache first
        if not force_refresh:
            cached_data = self.cache.load_raw_data(self.region, year)
            if cached_data:
                print(f"Cache hit: {self.region}_{year} (Raw)")
                return cached_data

        # Not cached or force refresh - scrape from Wikipedia
        if year < 0:
            page_title = f"{abs(year)} BC"
        else:
            if self.language == "zh":
                page_title = f"{year}年"
            else:
                page_title = str(year)

        params = {
            'action': 'query',
            'prop': 'extracts|categories|revisions',
            'exintro': False,
            'explaintext': True,
            'titles': page_title,
            'format': 'json',
            'origin': '*'
        }

        try:
            response = self.session.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            # Find the page ID (might be -1 if page doesn't exist)
            for page_id, page_data in pages.items():
                if page_id != '-1':
                    # Save to cache
                    self.cache.save_raw_data(self.region, year, page_data)
                    print(f"Cache saved: {self.region}_{year} (Raw)")
                    return page_data

            return None
        except Exception as e:
            print(f"Error fetching year page {year}: {e}")
            return None

    def get_dynasty_page(self, dynasty_name: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get content for a Chinese dynasty page (e.g., "唐朝", "宋朝").
        Uses cache to avoid redundant scraping.

        Args:
            dynasty_name: Dynasty name in Chinese (e.g., "唐朝", "宋朝", "明朝")
            force_refresh: Force re-scraping even if cached

        Returns:
            Dictionary with dynasty page content or None
        """
        # Check cache first
        if not force_refresh:
            cached_data = self.cache.load_raw_data(self.region, dynasty_name)
            if cached_data:
                print(f"Cache hit: {self.region}_{dynasty_name} (Raw)")
                return cached_data

        # Not cached or force refresh - scrape from Wikipedia
        params = {
            'action': 'query',
            'prop': 'extracts|categories|pageprops',
            'exintro': False,
            'explaintext': True,
            'exsectionformat': 'wiki',
            'cllimit': 500,
            'ppprop': 'wikibase_item',
            'titles': dynasty_name,
            'format': 'json',
            'origin': '*'
        }

        try:
            response = self.session.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            # Find page ID (might be -1 if page doesn't exist)
            for page_id, page_data in pages.items():
                if page_id != '-1':
                    # Add dynasty name to page data for identification
                    page_data['dynasty_name'] = dynasty_name
                    # Save to cache
                    self.cache.save_raw_data(self.region, dynasty_name, page_data)
                    print(f"Cache saved: {self.region}_{dynasty_name} (Raw)")
                    return page_data

            return None
        except Exception as e:
            print(f"Error fetching dynasty page {dynasty_name}: {e}")
            return None


