#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to run the civilizations timeline scraping task.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator

def main():
    """Run the civilizations timeline scraping."""
    print("Starting European civilizations timeline scraping...")

    # Initialize the timeline generator
    generator = TimelineGenerator(
        region="European",
        db_connection_string="postgresql://neondb_owner:npg_OoTY3udR5ElK@ep-aged-rice-ahgrgzju-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

    # Run the scraping
    try:
        result = generator.scrape_civilizations_timeline()
        print(f"\nScraping completed successfully!")
        print(f"Results: {result}")
    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())