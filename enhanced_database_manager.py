"""
Enhanced Database Manager with Advanced Query Features

This module extends the base DatabaseManager with:
- Pagination support for time-axis scrolling
- Enhanced cross-regional queries
- Aggregated statistics queries
- Event importance-based filtering
"""

from typing import List, Dict, Optional, Tuple
from database_manager import DatabaseManager
from sqlalchemy import text


class EnhancedDatabaseManager(DatabaseManager):
    """Extended database manager with advanced query features."""

    def get_events_paginated(self,
                             start_year: Optional[int] = None,
                             end_year: Optional[int] = None,
                             region: Optional[str] = None,
                             min_importance: Optional[int] = None,
                             offset: int = 0,
                             limit: int = 50) -> Tuple[List[Dict], Dict]:
        """
        Get events with pagination support (for scrolling timeline).

        Args:
            start_year: Start year (optional)
            end_year: End year (optional)
            region: Filter by region (optional)
            min_importance: Filter by minimum importance level (optional)
            offset: Pagination offset (default 0)
            limit: Maximum number of results (default 50)

        Returns:
            Tuple of (events list, metadata dict with total_count)
        """
        # Build WHERE clause
        conditions = []
        params = {}

        if start_year is not None:
            conditions.append("start_year >= :start_year")
            params["start_year"] = start_year

        if end_year is not None:
            conditions.append("start_year <= :end_year")
            params["end_year"] = end_year

        if region:
            conditions.append("region = :region")
            params["region"] = region

        if min_importance is not None:
            conditions.append("importance_level >= :min_importance")
            params["min_importance"] = min_importance

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Count total for pagination metadata
        count_query = text(f"""
            SELECT COUNT(*) as total FROM events
            {where_clause}
        """)

        # Get paginated data
        data_query = text(f"""
            SELECT * FROM events
            {where_clause}
            ORDER BY start_year ASC, importance_level DESC
            LIMIT :limit OFFSET :offset
        """)

        params.update({"limit": limit, "offset": offset})

        try:
            with self.engine.connect() as conn:
                # Get total count
                count_result = conn.execute(count_query, params)
                total = count_result.fetchone()[0]

                # Get paginated events
                data_result = conn.execute(data_query, params)
                columns = data_result.keys()
                events = [dict(zip(columns, row)) for row in data_result]

                metadata = {
                    "total": total,
                    "offset": offset,
                    "limit": limit,
                    "has_more": (offset + limit) < total
                }

                return events, metadata
        except Exception as e:
            print(f"Error in paginated query: {e}")
            return [], {"total": 0, "offset": offset, "limit": limit, "has_more": False}

    def get_events_by_importance(self,
                                 region: Optional[str] = None,
                                 importance_threshold: int = 8,
                                 limit: int = 100) -> List[Dict]:
        """
        Get events filtered by importance level.

        Args:
            region: Filter by region (optional)
            importance_threshold: Minimum importance level (default 8)
            limit: Maximum number of results (default 100)

        Returns:
            List of event dictionaries
        """
        base_query = """
            SELECT * FROM events
            WHERE importance_level >= :threshold
        """

        params = {"threshold": importance_threshold, "limit": limit}

        if region:
            base_query += " AND region = :region"
            params["region"] = region

        base_query += " ORDER BY importance_level DESC, start_year ASC LIMIT :limit"

        query = text(base_query)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            print(f"Error querying by importance: {e}")
            return []

    def get_events_around_year(self,
                               year: int,
                               years_before: int = 25,
                               years_after: int = 25,
                               region: Optional[str] = None,
                               min_importance: Optional[int] = None,
                               limit: int = 50) -> List[Dict]:
        """
        Get events around a specific year (for cross-regional comparison).

        Args:
            year: Reference year
            years_before: Years before the reference (default 25)
            years_after: Years after the reference (default 25)
            region: Filter by region (optional)
            min_importance: Filter by minimum importance (optional)
            limit: Maximum number of results (default 50)

        Returns:
            List of event dictionaries
        """
        start_year = year - years_before
        end_year = year + years_after

        return self.get_events_by_time_range(
            start_year=start_year,
            end_year=end_year,
            region=region,
            min_importance=min_importance,
            limit=limit
        )

    def get_cross_regional_comparison(self,
                                     year: int,
                                     regions: List[str],
                                     years_around: int = 50,
                                     importance_threshold: int = 6) -> Dict[str, Dict]:
        """
        Get comprehensive cross-regional comparison.

        Args:
            year: Reference year
            regions: List of regions to compare
            years_around: Years before and after (default 50)
            importance_threshold: Minimum importance level (default 6)

        Returns:
            Dictionary with region names as keys, containing events and statistics
        """
        comparison = {}

        for region in regions:
            events = self.get_events_around_year(
                year=year,
                years_before=years_around,
                years_after=years_around,
                region=region,
                min_importance=importance_threshold,
                limit=100
            )

            # Calculate statistics
            stats = {
                "total_events": len(events),
                "highest_importance": max([e["importance_level"] for e in events]) if events else 0,
                "categories": {}
            }

            # Count by category
            for event in events:
                cat = event.get("category", "unknown")
                stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

            comparison[region] = {
                "events": events,
                "statistics": stats
            }

        return comparison

    def search_events_advanced(self,
                               query: str,
                               region: Optional[str] = None,
                               category: Optional[str] = None,
                               min_importance: Optional[int] = None,
                               start_year: Optional[int] = None,
                               end_year: Optional[int] = None,
                               limit: int = 50) -> List[Dict]:
        """
        Advanced search with multiple filters.

        Args:
            keyword: Search keyword
            region: Filter by region (optional)
            category: Filter by category (optional)
            min_importance: Filter by minimum importance (optional)
            start_year: Filter events after this year (optional)
            end_year: Filter events before this year (optional)
            limit: Maximum number of results (default 50)

        Returns:
            List of event dictionaries
        """
        base_query = """
            SELECT * FROM events
            WHERE (
                LOWER(event_name) LIKE LOWER(:keyword) OR
                LOWER(description) LIKE LOWER(:keyword) OR
                LOWER(impact) LIKE LOWER(:keyword) OR
                LOWER(key_figures) LIKE LOWER(:keyword)
            )
        """

        params = {"keyword": f"%{keyword}%", "limit": limit}

        if region:
            base_query += " AND region = :region"
            params["region"] = region

        if category:
            base_query += " AND category = :category"
            params["category"] = category

        if min_importance:
            base_query += " AND importance_level >= :min_importance"
            params["min_importance"] = min_importance

        if start_year:
            base_query += " AND start_year >= :start_year"
            params["start_year"] = start_year

        if end_year:
            base_query += " AND start_year <= :end_year"
            params["end_year"] = end_year

        base_query += " ORDER BY importance_level DESC, start_year ASC LIMIT :limit"

        query = text(base_query)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            print(f"Error in advanced search: {e}")
            return []

    def get_timeline_statistics(self,
                               start_year: Optional[int] = None,
                               end_year: Optional[int] = None,
                               region: Optional[str] = None) -> Dict:
        """
        Get comprehensive timeline statistics.

        Args:
            start_year: Start year (optional)
            end_year: End year (optional)
            region: Filter by region (optional)

        Returns:
            Dictionary with detailed statistics
        """
        conditions = []
        params = {}

        if start_year is not None:
            conditions.append("start_year >= :start_year")
            params["start_year"] = start_year

        if end_year is not None:
            conditions.append("start_year <= :end_year")
            params["end_year"] = end_year

        if region:
            conditions.append("region = :region")
            params["region"] = region

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        queries = {
            "total_events": text(f"SELECT COUNT(*) FROM events {where_clause}"),
            "avg_importance": text(f"SELECT AVG(importance_level) FROM events {where_clause}"),
            "max_importance": text(f"SELECT MAX(importance_level) FROM events {where_clause}"),
            "min_importance": text(f"SELECT MIN(importance_level) FROM events {where_clause}"),
            "by_category": text(f"SELECT category, COUNT(*) as count FROM events {where_clause} GROUP BY category ORDER BY count DESC"),
            "by_region": text(f"SELECT region, COUNT(*) as count FROM events {where_clause} GROUP BY region ORDER BY count DESC")
        }

        stats = {}
        with self.engine.connect() as conn:
            # Basic stats
            for key, query in queries.items():
                if "GROUP BY" in str(query):
                    # Returns multiple rows
                    result = conn.execute(query, params)
                    stats[key] = {row[0]: row[1] for row in result}
                else:
                    # Returns single value
                    result = conn.execute(query, params)
                    stats[key] = result.fetchone()[0]

        return stats

    def get_years_with_most_events(self,
                                   region: Optional[str] = None,
                                   min_importance: int = 6,
                                   limit: int = 10) -> List[Dict]:
        """
        Get years with the most events.

        Args:
            region: Filter by region (optional)
            min_importance: Filter by minimum importance (default 6)
            limit: Maximum number of years to return (default 10)

        Returns:
            List of dictionaries with year and event count
        """
        base_query = """
            SELECT start_year, COUNT(*) as event_count,
                   AVG(importance_level) as avg_importance
            FROM events
            WHERE importance_level >= :min_importance
        """

        params = {"min_importance": min_importance, "limit": limit}

        if region:
            base_query += " AND region = :region"
            params["region"] = region

        base_query += """
            GROUP BY start_year
            ORDER BY event_count DESC
            LIMIT :limit
        """

        query = text(base_query)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            print(f"Error querying years with most events: {e}")
            return []

    def search_events(self,
                      query: str,
                      region: Optional[str] = None,
                      limit: int = 50) -> Tuple[List[Dict], Dict]:
        """
        Search events by keyword in name, description, or key figures.

        Args:
            query: Search query string
            region: Optional region filter
            limit: Maximum number of results

        Returns:
            Tuple of (events list, metadata dict)
        """
        # Build search conditions for full-text search
        search_conditions = [
            "event_name LIKE :query",
            "description LIKE :query",
            "key_figures LIKE :query"
        ]

        # Combine with OR for multiple fields
        search_clause = "(" + " OR ".join(search_conditions) + ")"

        conditions = [search_clause]
        params = {"query": f"%{query}%"}

        if region:
            conditions.append("region = :region")
            params["region"] = region

        where_clause = "WHERE " + " AND ".join(conditions)

        # Count total for pagination metadata
        count_query = text(f"""
            SELECT COUNT(*) as total FROM events
            {where_clause}
        """)

        # Get search results
        data_query = text(f"""
            SELECT * FROM events
            {where_clause}
            ORDER BY importance_level DESC, start_year ASC
            LIMIT :limit
        """)

        params["limit"] = limit

        try:
            with self.engine.connect() as conn:
                # Get total count
                count_result = conn.execute(count_query, params)
                total = count_result.fetchone()[0]

                # Get search results
                data_result = conn.execute(data_query, params)
                columns = data_result.keys()
                events = [dict(zip(columns, row)) for row in data_result]

                metadata = {
                    "total": total,
                    "limit": limit,
                    "query": query
                }

                return events, metadata
        except Exception as e:
            print(f"Error in search query: {e}")
            return [], {"total": 0, "limit": limit, "query": query}

    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics about the historical timeline data.

        Returns:
            Dictionary with various statistics
        """
        try:
            with self.engine.connect() as conn:
                # Total events count
                total_events_query = text("SELECT COUNT(*) as total FROM events")
                total_events = conn.execute(total_events_query).fetchone()[0]

                # Events by region
                region_query = text("""
                    SELECT region, COUNT(*) as count
                    FROM events
                    GROUP BY region
                """)
                region_stats = {}
                for row in conn.execute(region_query):
                    region_stats[row[0]] = row[1]

                # Events by category
                category_query = text("""
                    SELECT category, COUNT(*) as count
                    FROM events
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY count DESC
                """)
                category_stats = {}
                for row in conn.execute(category_query):
                    category_stats[row[0]] = row[1]

                # Year range
                year_range_query = text("""
                    SELECT MIN(start_year) as min_year, MAX(start_year) as max_year
                    FROM events
                """)
                year_result = conn.execute(year_range_query).fetchone()
                min_year, max_year = year_result[0], year_result[1]

                # Importance distribution
                importance_query = text("""
                    SELECT importance_level, COUNT(*) as count
                    FROM events
                    GROUP BY importance_level
                    ORDER BY importance_level
                """)
                importance_stats = {}
                for row in conn.execute(importance_query):
                    importance_stats[int(row[0])] = row[1]

                return {
                    "total_events": total_events,
                    "regions": region_stats,
                    "categories": category_stats,
                    "year_range": {
                        "min": min_year,
                        "max": max_year
                    },
                    "importance_distribution": importance_stats,
                    "average_importance": sum(k * v for k, v in importance_stats.items()) / total_events if total_events > 0 else 0
                }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                "error": str(e),
                "total_events": 0,
                "regions": {},
                "categories": {},
                "year_range": {"min": None, "max": None},
                "importance_distribution": {},
                "average_importance": 0
            }
