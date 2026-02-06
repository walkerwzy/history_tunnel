#!/usr/bin/env python3
"""
将 euro_history4.json 中的宗教层面欧洲历史事件导入数据库
"""

import json
import sqlite3
import re
from datetime import datetime

def parse_year_range(year_str):
    """解析年份范围字符串"""
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
    """解析单个年份"""
    year_str = year_str.strip()
    
    # 处理特殊情况
    if year_str.lower() == 'present':
        return 2026
    
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

def determine_period_type(period_name, period_name_cn, start_year, end_year=None):
    """
    根据历史学专业知识推断 period_type
    """
    # 连续时期（朝代、帝国等）
    continuous_patterns = [
        r'civilization',  # 文明
        r'empire',  # 帝国
        r'kingdom',  # 王国
        r'republic',  # 共和国
        r'period',  # 时期
        r'church',  # 教会
        r'reformation',  # 宗教改革
        r'crusade',  # 十字军
    ]
    
    # 独立事件（特定时间点的事件）
    independent_patterns = [
        r'war',  # 战争
        r'battle',  # 战役
        r'revolution',  # 革命
        r'rebellion',  # 叛乱
        r'uprising',  # 起义
        r'council',  # 会议
    ]
    
    # 特殊独立事件
    special_independent = [
        'exodus',  # 出埃及
        'crucifixion',  # 钉十字架
        'resurrection',  # 复活
        'conversion',  # 改信
        'schism',  # 分裂
        'reformation',  # 改革
        'holocaust',  # 大屠杀
        'council',  # 会议
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
    duration = end_year - start_year
    if duration > 50:
        return 'continuous'
    
    # 默认为连续时期
    return 'continuous'

def main():
    """
    导入 euro_history4.json 中的宗教历史数据到数据库
    """
    print("📂 加载 euro_history4.json...")
    
    file_path = 'cache/European/euro_history4.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            periods_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        return
    
    print(f"📊 共找到 {len(periods_data)} 个宗教历史时期")

    # 连接数据库
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    periods_inserted = 0
    events_inserted = 0
    periods_duplicates = 0
    events_duplicates = 0

    for period_name, period_data in periods_data.items():
        # 解析年份
        year_str = period_data.get('year', '')
        if year_str:
            try:
                start_year, end_year = parse_year_range(year_str)
            except ValueError as e:
                print(f"⚠️ 跳过无法解析年份的时期: {period_name} ({year_str}) - {e}")
                continue
        else:
            print(f"⚠️ 跳过没有年份信息的时期: {period_name}")
            continue
        
        period_name_cn = period_data.get('period_name_cn', period_name)
        region = period_data.get('region', 'European')
        
        # 为宗教时期生成特征和影响
        if "Abrahamic" in period_name:
            era_characteristics = "一神教信仰体系形成；圣经文献编纂；先知传统建立；律法传统起源；道德观念体系化"
            key_legacy = "奠定了西方一神教基础；影响了犹太教、基督教、伊斯兰教发展；塑造了西方道德哲学传统"
        elif "Universal Church" in period_name:
            era_characteristics = "基督教体制化发展；教义统一化；教会与皇权结合；传教网络扩展；宗教权威集中化"
            key_legacy = "建立了基督教正统教义体系；形成了教会组织模式；影响了中世纪欧洲政治格局"
        elif "Schisms and Crusades" in period_name:
            era_characteristics = "基督教大分裂；宗教战争爆发；东西方教会对立；十字军东征运动；宗教军事化冲突"
            key_legacy = "导致基督教东西分裂；促进了东西方文化交流；塑造了宗教与政治的关系模式"
        elif "Reformation" in period_name:
            era_characteristics = "宗教改革兴起；新教诞生；宗教多样性增加；印刷术助力；民族宗教形成"
            key_legacy = "打破了天主教会垄断；推动了宗教自由发展；促进了民族国家意识觉醒"
        else:
            era_characteristics = "宗教发展与变革"
            key_legacy = "对后世产生宗教影响"
        
        # 确定时期类型
        period_type = determine_period_type(period_name, period_name_cn, start_year, end_year)
        
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
                    period_type, region, description,
                    era_characteristics, key_legacy
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                period_name,         # period_name
                start_year,          # start_year
                end_year,            # end_year
                period_type,         # period_type
                region,              # region
                era_characteristics, # description
                key_legacy           # key_legacy
            ))
            
            periods_inserted += 1
        else:
            print(f"⏭️ 时期已存在: {period_name} ({start_year})")
            periods_duplicates += 1
        
        # 获取时期ID（用于插入事件）
        cursor.execute('''
            SELECT id FROM periods
            WHERE period_name = ? AND start_year = ?
        ''', (period_name, start_year))
        period_result = cursor.fetchone()
        if period_result:
            period_id = period_result[0]
        else:
            print(f"❌ 无法获取时期ID: {period_name}")
            continue
        
        # 插入事件
        events = period_data.get('events', [])
        for event in events:
            event_name = event.get('event_name', '')
            event_start_year = event.get('start_year', start_year)
            event_end_year = event.get('end_year', event_start_year)
            key_figures = event.get('key_figures', '')
            description = event.get('description', '')
            impact = event.get('impact', '')
            category = event.get('category', '')
            importance_level = event.get('importance_level', 5)  # 修正字段名
            event_region = event.get('region', region)
            source = event.get('source', '')
            
            # 检查事件是否已存在
            cursor.execute('''
                SELECT id FROM events
                WHERE event_name = ? AND start_year = ?
            ''', (event_name, event_start_year))
            
            if not cursor.fetchone():
                print(f"  ✅ 插入事件: {event_name} ({event_start_year}) [{category}]")
                
                cursor.execute('''
                    INSERT INTO events (
                        event_name, start_year, end_year, key_figures,
                        description, impact, category, region, 
                        importance_level, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_name,         # event_name
                    event_start_year,   # start_year
                    event_end_year,     # end_year
                    key_figures,        # key_figures
                    description,        # description
                    impact,             # impact
                    category,           # category
                    event_region,       # region
                    importance_level,    # importance_level
                    source              # source
                ))
                
                events_inserted += 1
            else:
                print(f"  ⏭️ 事件已存在: {event_name} ({event_start_year})")
                events_duplicates += 1

    conn.commit()
    conn.close()

    print("\n🎉 数据导入完成！")
    print(f"✅ 新增时期: {periods_inserted} 个")
    print(f"✅ 新增事件: {events_inserted} 个")
    print(f"⏭️ 重复时期: {periods_duplicates} 个")
    print(f"⏭️ 重复事件: {events_duplicates} 个")
    
    # 显示数据库统计
    print("\n📊 数据库统计：")
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE region = "European";')
    total_european = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE region = "Chinese";')
    total_chinese = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE region = "European";')
    total_european_events = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE region = "Chinese";')
    total_chinese_events = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE category = "宗教"')
    religious_events = cursor.fetchone()[0]
    
    print(f"🇪🇺 欧洲时期总数: {total_european}")
    print(f"🇨🇳 中国时期总数: {total_chinese}")
    print(f"🇪🇺 欧洲事件总数: {total_european_events}")
    print(f"🇨🇳 中国事件总数: {total_chinese_events}")
    print(f"⛪ 宗教相关事件总数: {religious_events}")
    
    conn.close()

if __name__ == "__main__":
    main()