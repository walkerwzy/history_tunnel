#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to verify the stored historical events in data.db.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator

def main():
    """Verify stored events."""
    print("Verifying stored historical events...")

    # Initialize the timeline generator
    generator = TimelineGenerator(
        region="European",
        db_connection_string="sqlite:///data.db"
    )

    # Get database statistics
    stats = generator.db.get_statistics()
    print(f"Database statistics: {stats}")

    # Get recent European events
    recent_events = generator.db.get_events_by_time_range(-1000, 2000, region="European", limit=10)
    print(f"\nRecent European events (showing first 10):")

    for i, event in enumerate(recent_events[:10], 1):
        print(f"{i}. {event['event_name']} ({event['start_year']})")
        print(f"   Category: {event['category']}, Importance: {event['importance_level']}")
        print(f"   Description: {event['description'][:100]}...")
        print(f"   Impact: {event['impact']}")
        print()

    print("Verification complete!")

if __name__ == "__main__":
    exit(main())