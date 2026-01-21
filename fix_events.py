#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to fix event titles and descriptions in the database.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from timeline_generator import TimelineGenerator

def main():
    """Fix event titles and descriptions."""
    print("Fixing event titles and descriptions...")

    # Initialize the timeline generator
    generator = TimelineGenerator(
        region="European",
        db_connection_string="sqlite:///data.db"
    )

    # Get recent European events to analyze the problems
    recent_events = generator.db.get_events_by_time_range(-1000, 2000, region="European", limit=50)
    print(f"Analyzing {len(recent_events)} recent European events...")

    # Show examples of problematic titles and descriptions
    print("\nExamples of current problematic events:")
    for i, event in enumerate(recent_events[:10], 1):
        print(f"{i}. Title: '{event['event_name']}'")
        print(f"   Description (first 50 chars): '{event['description'][:50]}...'")
        print(f"   Impact: '{event['impact']}'")
        print()

    # Now implement the fix
    print("Starting to fix events...")

    # Get all European events
    all_european_events = generator.db.get_events_by_time_range(-2000, 2000, region="European", limit=1000)
    print(f"Found {len(all_european_events)} European events to process")

    fixed_count = 0
    for event in all_european_events:
        # Check if this is one of the newly added events that need fixing
        event_name = event['event_name']

        # Skip events that already have proper Chinese names
        if not any(pattern in event_name for pattern in ["年", "时期", "civilization", "period", "Empire", "War", "Age"]):
            continue

        # Try to find corresponding raw content in cache
        # For now, let's create a simplified fix based on the event name pattern

        # Extract the original title from the event name
        if "年" in event_name:
            # Pattern like "公元前753年Ancient Rome"
            parts = event_name.split("年")
            if len(parts) >= 2:
                original_title = parts[1].strip()
            else:
                continue
        else:
            continue

        # Generate proper Chinese title and description
        chinese_title, chinese_description = generate_proper_chinese_content(original_title, event['description'], event['start_year'])

        if chinese_title and chinese_description:
            # Update the event in database
            update_data = {
                "event_name": chinese_title,
                "description": chinese_description,
                "start_year": event['start_year'],
                "end_year": event['end_year'],
                "key_figures": event['key_figures'],
                "impact": event['impact'],
                "category": event['category'],
                "region": event['region'],
                "importance_level": event['importance_level'],
                "source": event['source']
            }

            # Actually update the event in database
            success = generator.db.update_event(event['id'], update_data)
            if success:
                print(f"Updated: '{event_name}' -> '{chinese_title}'")
                print(f"Description: '{event['description'][:30]}...' -> '{chinese_description[:30]}...'")
                fixed_count += 1
            else:
                print(f"Failed to update event {event['id']}: {event_name}")

    print(f"\nWould fix {fixed_count} events")
    print("Note: Database update functionality needs to be implemented")

def generate_proper_chinese_content(original_title, english_description, year):
    """
    Generate proper Chinese title and description based on historical expertise.
    """
    # Mapping of common English titles to proper Chinese event names
    title_mappings = {
        "Ancient Greece": "古希腊文明的诞生",
        "Ancient Rome": "罗马王国的建立",
        "Minoan civilization": "米诺斯文明的兴起",
        "Mycenaean civilization": "迈锡尼文明的繁荣",
        "Phoenicians": "腓尼基人的海上贸易",
        "Canaan": "迦南地区的早期文明",
        "Hittites": "赫梯帝国的扩张",
        "Assyrians": "亚述帝国的崛起",
        "Babylonians": "巴比伦帝国的辉煌",
        "Classical Greece": "古典希腊的黄金时代",
        "Hellenistic period": "希腊化时期的扩张",
        "Roman Republic": "罗马共和国的建立",
        "Carthage": "迦太基的兴盛",
        "Byzantine Empire": "拜占庭帝国的延续",
        "Viking Age": "维京时代的开始",
        "Islamic Golden Age": "伊斯兰黄金时代的曙光",
        "Holy Roman Empire": "神圣罗马帝国的建立",
        "Crusades": "十字军东征的发起",
        "Mongol Empire": "蒙古帝国的欧洲扩张",
        "Song Dynasty (Chinese influence)": "宋朝对欧洲的影响",
        "Black Death": "黑死病的肆虐",
        "Hundred Years' War": "百年战争的爆发",
        "Ottoman Empire": "奥斯曼帝国的崛起",
        "Renaissance": "文艺复兴的开端",
        "Hanseatic League": "汉萨同盟的形成",
        "Caliphate": "哈里发的扩张",
        "War of the Roses": "玫瑰战争的开始",
        "Italian Renaissance": "意大利文艺复兴",
        "Age of Discovery": "地理大发现的时代",
        "Reformation": "宗教改革的兴起",
        "Scientific Revolution": "科学革命的开始",
        "Age of Enlightenment": "启蒙运动的兴起",
        "Thirty Years' War": "三十年战争的爆发",
        "Ottoman wars": "奥斯曼战争的持续",
        "Baroque period": "巴洛克艺术时期",
        "Colonialism": "殖民主义的兴起",
        "Mercantilism": "重商主义的盛行"
    }

    chinese_title = title_mappings.get(original_title, f"{original_title}的历史事件")

    # Generate Chinese description based on the year and context
    if year < 0:
        time_context = f"公元前{abs(year)}年"
    else:
        time_context = f"{year}年"

    # Create a meaningful Chinese description
    chinese_descriptions = {
        "Ancient Greece": f"{time_context}，古希腊文明开始在爱琴海地区崛起，奠定了西方哲学和民主的基础。",
        "Ancient Rome": f"{time_context}，罗马王国在意大利半岛建立，标志着罗马文明的开端。",
        "Minoan civilization": f"{time_context}，米诺斯文明在克里特岛达到鼎盛，成为欧洲最早的青铜时代文明。",
        "Classical Greece": f"{time_context}，古典希腊进入黄金时代，产生了众多哲学家和科学家。",
        "Roman Republic": f"{time_context}，罗马从王国转变为共和国，开启了罗马的扩张时代。",
        "Renaissance": f"{time_context}，文艺复兴运动在意大利兴起，标志着欧洲从中世纪向现代的转型。",
        "Scientific Revolution": f"{time_context}，科学革命开始改变人们对自然界的认识。",
        "Age of Enlightenment": f"{time_context}，启蒙运动强调理性思维，影响了欧洲的思想发展。",
    }

    chinese_description = chinese_descriptions.get(original_title,
        f"{time_context}，{original_title}在欧洲历史上具有重要意义，标志着一个时代的开始或转折点。")

    return chinese_title, chinese_description

if __name__ == "__main__":
    exit(main())