"""
Chinese Historical Timeline Generator

This script generates Chinese historical timeline data using the
encapsulated TimelineGenerator module.
"""

from timeline_generator import TimelineGenerator
import os
import dotenv

def main():
    """Generate Chinese historical timeline."""

    print("=" * 60)
    print("中国历史大事年表生成器")
    print("=" * 60)

    dotenv.load_dotenv(override=True)
    model = os.getenv("OPENAI_MODEL")

    # 初始化中国时间轴生成器
    generator = TimelineGenerator(region="Chinese", llm_model=model)

    # 真正爬取中国历史数据（从 Wikipedia 抓取）
    print("\n[1] 真正爬取中国历史数据（从 Wikipedia 抓取）...")
    result = generator.scrape_full_timeline(
        classical_years=50,      # 古代时期（-1000 到 500）：每50年采样一次
        medieval_years=25,       # 中世纪（500 到 1500）：每25年采样一次
        early_modern_years=12,   # 近代早期（1500 到 1800）：每12年采样一次
        nineteenth_century_years=10,  # 19世纪（1800 到 1900）：每10年采样一次
        twentieth_century_years=5,    # 20世纪（1900 到 2000）：每5年采样一次
        twenty_first_century_years=1,   # 21世纪（2000 到 2026）：每年采样一次
        min_importance=5,    # 最低重要性等级
        force_refresh=False,  # 不强制刷新，使用缓存
        progress_callback=lambda x: print(f"  {x}")
    )
    print(f"生成结果: {result['events']} 个事件, {result['periods']} 个时期")

    # 查询唐朝时期（618-907年）
    print("\n[2] 查询唐朝时期历史事件...")
    tang_dynasty = generator.get_timeline(
        start_year=618,
        end_year=907,
        min_importance=6,
        limit=20
    )
    print(f"找到 {len(tang_dynasty)} 个事件")
    for event in tang_dynasty[:5]:
        print(f"  - {event['event_name']} ({event['start_year']}) "
            f"[{event.get('category', 'N/A')}]")

    # 查询宋朝时期（960-1279年）
    print("\n[3] 查询宋朝时期历史事件...")
    song_dynasty = generator.get_timeline(
        start_year=960,
        end_year=1279,
        min_importance=6,
        limit=20
    )
    print(f"找到 {len(song_dynasty)} 个事件")
    for event in song_dynasty[:5]:
        print(f"  - {event['event_name']} ({event['start_year']})")

    # 搜索"统一"相关事件
    print("\n[4] 搜索统一相关事件...")
    unification_events = generator.search_events("unification", limit=10)
    print(f"找到 {len(unification_events)} 个事件")
    for event in unification_events[:3]:
        print(f"  - {event['event_name']} ({event['start_year']})")

    # 查询明清时期（1368-1911年）
    print("\n[5] 查询明清时期历史事件...")
    ming_qing = generator.get_timeline(
        start_year=1368,
        end_year=1911,
        min_importance=7,
        limit=25
    )
    print(f"找到 {len(ming_qing)} 个事件")
    for event in ming_qing[:5]:
        print(f"  - {event['event_name']} ({event['start_year']})")

    # 与欧洲历史对比（同一时间）
    print("\n[6] 跨地区对比：唐朝时期与欧洲对比...")
    cross_events = generator.get_cross_regional_view(
        year=756,  # 唐朝中期
        other_regions=["European"],
        importance_threshold=7
    )
    for region, events in cross_events.items():
        print(f"  {region}: {len(events)} 个事件")
        for event in events[:3]:
            print(f"    - {event['event_name']} ({event['start_year']})")

    # 搜索"改革"相关事件
    print("\n[7] 搜索改革相关事件...")
    reform_events = generator.search_events("reform", limit=10)
    print(f"找到 {len(reform_events)} 个事件")
    for event in reform_events[:3]:
        print(f"  - {event['event_name']} ({event['start_year']})")

    # 获取统计数据
    print("\n[8] 数据库统计信息...")
    stats = generator.get_statistics()
    print(f"  总事件数: {stats.get('total_events', 0)}")
    print(f"  总时期数: {stats.get('total_periods', 0)}")
    if 'events_by_region' in stats:
        print(f"  按地区统计: {stats['events_by_region']}")
    if 'periods_by_region' in stats:
        print(f"  按地区统计时期: {stats['periods_by_region']}")

    print("\n" + "=" * 60)
    print("中国历史数据生成完成！")


if __name__ == "__main__":
    main()
