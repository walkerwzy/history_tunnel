"""
Database Manager for Historical Timeline

This module handles SQLite database operations for storing
and querying historical events and periods.
"""

import os
from typing import List, Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseManager:
    """Manager for SQLite database operations."""

    def __init__(self, connection_string: str = None):
        """
        Initialize database manager.

        Args:
            connection_string: SQLite connection string (e.g., "sqlite:///data.db")
        """
        if connection_string is None:
            connection_string = "sqlite:///data.db"

        self.engine = create_engine(connection_string)

    def create_tables(self):
        """Create database tables if they don't exist."""
        create_events_table = """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name VARCHAR(255) NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER,
            key_figures TEXT,
            description TEXT,
            impact TEXT,
            category VARCHAR(100),
            region VARCHAR(100),
            importance_level INTEGER DEFAULT 5,
            source TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_periods_table = """
        CREATE TABLE IF NOT EXISTS periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_name VARCHAR(255) NOT NULL,
            start_year INTEGER NOT NULL,
            end_year INTEGER NOT NULL,
            period_type VARCHAR(50) NOT NULL,
            description TEXT,
            region VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_events_start_year ON events(start_year);",
            "CREATE INDEX IF NOT EXISTS idx_events_region ON events(region);",
            "CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);",
            "CREATE INDEX IF NOT EXISTS idx_events_importance ON events(importance_level);",
            "CREATE INDEX IF NOT EXISTS idx_periods_start_year ON periods(start_year);",
            "CREATE INDEX IF NOT EXISTS idx_periods_region ON periods(region);",
            "CREATE INDEX IF NOT EXISTS idx_periods_type ON periods(period_type);"
        ]

        with self.engine.connect() as conn:
            conn.execute(text(create_events_table))
            conn.execute(text(create_periods_table))
            for index_sql in create_indexes:
                conn.execute(text(index_sql))
            conn.commit()

        print("Database tables and indexes created successfully!")

    def insert_event(self, event: Dict) -> Optional[int]:
        """
        Insert a single event into the database.

        Args:
            event: Event dictionary with all required fields

        Returns:
            The ID of the inserted row, or None if failed
        """
        insert_query = text("""
            INSERT INTO events (
                event_name, start_year, end_year, key_figures,
                description, impact, category, region,
                importance_level, source
            )
            VALUES (
                :event_name, :start_year, :end_year, :key_figures,
                :description, :impact, :category, :region,
                :importance_level, :source
            )
        """)

        try:
            with self.engine.connect() as conn:
                conn.execute(insert_query, event)
                conn.commit()
                result = conn.execute(text("SELECT last_insert_rowid()"))
                return result.fetchone()[0]
        except SQLAlchemyError as e:
            print(f"Error inserting event {event.get('event_name')}: {e}")
            return None

    def update_event(self, event_id: int, event: Dict) -> bool:
        """
        Update an existing event in the database.

        Args:
            event_id: The ID of the event to update
            event: Event dictionary with fields to update

        Returns:
            True if update was successful, False otherwise
        """
        update_query = text("""
            UPDATE events SET
                event_name = :event_name,
                start_year = :start_year,
                end_year = :end_year,
                key_figures = :key_figures,
                description = :description,
                impact = :impact,
                category = :category,
                region = :region,
                importance_level = :importance_level,
                source = :source
            WHERE id = :id
        """)

        try:
            with self.engine.connect() as conn:
                conn.execute(update_query, {**event, "id": event_id})
                conn.commit()
                return True
        except SQLAlchemyError as e:
            print(f"Error updating event {event_id}: {e}")
            return False

    def insert_period(self, period: Dict) -> Optional[int]:
        """
        Insert a single period into the database.

        Args:
            period: Period dictionary with all required fields

        Returns:
            The ID of the inserted row, or None if failed
        """
        insert_query = text("""
            INSERT INTO periods (
                period_name, start_year, end_year, period_type,
                description, region
            )
            VALUES (
                :period_name, :start_year, :end_year, :period_type,
                :description, :region
            )
        """)

        try:
            with self.engine.connect() as conn:
                conn.execute(insert_query, period)
                conn.commit()
                result = conn.execute(text("SELECT last_insert_rowid()"))
                return result.fetchone()[0]
        except SQLAlchemyError as e:
            print(f"Error inserting period {period.get('period_name')}: {e}")
            return None

    def batch_insert_events(self, events: List[Dict]) -> int:
        """
        Insert multiple events at once.

        Args:
            events: List of event dictionaries

        Returns:
            Number of successfully inserted events
        """
        insert_query = text("""
            INSERT INTO events (
                event_name, start_year, end_year, key_figures,
                description, impact, category, region,
                importance_level, source
            )
            VALUES (
                :event_name, :start_year, :end_year, :key_figures,
                :description, :impact, :category, :region,
                :importance_level, :source
            )
        """)

        count = 0
        with self.engine.connect() as conn:
            for event in events:
                try:
                    conn.execute(insert_query, event)
                    count += 1
                except SQLAlchemyError as e:
                    print(f"Error inserting event {event.get('event_name')}: {e}")
            conn.commit()

        return count

    def batch_insert_periods(self, periods: List[Dict]) -> int:
        """
        Insert multiple periods at once.

        Args:
            periods: List of period dictionaries

        Returns:
            Number of successfully inserted periods
        """
        insert_query = text("""
            INSERT INTO periods (
                period_name, start_year, end_year, period_type,
                description, region
            )
            VALUES (
                :period_name, :start_year, :end_year, :period_type,
                :description, :region
            )
        """)

        count = 0
        with self.engine.connect() as conn:
            for period in periods:
                try:
                    conn.execute(insert_query, period)
                    count += 1
                except SQLAlchemyError as e:
                    print(f"Error inserting period {period.get('period_name')}: {e}")
            conn.commit()

        return count

    def get_events_by_time_range(self, start_year: int, end_year: int,
                               region: str = None, min_importance: int = None,
                               limit: int = 100) -> List[Dict]:
        """
        Query events within a time range.

        Args:
            start_year: Start year
            end_year: End year
            region: Filter by region (optional)
            min_importance: Filter by minimum importance level (optional)
            limit: Maximum number of results

        Returns:
            List of event dictionaries
        """
        base_query = """
            SELECT * FROM events
            WHERE start_year >= :start_year AND start_year <= :end_year
        """

        conditions = []
        params = {"start_year": start_year, "end_year": end_year, "limit": limit}

        if region:
            conditions.append("region = :region")
            params["region"] = region

        if min_importance:
            conditions.append("importance_level >= :min_importance")
            params["min_importance"] = min_importance

        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        base_query += " ORDER BY start_year ASC LIMIT :limit"

        query = text(base_query)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
        except SQLAlchemyError as e:
            print(f"Error querying events: {e}")
            return []

    def search_events_by_keyword(self, keyword: str, region: str = None,
                              limit: int = 50) -> List[Dict]:
        """
        Search events by keyword.

        Args:
            keyword: Search keyword
            region: Filter by region (optional)
            limit: Maximum number of results

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

        base_query += " ORDER BY importance_level DESC, start_year ASC LIMIT :limit"

        query = text(base_query)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
        except SQLAlchemyError as e:
            print(f"Error searching events: {e}")
            return []

    def get_periods_by_time_range(self, start_year: int, end_year: int,
                                region: str = None) -> List[Dict]:
        """
        Query periods within a time range.

        Args:
            start_year: Start year
            end_year: End year
            region: Filter by region (optional)

        Returns:
            List of period dictionaries
        """
        base_query = """
            SELECT * FROM periods
            WHERE start_year <= :end_year AND end_year >= :start_year
        """

        params = {"start_year": start_year, "end_year": end_year}

        if region:
            base_query += " AND region = :region"
            params["region"] = region

        base_query += " ORDER BY start_year ASC"

        query = text(base_query)

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
        except SQLAlchemyError as e:
            print(f"Error querying periods: {e}")
            return []

    def get_cross_regional_events(self, year: int, other_regions: List[str],
                                importance_threshold: int = 6) -> Dict[str, List[Dict]]:
        """
        Get events from other regions for a specific year/time period.

        Args:
            year: Reference year
            other_regions: List of regions to check
            importance_threshold: Minimum importance level

        Returns:
            Dictionary mapping region to list of events
        """
        placeholders = ','.join([f':region_{i}' for i in range(len(other_regions))])
        query = text(f"""
            SELECT * FROM events
            WHERE region IN ({placeholders})
            AND ABS(start_year - :year) <= 50
            AND importance_level >= :threshold
            ORDER BY start_year ASC
        """)

        params = {"year": year, "threshold": importance_threshold}
        for i, region in enumerate(other_regions):
            params[f"region_{i}"] = region

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                columns = result.keys()

                events_by_region = {}
                for row in result:
                    event = dict(zip(columns, row))
                    region = event['region']
                    if region not in events_by_region:
                        events_by_region[region] = []
                    events_by_region[region].append(event)

                return events_by_region
        except SQLAlchemyError as e:
            print(f"Error querying cross-regional events: {e}")
            return {}

    def get_statistics(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with statistics
        """
        queries = {
            "total_events": "SELECT COUNT(*) FROM events",
            "total_periods": "SELECT COUNT(*) FROM periods",
            "events_by_region": "SELECT region, COUNT(*) FROM events GROUP BY region",
            "periods_by_region": "SELECT region, COUNT(*) FROM periods GROUP BY region"
        }

        stats = {}
        with self.engine.connect() as conn:
            for key, query in queries.items():
                result = conn.execute(text(query))
                if "GROUP BY" in query:
                    stats[key] = {row[0]: row[1] for row in result}
                else:
                    stats[key] = result.fetchone()[0]

        return stats



