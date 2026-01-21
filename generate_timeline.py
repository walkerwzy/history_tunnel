"""
European Timeline Generator

This script demonstrates how to use the encapsulated modules
to generate European historical timeline data.
"""

from timeline_generator import TimelineGenerator


def main():
    """主函数：生成欧洲历史大事年表"""

    print("=" * 60)
    print("欧洲历史大事年表生成器")
    print("=" * 60)

    # 初始化欧洲时间轴生成器
    generator = TimelineGenerator(region="European")

    # 生成真实历史数据
    print("\n[生成] 从Wikipedia抓取欧洲历史数据...")
    result = generator.scrape_full_timeline(
        classical_years=100,      # 古典时期：每100年
        medieval_years=50,         # 中世纪：每50年
        early_modern_years=25,     # 近代早期：每25年
        nineteenth_century_years=10, # 19世纪：每10年
        twentieth_century_years=5,    # 20世纪：每5年
        twenty_first_century_years=1, # 21世纪：每年
        min_importance=6,          # 只保留重要事件
        progress_callback=lambda x: print(f"  {x}")
    )
    print(f"抓取结果: {result['events']} 个事件")

    # 查询时间轴数据
    print("\n[查询] 获取1900-2026年的历史事件...")
    timeline = generator.get_timeline(
        start_year=1900,
        end_year=2026,
        min_importance=7,  # 只显示重要事件
        limit=20
    )
    print(f"找到 {len(timeline)} 个事件")
    for event in timeline[:5]:
        print(f"  - {event['event_name']} ({event['start_year']}) "
            f"[{event.get('category', 'N/A')}] 重要性: {event['importance_level']}")

    # 关键词搜索
    print("\n[搜索] 搜索包含 'war' 的事件...")
    war_events = generator.search_events(keyword="war", limit=10)
    print(f"找到 {len(war_events)} 个事件")
    for event in war_events[:3]:
        print(f"  - {event['event_name']} ({event['start_year']})")

    # 获取统计数据
    print("\n[统计] 数据库统计信息...")
    stats = generator.get_statistics()
    print(f"  总事件数: {stats.get('total_events', 0)}")
    print(f"  总时期数: {stats.get('total_periods', 0)}")
    if 'events_by_region' in stats:
        print(f"  按地区统计: {stats['events_by_region']}")

    # 跨地区对比
    print("\n[跨地区] 查看1945年的其他地区事件...")
    cross_events = generator.get_cross_regional_view(
        year=1945,
        other_regions=["Chinese"],
        importance_threshold=7
    )
    for region, events in cross_events.items():
        print(f"  {region}: {len(events)} 个事件")
        for event in events[:3]:
            print(f"    - {event['event_name']} ({event['start_year']})")

    print("\n" + "=" * 60)
    print("生成完成！")


if __name__ == "__main__":
    main()
