#!/usr/bin/env python3
"""
将 euro_history3.json 中的100个欧洲事件按照相同的规则插入 periods 表
"""

import json
import sqlite3
import re
from datetime import datetime

def parse_year_range(year_str):
    """
    解析年份范围字符串，返回 (start_year, end_year)
    支持: "3000 BC - 1450", "-3000 to -1450", "753 BC - 509 BC", "330 AD - 1453 AD"
    """
    year_str = year_str.strip()
    
    if 'to' in year_str.lower():
        parts = year_str.split('to')
    else:
        parts = year_str.split('-')
    
    if len(parts) < 2:
        raise ValueError(f"无法解析年份范围: {year_str}")
    
    start_str = parts[0].strip()
    end_str = parts[-1].strip()
    
    start_year = parse_single_year(start_str)
    end_year = parse_single_year(end_str)
    
    return start_year, end_year

def parse_single_year(year_str):
    """
    解析单个年份，支持 BC/AD
    """
    year_str = year_str.strip()
    
    # 处理特殊情况
    if year_str.lower() == 'present':
        return 2026  # 使用当前年份
    
    # 提取数字部分
    num_match = re.search(r'(\d+)', year_str)
    if not num_match:
        raise ValueError(f"无法从 '{year_str}' 提取年份")
    
    year_num = int(num_match.group(1))
    
    # 处理 BC（公元前）- 转换为负数
    if 'bc' in year_str.lower():
        return -year_num
    
    # AD 或其他情况保持为正数
    return year_num

def determine_period_type(period_name, period_name_cn, start_year):
    """
    根据历史学专业知识推断 period_type
    """
    # 连续时期（有明确起止时间的朝代、帝国等）
    continuous_patterns = [
        r'civilization',  # 文明
        r'Empire',  # 帝国
        r'Kingdom',  # 王国
        r'Republic',  # 共和国
        r'Age',  # 时代
        r'Renaissance',  # 复兴
        r'Golden Age',  # 黄金时代
        r'Discovery',  # 大航海时代
        r'Industrial Revolution', # 工业革命
        r'Migration Period',  # 民族大迁徙
        r'Contemporary Era' # 当代
    ]
    
    # 独立事件（特定时间点的事件）
    independent_patterns = [
        r'Crusade',  # 十字军东征
        r'War',  # 战争
        r'Battle',  # 战役
        r'Revolution',  # 革命
        r'Movement', # 运动
        r'Enlightenment',  # 启蒙运动
        r'Reformation',  # 宗教改革
        r'Treaty', # 条约
    ]
    
    # 特殊独立事件
    special_independent = [
        'Black Death',  # 黑死病
        'Reformation', # 宗教改革
        'Proclamation', # 宣言、宣告
        'Reform',  # 改革
        'Scientific Revolution',  # 科学革命
        'Olympic Games',  # 奥林匹克运动会
        'Marathon Battle',  # 马拉松战役
        'Parthenon Construction',  # 帕特农神庙建成
        'Socrates Death',  # 苏格拉底之死
        'Crossing Rubicon',  # 跨越卢比孔河
        'Rome Founding',  # 罗马建城
    ]
    
    # 检查特殊词汇
    for keyword in special_independent:
        if keyword.lower() in period_name.lower() or keyword.lower() in period_name_cn.lower():
            return 'independent'
    
    # 检查独立事件模式
    for pattern in independent_patterns:
        if re.search(pattern, period_name, re.IGNORECASE) or re.search(pattern, period_name_cn, re.IGNORECASE):
            return 'independent'
    
    # 检查连续时期模式
    for pattern in continuous_patterns:
        if re.search(pattern, period_name, re.IGNORECASE) or re.search(pattern, period_name_cn, re.IGNORECASE):
            return 'continuous'
    
    # 根据时间长度判断 - 超过50年的通常是连续时期
    if 'start_year' in locals() and 'end_year' in locals():
        duration = end_year - start_year
        if duration > 50:
            return 'continuous'
    
    # 默认为连续时期
    return 'continuous'

def main():
    """
    插入 euro_history3.json 中的100个欧洲历史时期到 periods 表
    按照与 eura_history2.json 相同的规则
    """
    
    print("📂 加载 euro_history3.json...")
    
    # 修正文件路径
    file_path = 'cache/European/euro_history3.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        print("请确认 euro_history3.json 文件存在于 cache/European/ 目录中")
        return
    
    print(f"📊 共找到 {len(events)} 个历史时期")

    # 连接数据库
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    periods_inserted = 0
    duplicates_found = 0

    for period_name, period_data in events.items():
        # period_name 是时期名称，period_data 是包含时期信息的字典
        period_name_cn = period_data.get('period_name_cn', period_name)  # 中文名
        
        # 解析年份范围
        year_str = period_data.get('year', '')
        if year_str:
            start_year, end_year = parse_year_range(year_str)
        else:
            # 如果没有年份信息，跳过这个时期
            print(f"⚠️ 跳过没有年份信息的时期: {period_name}")
            continue
        
        # 确定时期类型
        period_type = determine_period_type(period_name, period_name_cn, start_year)
        
        # 检查时期是否已存在
        cursor.execute('''
            SELECT id FROM periods
            WHERE period_name = ? AND start_year = ?
        ''', (period_name, start_year))
        
        if not cursor.fetchone():
            # 插入新时期到 periods 表
            print(f"✅ 插入时期: {period_name} ({start_year}-{end_year}) [{period_type}]")
            
            cursor.execute('''
                INSERT INTO periods (
                    period_name, start_year, end_year, 
                    period_type, region, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                period_name,         # period_name
                start_year,          # start_year
                end_year,            # end_year
                period_type,         # period_type
                'European',          # region
                period_data.get('description', '')   # description
            ))
            
            periods_inserted += 1
        else:
            print(f"⏭️ 时期已存在: {period_name} ({start_year})")
            duplicates_found += 1

    conn.commit()
    conn.close()

    print("\n🎉 数据插入完成！")
    print(f"✅ 新增时期: {periods_inserted} 个")
    print(f"⏭️ 重复时期: {duplicates_found} 个")
    
    # 显示数据库统计
    print("\n📊 数据库统计：")
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE region = "European";')
    total_european = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE region = "Chinese";')
    total_chinese = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE period_type = "continuous";')
    total_continuous = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE period_type = "independent";')
    total_independent = cursor.fetchone()[0]
    
    print(f"🇪🇺 欧洲时期总数: {total_european}")
    print(f"🇨🇳 中国时期总数: {total_chinese}")
    print(f"📈 连续时期数: {total_continuous}")
    print(f"🎯 独立事件数: {total_independent}")
    
    conn.close()

if __name__ == "__main__":
    main()