#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to run the civilizations timeline scraping task - limited version.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator

def main():
    """Run the civilizations timeline scraping with limits."""
    print("Starting limited European civilizations timeline scraping...")

    # Initialize the timeline generator
    generator = TimelineGenerator(
        region="European",
        db_connection_string="sqlite:///data.db"
    )

    # Run the scraping with limits
    try:
        # Process all three periods with 3 events max per term
        print("Processing all periods (Ancient, Medieval, Early Modern) with 3 events max per term...")
        result = generator.scrape_civilizations_timeline_limited(max_events_per_term=3)
        print(f"\nLimited scraping completed successfully!")
        print(f"Results: {result}")

        # Check final stats
        stats = generator.db.get_statistics()
        print(f"\nFinal database stats: {stats}")

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())