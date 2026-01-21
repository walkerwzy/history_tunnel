
# This script appends the scrape_civilizations_timeline method to timeline_generator.py
# It should be inserted after line 625 (Mongol Empire line)

import sys
import re

# Read the current file
with open('/Users/walker/Documents/_code/vibe/history/timeline_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the insertion point - after EARLY_MODERN_SEARCH_TERMS list
insertion_point = content.rfind('EARLY_MODERN_SEARCH_TERMS = [')

if insertion_point == -1:
    print("ERROR: Could not find insertion point in file!")
    sys.exit(1)

# Split content at insertion point
before = content[:insertion_point]
after = content[insertion_point:]

# Define the new method to insert
new_method = '''
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
        total_periods = len(ANCIENT_SEARCH_TERMS + MEDIEVAL_SEARCH_TERMS + EARLY_MODERN_SEARCH_TERMS)

        for i, search_terms in enumerate([ANCIENT_SEARCH_TERMS, MEDIEVAL_SEARCH_TERMS, EARLY_MODERN_SEARCH_TERMS]):
            if progress_callback:
                period_num = i + 1
                progress = period_num / total_periods * 100
                progress_callback(f"Processing period {period_num}/{total_periods} ({progress:.1f}%)")

            # Process each search term in the period
            for j, term in enumerate(search_terms):
                if progress_callback:
                    period_progress = (i * len(search_terms) + j) / (total_periods * len(ANCIENT_SEARCH_TERMS)) * 100
                    progress_callback(f" Processing term {j+1}/{len(search_terms)} {term}")

                # Search Wikipedia for term
                search_results = self.scraper.search_pages(term, limit=3)

                if not search_results:
                    print(f" No results found for '{term}'")
                    continue

                # Get the first result's page content (in English from English Wikipedia)
                page_content = self.scraper.get_page_content(search_results[0]['pageid'])

                if not page_content:
                    print(f" Failed to fetch page content for '{term}'")
                    continue

                # Directly extract structured events from the English Wikipedia content
                # Generate meaningful events based on page title and extract
                events = self._extract_events_from_wikipedia_page(
                    page_content['title'],
                    page_content.get('extract', ''),
                    'European',
                    max_events_per_period
                )

                if not events:
                    print(f" No events extracted from '{term}'")
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
                        print(f" Skipping duplicate: {event['event_name']} ({event['start_year']})")
                        continue

                    # Insert into database
                    self.db.insert_event(event)
                    events_inserted += 1

                print(f" {term}: {len(events)} events extracted")

            time.sleep(0.5)

        print(f"Total civilizations timeline events inserted: {events_inserted}")
        return {"events": events_inserted, "periods": 0}
'''

# Insert the new method after the get_statistics method
insertion_with_whitespace = "\\n" + new_method

# Write back
with open('/Users/walker/Documents/_code/vibe/history/timeline_generator.py', 'w', encoding='utf-8') as f:
    f.write(before + insertion_with_whitespace + after)

print("Method successfully added to timeline_generator.py!")
print(f"Insertion point: after line {insertion_point}")
