"""
测试增强的数据库查询功能
"""

from enhanced_database_manager import EnhancedDatabaseManager
from nl_query_engine import create_sql_query_engine

# 初始化增强数据库管理器
print("=" * 60)
print("测试增强数据库管理器")
print("=" * 60)

enhanced_db = EnhancedDatabaseManager("sqlite:///data.db")

# 测试1: 分页查询（时间轴滚动）
print("\n1. 测试分页查询（时间轴滚动功能）")
print("-" * 60)
events_page1, meta1 = enhanced_db.get_events_paginated(
    start_year=1900,
    end_year=2000,
    limit=10,
    offset=0
)
print(f"第一页: {len(events_page1)} 个事件")
print(f"元数据: {meta1}")
if events_page1:
    for event in events_page1[:3]:
        print(f"  - {event['event_name']} ({event['start_year']}) [重要性: {event['importance_level']}]")

events_page2, meta2 = enhanced_db.get_events_paginated(
    start_year=1900,
    end_year=2000,
    limit=10,
    offset=10
)
print(f"\n第二页: {len(events_page2)} 个事件")
print(f"元数据: {meta2}")

# 测试2: 按重要性筛选
print("\n2. 测试按重要性筛选")
print("-" * 60)
important_events = enhanced_db.get_events_by_importance(
    importance_threshold=8,
    limit=5
)
print(f"重要性 >= 8 的事件（共 {len(important_events)} 个）:")
for event in important_events:
    print(f"  - {event['event_name']} ({event['start_year']}) [重要性: {event['importance_level']}]")

# 测试3: 某年份附近的事件
print("\n3. 测试某年份附近的事件")
print("-" * 60)
around_events = enhanced_db.get_events_around_year(
    year=1945,
    years_before=10,
    years_after=10,
    limit=10
)
print(f"1945年附近 ±10 年的事件（共 {len(around_events)} 个）:")
for event in around_events[:5]:
    print(f"  - {event['event_name']} ({event['start_year']})")

# 测试4: 跨地区对比
print("\n4. 测试跨地区对比")
print("-" * 60)
comparison = enhanced_db.get_cross_regional_comparison(
    year=1945,
    regions=["European", "Chinese"],
    years_around=50,
    importance_threshold=7
)
for region, data in comparison.items():
    print(f"\n{region}:")
    print(f"  总事件数: {data['statistics']['total_events']}")
    print(f"  最高重要性: {data['statistics']['highest_importance']}")
    print(f"  分类统计: {data['statistics']['categories']}")
    print(f"  重要事件示例:")
    for event in data['events'][:3]:
        print(f"    - {event['event_name']} ({event['start_year']}) [重要性: {event['importance_level']}]")

# 测试5: 高级搜索
print("\n5. 测试高级搜索（多条件）")
print("-" * 60)
advanced_results = enhanced_db.search_events_advanced(
    keyword="战争" if False else "war",
    category="军事" if False else None,
    min_importance=7,
    start_year=1900,
    end_year=2000,
    limit=5
)
print(f"搜索结果（共 {len(advanced_results)} 个）:")
for event in advanced_results:
    print(f"  - {event['event_name']} ({event['start_year']}) [分类: {event.get('category')}, 重要性: {event['importance_level']}]")

# 测试6: 时间线统计
print("\n6. 测试时间线统计")
print("-" * 60)
stats = enhanced_db.get_timeline_statistics(start_year=1900, end_year=2000)
print(f"总事件数: {stats['total_events']}")
print(f"平均重要性: {stats['avg_importance']:.2f}")
print(f"最高重要性: {stats['max_importance']}")
print(f"最低重要性: {stats['min_importance']}")
print(f"\n按分类统计:")
for category, count in stats['by_category'].items():
    print(f"  - {category}: {count}")

# 测试7: 事件最多的年份
print("\n7. 测试事件最多的年份")
print("-" * 60)
top_years = enhanced_db.get_years_with_most_events(
    min_importance=6,
    limit=5
)
print(f"事件最多的年份:")
for year_info in top_years:
    print(f"  - {year_info['start_year']}: {year_info['event_count']} 个事件 (平均重要性: {year_info['avg_importance']:.2f})")

print("\n" + "=" * 60)
print("增强数据库管理器测试完成！")
print("=" * 60)

# 测试自然语言查询引擎
print("\n" + "=" * 60)
print("测试自然语言查询引擎")
print("=" * 60)

try:
    nl_engine = create_sql_query_engine("sqlite:///data.db")

    print("\n可用表:")
    tables = nl_engine.get_available_tables()
    for table in tables:
        print(f"  - {table}")

    print("\n所有表的 Schema:")
    print(nl_engine.get_all_schemas())

    # 测试自然语言查询
    queries = [
        "Show me the most important events in the 20th century",
        "How many events are from China?",
        "List the top 5 most important events",
    ]

    print("\n自然语言查询测试:")
    for i, query in enumerate(queries, 1):
        print(f"\n查询 {i}: {query}")
        print("-" * 60)
        result = nl_engine.query(query)
        print(f"回答: {result}")

except Exception as e:
    print(f"\n自然语言查询引擎初始化失败: {e}")
    print("这可能是因为 OPENAI_API_KEY 未设置")

print("\n" + "=" * 60)
print("所有测试完成！")
print("=" * 60)
