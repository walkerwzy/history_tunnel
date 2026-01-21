#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal test for database connection and constants.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator

def main():
    """Minimal test."""
    print("Testing minimal setup...")

    try:
        # Initialize the timeline generator
        generator = TimelineGenerator(
            region="European",
            db_connection_string="postgresql://neondb_owner:npg_OoTY3udR5ElK@ep-aged-rice-ahgrgzju-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )

        print("Generator initialized successfully")

        # Test constants
        print(f"ANCIENT_SEARCH_TERMS: {len(generator.ANCIENT_SEARCH_TERMS)} terms")
        print(f"MEDIEVAL_SEARCH_TERMS: {len(generator.MEDIEVAL_SEARCH_TERMS)} terms")
        print(f"EARLY_MODERN_SEARCH_TERMS: {len(generator.EARLY_MODERN_SEARCH_TERMS)} terms")

        # Test database connection
        stats = generator.db.get_statistics()
        print(f"Database stats: {stats}")

        print("All tests passed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())