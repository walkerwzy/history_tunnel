#!/usr/bin/env python3
"""
将 euro_history.json 的数据插入到数据库中
根据历史学专业知识自动推断 period_type
"""

import json
import sqlite3
import re
from datetime import datetime

def parse_year_range(year_str):
    """
    解析年份范围字符串，返回 (start_year, end_year)
    支持: "3000 BC - 500 BC", "330 - 1453", "793 - 1066"
    """
    parts = year_str.split('-')
    if len(parts) != 2:
        raise ValueError(f"无法解析年份范围: {year_str}")

    start_str, end_str = parts[0].strip(), parts[1].strip()

    # 处理 BC 年份（负数）
    def parse_year(s):
        s = s.strip()
        if 'BC' in s.upper():
            return -int(s.upper().replace('BC', '').strip())
        else:
            return int(s.split()[0])  # 取第一个数字，忽略其他说明

    return parse_year(start_str), parse_year(end_str)

def determine_period_type(period_name, period_name_cn):
    """
    根据历史学专业知识推断 period_type
    """
    continuous_patterns = [
        # 文明/帝国/王国类
        r'civilization',  # 文明
        r'Empire',  # 帝国
        r'Kingdom',  # 王国
        r'Republic',  # 共和国
        r'Dynasty',  # 朝代
        r'Age',  # 时代

        # 长期历史时期
        r'Ancient Greece',  # 古希腊
        r'Ancient Rome',  # 古罗马
        r'Classical',  # 古典时期
        r'Hellenistic',  # 希腊化时代
        r'Medieval',  # 中世纪
        r'Renaissance',  # 文艺复兴
        r'Golden Age',  # 黄金时代
        r'Discovery',  # 大航海时代
        r'Mercantilism',  # 重商主义时代

        # 中文时期标识
        r'文明',  # 文明
        r'帝国',  # 帝国
        r'时期',  # 时期
        r'时代',  # 时代
        r'朝',  # 朝代
        r'王政',  # 王政
        r'共和国',  # 共和国
    ]

    independent_patterns = [
        # 特定事件/运动/战争类
        r'Crusade',  # 十字军东征
        r'War',  # 战争
        r'Battle',  # 战役
        r'Revolution',  # 革命（特定事件）
        r'Movement',  # 运动
        r'Enlightenment',  # 启蒙运动

        # 中文特定事件
        r'战争',  # 战争
        r'东征',  # 东征
        r'革命',  # 革命
        r'运动',  # 运动
        r'黑死病',  # 黑死病
    ]

    # 特殊处理
    if 'Black Death' in period_name or '黑死病' in period_name_cn:
        return 'independent'

    # 检查 independent 模式
    for pattern in independent_patterns:
        if re.search(pattern, period_name, re.IGNORECASE):
            return 'independent'

    # 默认为 continuous
    return 'continuous'

def insert_periods(conn, data):
    """
    插入时期数据
    """
    cursor = conn.cursor()

    for period_name, period_data in data.items():
        period_name_cn = period_data.get('period_name_cn', period_name)
        region = period_data.get('region', 'European')
        year_str = period_data.get('year', '')

        try:
            start_year, end_year = parse_year_range(year_str)
        except ValueError as e:
            print(f"⚠️  跳过时期 {period_name}: {e}")
            continue

        # 确定时期类型
        period_type = determine_period_type(period_name, period_name_cn)
        description = period_name_cn  # 使用中文时期名作为描述

        # 检查是否已存在
        cursor.execute('''
            SELECT id FROM periods
            WHERE period_name = ? AND start_year = ? AND end_year = ?
        ''', (period_name, start_year, end_year))

        if cursor.fetchone():
            print(f"⏭️  时期已存在: {period_name} ({start_year} - {end_year})")
            continue

        # 插入
        cursor.execute('''
            INSERT INTO periods (period_name, start_year, end_year, period_type, description, region)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (period_name, start_year, end_year, period_type, description, region))

        print(f"✅ 插入时期: {period_name_cn} ({start_year} - {end_year}) [{period_type}]")

    conn.commit()
    print(f"\n✅ 完成！共插入时期数据")

def insert_events(conn, data):
    """
    插入事件数据
    """
    cursor = conn.cursor()

    total_events = 0
    inserted_count = 0

    for period_name, period_data in data.items():
        events = period_data.get('events', [])

        for event in events:
            total_events += 1
            event_name = event.get('event_name')
            start_year = event.get('start_year')
            end_year = event.get('end_year') or start_year  # 如果 end_year 为空，使用 start_year
            key_figures = event.get('key_figures', '')
            description = event.get('description', '')
            impact = event.get('impact', '')
            category = event.get('category', '')
            importance_level = event.get('importance_level', 5)
            region = event.get('region', 'European')
            source = event.get('source', '')

            # 检查是否已存在（根据事件名称和起始年份）
            cursor.execute('''
                SELECT id FROM events
                WHERE event_name = ? AND start_year = ?
            ''', (event_name, start_year))

            if cursor.fetchone():
                print(f"⏭️  事件已存在: {event_name} ({start_year})")
                continue

            # 插入
            cursor.execute('''
                INSERT INTO events (event_name, start_year, end_year, key_figures,
                                     description, impact, category, region, importance_level, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_name, start_year, end_year, key_figures, description,
                  impact, category, region, importance_level, source))

            inserted_count += 1
            print(f"✅ 插入事件: {event_name} ({start_year}) [{category}]")

    conn.commit()
    print(f"\n✅ 完成！共处理 {total_events} 个事件，插入 {inserted_count} 个新事件")

def main():
    # 加载 JSON 数据
    print("📂 加载 euro_history.json...")
    with open('cache/European/euro_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📊 找到 {len(data)} 个时期\n")

    # 连接数据库
    print("🔌 连接数据库 data.db...")
    conn = sqlite3.connect('data.db')

    # 插入时期
    print("\n" + "="*60)
    print("📝 开始插入时期数据...")
    print("="*60)
    insert_periods(conn, data)

    # 插入事件
    print("\n" + "="*60)
    print("📝 开始插入事件数据...")
    print("="*60)
    insert_events(conn, data)

    # 关闭连接
    conn.close()
    print("\n" + "="*60)
    print("🎉 所有数据插入完成！")
    print("="*60)

if __name__ == '__main__':
    main()
