#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for civilizations timeline scraping - simplified version.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator

def main():
    """Test the civilizations timeline scraping."""
    print("Testing European civilizations timeline scraping...")

    try:
        # Initialize the timeline generator
        generator = TimelineGenerator(
            region="European",
            db_connection_string="postgresql://neondb_owner:npg_OoTY3udR5ElK@ep-aged-rice-ahgrgzju-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )

        # Test just the first few terms to avoid timeout
        print("Constants available:")
        print(f"ANCIENT_SEARCH_TERMS: {len(generator.ANCIENT_SEARCH_TERMS)} terms")
        print(f"MEDIEVAL_SEARCH_TERMS: {len(generator.MEDIEVAL_SEARCH_TERMS)} terms")
        print(f"EARLY_MODERN_SEARCH_TERMS: {len(generator.EARLY_MODERN_SEARCH_TERMS)} terms")

        # Test with just one period to avoid timeout
        print("\nTesting with first period only...")
        result = generator.scrape_civilizations_timeline(max_events_per_period=5)  # Limit events
        print(f"\nTest completed successfully!")
        print(f"Results: {result}")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())