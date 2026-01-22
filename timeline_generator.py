"""
    Timeline Generator for Historical Events

    This module provides a comprehensive timeline generation system that integrates
    data scraping, LangChain processing, and database storage.
"""

import os
import time
from typing import List, Dict, Optional, Callable

from wikipedia_scraper import WikipediaScraper
from langchain_processor import HistoricalDataProcessor
from database_manager import DatabaseManager
from cache_manager import CacheManager


class TimelineGenerator:
    """
    Generator for creating historical timelines.

    Supports multiple regions and integrates scraping, processing,
    and database storage.
    """

    def __init__(self,
            region: str,  # 区域名称，例如"European"、"Chinese"
            db_connection_string: str = None,  # SQLite数据库连接字符串，可选参数
            llm_api_key: str = None,  # OpenAI API密钥，用于LangChain，可选参数
            llm_base_url: str = None,  # API基础URL，可选参数
            llm_model: Optional[str] = None):  # 要使用的模型名称，可选参数
        """
        Initialize TimelineGenerator.

        Args:
            region: Region name (e.g., "European", "Chinese")
            db_connection_string: database connection string
            llm_api_key: OpenAI API key for LangChain
            llm_base_url: API base URL
            llm_model: Model name to use
        """
        # print(f"args: {llm_api_key}, {llm_base_url}, {llm_model}")
        self.region = region

        self.scraper = WikipediaScraper(language="en" if region == "European" else "zh", region=region)
        self.cache = CacheManager()

        try:
            processor_kwargs = {
                "api_key": llm_api_key,
                "base_url": llm_base_url
            }
            if llm_model is not None:
                processor_kwargs["model"] = llm_model

            self.processor = HistoricalDataProcessor(**processor_kwargs)
            self.has_processor = True
        except ValueError as e:
            print(f"Warning: LangChain processor not available (no API key)")
            print("Will use simple data extraction without LLM processing")
            print(e)
            self.processor = None
            self.has_processor = False

        self.db = DatabaseManager(db_connection_string)
        self.db.create_tables()

    CHINESE_DYNASTIES = [
        "夏朝",
        "商朝",
        "周朝",
        "秦朝",
        "汉朝",
        "三国",
        "晋朝",
        "南北朝",
        "隋朝",
        "唐朝",
        "五代十国",
        "宋朝",
        "元朝",
        "明朝",
        "清朝",
        "中華民國",
        "中华人民共和国"
    ]

    def scrape_from_dynasties(self,
                            max_events_per_dynasty: int = 50,
                            min_importance: int = 5,
                            force_refresh: bool = False,
                            progress_callback: Optional[Callable] = None) -> Dict[str, int]:
        """
        Scrape Chinese history by dynasty pages instead of year pages.
        Uses cache to avoid redundant scraping and LLM processing.

        Args:
            max_events_per_dynasty: Maximum number of events to extract per dynasty
            min_importance: Minimum importance level for events to save
            force_refresh: Force re-scraping and re-processing
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with counts of inserted events and periods
        """
        print(f"Scraping Chinese history from {len(self.CHINESE_DYNASTIES)} dynasty pages...")
        if force_refresh:
            print("Force refresh mode: will re-scrape and re-process all data")

        events_inserted = 0
        periods_inserted = 0
        total_dynasties = len(self.CHINESE_DYNASTIES)

        for i, dynasty in enumerate(self.CHINESE_DYNASTIES):
            if progress_callback:
                progress = (i + 1) / total_dynasties * 100
                progress_callback(f"Processing dynasty {dynasty} ({progress:.1f}%)")

            # Check LLM cache first (using dynasty name as cache key)
            if not force_refresh:
                cached_events = self.cache.load_llm_data(self.region, dynasty)
                if cached_events:
                    print(f"Cache hit: {self.region}_{dynasty} (LLM)")
                    for event in cached_events:
                        if self.processor and self.processor.validate_event(event):
                            importance = int(event.get("importance_level", 5))
                            if importance >= min_importance:
                                self.db.insert_event(event)
                                events_inserted += 1
                        elif not self.processor:
                            self.db.insert_event(event)
                            events_inserted += 1
                    continue

            # No LLM cache - try to use Raw cache or scrape
            dynasty_content = None

            if not force_refresh:
                cached_raw = self.cache.load_raw_data(self.region, dynasty)
                if cached_raw:
                    print(f"Cache hit: {self.region}_{dynasty} (Raw), processing with LLM...")
                    dynasty_content = cached_raw
                else:
                    print(f"Cache miss: {self.region}_{dynasty}, scraping from Wikipedia...")
                    dynasty_content = self.scraper.get_dynasty_page(dynasty)
            else:
                print(f"Force refresh: {self.region}_{dynasty}, scraping from Wikipedia...")
                dynasty_content = self.scraper.get_dynasty_page(dynasty)

            if dynasty_content:
                if self.has_processor:
                    events = self.processor.extract_events_from_dynasty_page(
                        dynasty,
                        dynasty_content,
                        self.region,
                        max_events_per_dynasty
                    )
                    # Save to LLM cache
                    self.cache.save_llm_data(self.region, dynasty, events)
                    print(f"Cache saved: {self.region}_{dynasty} (LLM)")
                else:
                    events = self._simple_extract_events_from_dynasty(dynasty, dynasty_content)

                # Insert events into database
                for event in events:
                    if self.processor and self.processor.validate_event(event):
                        importance = int(event.get("importance_level", 5))
                        if importance >= min_importance:
                            self.db.insert_event(event)
                            events_inserted += 1
                    elif not self.processor:
                        self.db.insert_event(event)
                        events_inserted += 1

                print(f"  {dynasty}: {len(events)} events extracted")

            time.sleep(0.5)

        print(f"Total inserted: {events_inserted} events")
        return {"events": events_inserted, "periods": periods_inserted}

    def scrape_year_range(self,
                            start_year: int,
                            end_year: int,
                            process_with_llm: bool = True,
                            progress_callback: Optional[Callable] = None) -> Dict[str, int]:
        """
        Scrape events from Wikipedia for a range of years.

        Args:
            start_year: Start year
            end_year: End year
            process_with_llm: Whether to process scraped data with LLM
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with counts of inserted events and periods
        """
        print(f"Scraping {self.region} history from {start_year} to {end_year}...")

        events_inserted = 0
        periods_inserted = 0
        total_years = abs(end_year - start_year)

        for i, year in enumerate(range(start_year, end_year + 1)):
            if progress_callback:
                progress = (i + 1) / total_years * 100
                progress_callback(f"Processing year {year} ({progress:.1f}%)")

            year_content = self.scraper.get_year_page(year)

            if not year_content:
                time.sleep(0.5)
                continue

            if process_with_llm and self.has_processor:
                events = self.processor.extract_events_from_year_page(
                    year,
                    year_content,
                    self.region
                )
            else:
                events = self._simple_extract_events(year, year_content)

            for event in events:
                if self.processor and self.processor.validate_event(event):
                    self.db.insert_event(event)
                    events_inserted += 1
                elif not self.processor:
                    event["importance_level"] = 5
                    self.db.insert_event(event)
                    events_inserted += 1

            time.sleep(0.5)

        print(f"Inserted {events_inserted} events")
        return {"events": events_inserted, "periods": periods_inserted}

    def scrape_key_events(self,
                        num_events: int = 50,
                        process_with_llm: bool = True) -> Dict[str, int]:
        """
        Scrape key historical events from Wikipedia search.

        Args:
            num_events: Number of events to scrape
            process_with_llm: Whether to process scraped data with LLM

        Returns:
            Dictionary with counts of inserted events and periods
        """
        print(f"Scraping key {self.region} events...")

        search_results = self.scraper.search_historical_periods(self.region)

        events_inserted = 0
        periods_inserted = 0

        for result in search_results[:num_events]:
            page_content = self.scraper.get_page_content(result['pageid'])

            if not page_content:
                continue

            if process_with_llm and self.has_processor:
                event = self.processor.process_wikipedia_page_as_event(
                    page_content,
                    self.region
                )
            else:
                event = self._simple_extract_event(page_content)

            if event:
                if self.processor and self.processor.validate_event(event):
                    self.db.insert_event(event)
                    events_inserted += 1
                elif not self.processor:
                    self.db.insert_event(event)
                    events_inserted += 1

            time.sleep(0.5)

        print(f"Inserted {events_inserted} events")
        return {"events": events_inserted, "periods": periods_inserted}

    def _simple_extract_event(self, page_content: Dict) -> Optional[Dict]:
        """
        Simple event extraction without LLM.

        Args:
            page_content: Wikipedia page content

        Returns:
            Event dictionary or None
        """
        title = page_content.get("title", "")
        extract = page_content.get("extract", "")

        if not extract:
            return None

        return {
            "event_name": title,
            "start_year": 0,
            "end_year": None,
            "key_figures": None,
            "description": extract[:500],
            "impact": None,
            "category": "cultural",
            "region": self.region,
            "importance_level": 5,
            "source": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        }

    def _simple_extract_events(self, year: int, year_content: Dict) -> List[Dict]:
        """
        Simple events extraction from year page without LLM.

        Args:
            year: Year number
            year_content: Wikipedia year page content

        Returns:
            List of event dictionaries
        """
        extract = year_content.get("extract", "")

        if not extract:
            return []

        return [{
            "event_name": f"{abs(year)} {'BC' if year < 0 else ''}",
            "start_year": year,
            "end_year": None,
            "key_figures": None,
            "description": extract[:500],
            "impact": None,
            "category": "historical",
            "region": self.region,
            "importance_level": 5,
            "source": f"https://en.wikipedia.org/wiki/{abs(year)}_{'BC' if year < 0 else ''}"
        }]

    def _simple_extract_events_from_dynasty(self, dynasty_name: str, dynasty_content: Dict) -> List[Dict]:
        """
        Simple events extraction from dynasty page without LLM.
        Creates basic events based on dynasty name.
        Args:
            dynasty_name: Dynasty name (e.g., "唐朝", "中华民国")
            dynasty_content: Wikipedia dynasty page content
        Returns:
            List of basic event dictionaries
        """
        extract = dynasty_content.get("extract", "")
        if not extract:
            return []
        # Create a basic event representing the dynasty
        return [{
            "event_name": f"{dynasty_name}时期",
            "start_year": 1900,  # Default fallback year
            "end_year": None,
            "key_figures": None,
            "description": extract[:500],
            "impact": f"{dynasty_name}是中國歷史上的重要時期",
            "category": "政治",
            "region": self.region,
            "importance_level": 7,
            "source": f"https://zh.wikipedia.org/wiki/{dynasty_name}"
        }]


    def get_timeline(self,
                    start_year: int = None,
                    end_year: int = None,
                    min_importance: int = None,
                    limit: int = 100) -> List[Dict]:
        """
        Get timeline events from database.

        Args:
            start_year: Start year (optional)
            end_year: End year (optional)
            min_importance: Minimum importance level (optional)
            limit: Maximum number of results

        Returns:
            List of event dictionaries
        """
        if start_year is None and end_year is None:
            stats = self.db.get_statistics()
            return []

        if start_year is None:
            start_year = -1000
        if end_year is None:
            end_year = 2026

        return self.db.get_events_by_time_range(
            start_year=start_year,
            end_year=end_year,
            region=self.region,
            min_importance=min_importance,
            limit=limit
        )

    def search_events(self, keyword: str, limit: int = 50) -> List[Dict]:
        """
        Search events by keyword.

        Args:
            keyword: Search keyword
            limit: Maximum number of results

        Returns:
            List of event dictionaries
        """
        return self.db.search_events_by_keyword(
            keyword=keyword,
            region=self.region,
            limit=limit
        )

    def scrape_key_periods_by_list(self, period_names: List[str],
                                events_per_period: int = 5,
                                min_importance: int = 7,
                                progress_callback: Optional[Callable] = None) -> Dict[str, int]:
        """
        Scrape key historical periods and their representative events.

        Args:
            period_names: List of key period names to scrape
            events_per_period: Number of events to extract from each period
            min_importance: Minimum importance level for events
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with counts of inserted events and periods
        """
        print(f"Scraping {len(period_names)} key periods for {self.region}...")

        periods_inserted = 0
        events_inserted = 0

        for i, period_name in enumerate(period_names):
            if progress_callback:
                progress_callback(f"Processing period {i+1}/{len(period_names)}: {period_name}")

            time.sleep(0.5)

            search_results = self.scraper.search_pages(period_name, limit=3)

            if search_results:
                period_content = self.scraper.get_page_content(search_results[0]['pageid'])

                if period_content:
                    if self.has_processor:
                        period_data = self.processor.process_wikipedia_page_as_period(
                            period_content,
                            self.region
                        )
                    else:
                        period_data = {
                            "period_name": period_name,
                            "start_year": 0,
                            "end_year": 100,
                            "period_type": "independent",
                            "description": period_content.get("extract", "")[:500],
                            "region": self.region
                        }

                    if period_data:
                        self.db.insert_period(period_data)
                        periods_inserted += 1

            time.sleep(0.5)

        print(f"Inserted {periods_inserted} periods")
        return {"events": events_inserted, "periods": periods_inserted}

    def scrape_full_timeline(self,
                    classical_years: int = 1000,
                    medieval_years: int = 50,
                    early_modern_years: int = 25,
                    nineteenth_century_years: int = 10,
                    twentieth_century_years: int = 5,
                    twenty_first_century_years: int = 1,
                    min_importance: int = 6,
                    force_refresh: bool = False,
                    progress_callback: Optional[Callable] = None) -> Dict[str, int]:
        """
        Scrape historical timeline from -1000 to 2026 using phased sampling.
        Uses cache to avoid redundant scraping and LLM processing.

        Args:
            classical_years: Sampling interval for classical period (-1000 to 500)
            medieval_years: Sampling interval for medieval period (500 to 1500)
            early_modern_years: Sampling interval for early modern period (1500 to 1800)
            nineteenth_century_years: Sampling interval for 19th century (1800 to 1900)
            twentieth_century_years: Sampling interval for 20th century (1900 to 2000)
            twenty_first_century_years: Sampling interval for 21st century (2000 to 2026)
            min_importance: Minimum importance level to keep events
            force_refresh: Force re-scraping and re-processing
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with counts of inserted events and periods
        """
        print(f"Scraping full timeline for {self.region} from -1000 to 2026...")
        if force_refresh:
            print("Force refresh mode: will re-scrape and re-process all data")

        events_inserted = 0

        phases = [
            ("Classical Period", -1000, 500, classical_years),
            ("Middle Ages", 501, 1500, medieval_years),
            ("Early Modern", 1501, 1800, early_modern_years),
            ("19th Century", 1801, 1900, nineteenth_century_years),
            ("20th Century", 1901, 2000, twentieth_century_years),
            ("21st Century", 2001, 2026, twenty_first_century_years)
        ]

        for phase_name, start_year, end_year, interval in phases:
            if progress_callback:
                progress_callback(f"Processing {phase_name} ({start_year} to {end_year})...")

            years_to_scrape = list(range(start_year, end_year + 1, interval))
            print(f"  {phase_name}: scraping {len(years_to_scrape)} years ({start_year}-{end_year})")

            for year in years_to_scrape:
                # Check LLM cache first
                if not force_refresh:
                    cached_events = self.cache.load_llm_data(self.region, year)
                    if cached_events:
                        print(f"Cache hit: {self.region}_{year} (LLM)")
                        for event in cached_events:
                            if self.processor and self.processor.validate_event(event):
                                importance = int(event.get("importance_level", 5))
                                if importance >= min_importance:
                                    self.db.insert_event(event)
                                    events_inserted += 1
                            elif not self.processor:
                                self.db.insert_event(event)
                                events_inserted += 1
                        continue

                # No LLM cache - try to use Raw cache or scrape
                year_content = None

                if not force_refresh:
                    cached_raw = self.cache.load_raw_data(self.region, year)
                    if cached_raw:
                        print(f"Cache hit: {self.region}_{year} (Raw), processing with LLM...")
                        year_content = cached_raw
                    else:
                        print(f"Cache miss: {self.region}_{year}, scraping from Wikipedia...")
                        year_content = self.scraper.get_year_page(year, force_refresh=False)
                else:
                    print(f"Force refresh: {self.region}_{year}, scraping from Wikipedia...")
                    year_content = self.scraper.get_year_page(year, force_refresh=True)

                if year_content:
                    if self.has_processor:
                        events = self.processor.extract_events_from_year_page(
                            year,
                            year_content,
                            self.region
                        )
                        # Save to LLM cache
                        self.cache.save_llm_data(self.region, year, events)
                        print(f"Cache saved: {self.region}_{year} (LLM)")
                    else:
                        events = self._simple_extract_events(year, year_content)

                    for event in events:
                        if self.processor and self.processor.validate_event(event):
                            importance = int(event.get("importance_level", 5))
                            if importance >= min_importance:
                                self.db.insert_event(event)
                                events_inserted += 1
                        elif not self.processor:
                            self.db.insert_event(event)
                            events_inserted += 1

                time.sleep(0.3)

        print(f"    Completed {phase_name}")

        print(f"Total events inserted: {events_inserted}")
        return {"events": events_inserted, "periods": 0}

    def get_cross_regional_view(self,
                            year: int,
                            other_regions: List[str],
                            importance_threshold: int = 6) -> Dict[str, List[Dict]]:
        """
        Get events from other regions for cross-regional comparison.

        Args:
            year: Reference year
            other_regions: List of other regions to check
            importance_threshold: Minimum importance level

        Returns:
            Dictionary mapping region to list of events
        """
        return self.db.get_cross_regional_events(
            year=year,
            other_regions=other_regions,
            importance_threshold=importance_threshold
        )

    def get_statistics(self) -> Dict:
        """Get statistics for current region's data."""
        return self.db.get_statistics()
    
    # European civilization search terms for ancient to pre-modern periods
    ANCIENT_SEARCH_TERMS = [
        # Ancient civilizations (3000 BC - 500 BC)
        "Ancient Greece", "Ancient Rome", "Minoan civilization", "Mycenaean civilization",
        # Pre-classical Mediterranean (500 BC - 500 BC)
        "Phoenicians", "Canaan", "Hittites", "Assyrians", "Babylonians",
        # Classical antiquity (500 BC - 1 BC)
        "Classical Greece", "Hellenistic period", "Roman Republic", "Carthage",
        # Early Middle Ages (500 - 1000)
        "Byzantine Empire", "Viking Age", "Islamic Golden Age", "Holy Roman Empire",
        # High Middle Ages (1000 - 1300)
        "Crusades", "Mongol Empire", "Song Dynasty (Chinese influence)"
    ]

    MEDIEVAL_SEARCH_TERMS = [
        # Late Middle Ages (1300 - 1500)
        "Black Death", "Hundred Years' War", "Ottoman Empire", "Renaissance",
        "Hanseatic League", "Caliphate", "War of the Roses", "Italian Renaissance"
    ]

    EARLY_MODERN_SEARCH_TERMS = [
        # Early modern period (1500 - 1789)
        "Age of Discovery", "Reformation", "Scientific Revolution",
        "Age of Enlightenment", "Thirty Years' War", "Ottoman wars",
        "Baroque period", "Colonialism", "Mercantilism"
    ]

    def scrape_civilizations_timeline(self,
                                        max_events_per_period: int = 20,
                                        min_importance: int = 6,
                                        progress_callback: Optional[Callable] = None) -> Dict[str, int]:
        """
        Scrape European historical events from ancient civilizations to pre-WWI.
        Uses targeted Wikipedia page searches for each civilization/period.
        Uses English Wikipedia (for European history), but saves Chinese LLM cache.

        Args:
            max_events_per_period: Maximum events to extract per period
            min_importance: Minimum importance level for events
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with counts of inserted events
        """
        print(f"Scraping European civilizations timeline to 1914...")
        if progress_callback:
            progress_callback(f"Starting European civilizations timeline generation")

        events_inserted = 0
        total_periods = len(self.ANCIENT_SEARCH_TERMS + self.MEDIEVAL_SEARCH_TERMS + self.EARLY_MODERN_SEARCH_TERMS)

        for i, search_terms in enumerate([self.ANCIENT_SEARCH_TERMS, self.MEDIEVAL_SEARCH_TERMS, self.EARLY_MODERN_SEARCH_TERMS]):
            if progress_callback:
                period_num = i + 1
                progress = period_num / total_periods * 100
                progress_callback(f"Processing period {period_num}/{total_periods} ({progress:.1f}%)")

            # Process each search term in the period
            for j, term in enumerate(search_terms):
                if progress_callback:
                    period_progress = (i * len(search_terms) + j) / (total_periods * len(self.ANCIENT_SEARCH_TERMS)) * 100
                    progress_callback(f"  Processing term {j+1}/{len(search_terms)}: {term}")

                # Search Wikipedia for the term
                search_results = self.scraper.search_pages(term, limit=3)

                if not search_results:
                    print(f"  No results found for '{term}'")
                    continue

                # Get the first result's content (in English from English Wikipedia)
                page_content = self.scraper.get_page_content(search_results[0]['pageid'])

                if not page_content:
                    print(f"  Failed to fetch page content for '{term}'")
                    continue

                # Save raw Wikipedia content to cache first
                raw_content = {
                    'title': page_content['title'],
                    'extract': page_content.get('extract', ''),
                    'url': f"https://en.wikipedia.org/wiki/{page_content['title'].replace(' ', '_')}",
                    'region': 'European',
                    'year': None  # Will be determined during processing
                }
                self.cache.save_raw_data('European', 0, raw_content)

                # COMMENTED OUT: Original LLM processing approach
                # This code would call the LLM processor to analyze the raw content and extract structured events
                events = self.processor.process_wikipedia_page_as_event(
                    page_content['title'],
                    page_content.get('extract', ''),
                    'European',
                    max_events_per_period
                )
                # Save to LLM cache
                # TODO: 这里需要增加方法，之前只有年份的缓存，现在应该是事件名
                # self.cache.save_llm_data(self.region, year, events)
                # print(f"Cache saved: {self.region}_{year} (LLM)")

                if not events:
                    print(f"  No events extracted from '{term}'")
                    continue

                # Check database for duplicates and cache
                for event in events:
                    # Check if event already exists in database
                    existing_events = self.db.get_events_by_time_range(
                        event['start_year'] - 5, event['start_year'] + 5,
                        region='European',
                        limit=100
                    )
                    
                    event_key = (event['event_name'], event['start_year'])
                    is_duplicate = False
                    for existing in existing_events:
                        if existing['event_name'] == event['event_name'] and abs(existing['start_year'] - event['start_year']) <= 5:
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        print(f"  Skipping duplicate: {event['event_name']} ({event['start_year']})")
                        continue

                    # Insert into database
                    self.db.insert_event(event)
                    events_inserted += 1

                print(f"  {term}: {len(events)} events extracted")

            time.sleep(0.5)

        print(f"Total civilizations timeline events inserted: {events_inserted}")
        return {"events": events_inserted, "periods": 0}

    # TODO: 需要确定基于事件的缓存结构，再实现这个从缓存读取的方法
    def _extract_events_from_cached_raw_content(self, raw_content: Dict, region: str, max_events: int) -> List[Dict]:
        pass