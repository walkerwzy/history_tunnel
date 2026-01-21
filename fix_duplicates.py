#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix problematic events and remove duplicates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator
from sqlalchemy import text

def main():
    """Fix problematic events and remove duplicates."""
    print("Fixing problematic events and removing duplicates...")

    # Initialize the timeline generator
    generator = TimelineGenerator(
        region="European",
        db_connection_string="sqlite:///data.db"
    )

    # Fix 1: Delete the erroneous 220 AD Han Chinese event
    print("\n1. Fixing erroneous 220 AD Han Chinese event...")
    try:
        with generator.db.engine.connect() as conn:
            conn.execute(text("DELETE FROM events WHERE id = :id"), {"id": 1084})
            conn.commit()
        print("   Deleted erroneous Han Chinese event (ID=1084)")
    except Exception as e:
        print(f"   Error deleting event: {e}")

    # Fix 2: Remove duplicate events based on event_name and start_year
    print("\n2. Finding and removing duplicate events...")

    # Find duplicates
    with generator.db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT event_name, start_year, COUNT(*) as cnt, MIN(id) as first_id
            FROM events
            WHERE region = 'European'
            GROUP BY event_name, start_year
            HAVING COUNT(*) > 1
            ORDER BY cnt DESC
        """))
        duplicates = result.fetchall()

    print(f"   Found {len(duplicates)} duplicate groups")

    deleted_count = 0
    for event_name, start_year, cnt, first_id in duplicates:
        print(f"   Processing: '{event_name}' ({start_year}) - {cnt} duplicates")

        # Delete all but the first one
        try:
            with generator.db.engine.connect() as conn:
                conn.execute(text("""
                    DELETE FROM events
                    WHERE event_name = :event_name
                    AND start_year = :start_year
                    AND id > :first_id
                """), {"event_name": event_name, "start_year": start_year, "first_id": first_id})
                conn.commit()
                deleted_count += 1
        except Exception as e:
            print(f"      Error removing duplicates: {e}")

    print(f"   Removed {len(duplicates) - deleted_count} duplicate events")

    # Fix 3: Fix remaining problematic titles
    print("\n3. Fixing remaining problematic event titles...")

    # Get all European events with problematic patterns
    with generator.db.engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, event_name, start_year, description
            FROM events
            WHERE region = 'European'
            AND (event_name LIKE '%的历史事件' OR event_name LIKE '%people的历史事件')
        """))
        problematic = result.fetchall()

    print(f"   Found {len(problematic)} events with problematic titles")

    # Mapping for problematic titles
    title_fixes = {
        "Babylonia": "巴比伦帝国",
        "Han Chinese": None,  # Should be deleted or moved to Chinese region
        "Assyrian people": "亚述人",
        "Mycenaean Greece": "迈锡尼希腊",
        "Wars of the Roses": "玫瑰战争",
        "Ottoman wars in Europe": "奥斯曼在欧洲的战争",
        "Baroque": "巴洛克艺术",
    }

    fixed_count = 0
    for event_id, event_name, start_year, description in problematic:
        if event_name in title_fixes:
            new_title = title_fixes[event_name]
            if new_title:
                # Update the title
                try:
                    with generator.db.engine.connect() as conn:
                        conn.execute(text("""
                            UPDATE events
                            SET event_name = :new_title, description = :new_desc
                            WHERE id = :id
                        """), {
                            "new_title": new_title,
                            "new_desc": f"公元{start_year}年，{new_title}在欧洲历史上具有重要意义，标志着一个时代的开始或转折点。",
                            "id": event_id
                        })
                        conn.commit()
                    fixed_count += 1
                except Exception as e:
                    print(f"      Error fixing event {event_id}: {e}")
            else:
                # Delete non-European events
                try:
                    with generator.db.engine.connect() as conn:
                        conn.execute(text("DELETE FROM events WHERE id = :id"), {"id": event_id})
                        conn.commit()
                    fixed_count += 1
                except Exception as e:
                    print(f"      Error deleting event {event_id}: {e}")

    print(f"   Fixed {fixed_count} problematic events")

    # Final statistics
    print("\n4. Final database statistics...")
    stats = generator.db.get_statistics()
    print(f"   Total events: {stats['total_events']}")
    print(f"   European events: {stats['events_by_region'].get('European', 0)}")
    print(f"   Chinese events: {stats['events_by_region'].get('Chinese', 0)}")

    print("\nFix completed!")

if __name__ == "__main__":
    exit(main())