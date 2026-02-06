#!/usr/bin/env python3
"""
将 ch_history2.json 中的中国宗教历史事件导入数据库
修复SQL参数数量错误
"""

import json
import sqlite3
import re

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
    
    if year_str.lower() == 'present':
        return 2026
    
    num_match = re.search(r'(\d+)', year_str)
    if not num_match:
        raise ValueError(f"无法从 '{year_str}' 提取年份")
    
    year_num = int(num_match.group(1))
    
    if 'bc' in year_str.lower():
        return -year_num
    
    return year_num

def determine_period_type(period_name, period_name_cn, start_year, end_year=None):
    """根據历史学专业知识推断 period_type"""
    continuous_patterns = [
        r'period', r'dynasty', r'age', r'era', r'kingdom', r'empire', r'republic'
    ]
    
    independent_patterns = [
        r'war', r'battle', r'rebellion', r'revolution', r'uprising', r'founding', r'persecution', r'suppression'
    ]
    
    special_independent = [
        'founding', 'translation', 'reform', 'movement', 'uprising', 'persecution'
    ]
    
    for keyword in special_independent:
        if keyword.lower() in period_name.lower() or keyword.lower() in period_name_cn.lower():
            return 'independent'
    
    for pattern in independent_patterns:
        if re.search(pattern, period_name, re.IGNORECASE) or re.search(pattern, period_name_cn, re.IGNORECASE):
            return 'independent'
    
    for pattern in continuous_patterns:
        if re.search(pattern, period_name, re.IGNORECASE) or re.search(pattern, period_name_cn, re.IGNORECASE):
            return 'continuous'
    
    duration = end_year - start_year if end_year else 0
    if duration > 50:
        return 'continuous'
    
    return 'continuous'

def main():
    """
    导入 ch_history2.json 中的宗教历史数据到数据库
    """
    print("📂 加载 ch_history2.json...")
    
    file_path = 'cache/Chinese/ch_history2.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            periods_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        return
    
    print(f"📊 共找到 {len(periods_data)} 个中国宗教历史时期")

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    periods_inserted = 0
    events_inserted = 0
    periods_duplicates = 0
    events_duplicates = 0

    for period_name, period_data in periods_data.items():
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
        region = period_data.get('region', 'Chinese')
        
        # 设置时期特征和历史影响
        description = ""
        era_characteristics = ""
        key_legacy = ""
        
        if "Foundations of Taoism" in period_name:
            era_characteristics = "道家哲学体系建立；清静无为思想形成；宇宙本源理论创立；道德伦理观念体系化"
            key_legacy = "奠定了中国本土哲学基础；影响了后世政治治理理念；塑造了中华文明的宇宙观"
        elif "Arrival and Early Translation of Buddhism" in period_name:
            era_characteristics = "佛教传入与经典翻译；僧伽制度建立；寺院经济发展；中印文化交流活跃"
            key_legacy = "开启了佛教中国化进程；促进了中印文化交流；奠定了中国佛教发展基础"
        elif "The Golden Age of Religion and Integration" in period_name:
            era_characteristics = "宗教鼎盛时期；三教合一思潮兴起；各宗派相互融合；宗教与皇权深度结合"
            key_legacy = "形成了独特的中国宗教格局；三教合一思想影响深远；宗教促进文化大发展"
        elif "The Later Developments and Syncretism" in period_name:
            era_characteristics = "宗教民间化发展；三教融合深化；神秘主义兴起；宗教与伦理紧密结合"
            key_legacy = "标志着宗教进入民间化阶段；儒释道三家思想深入融合；影响了民众日常生活"
        else:
            era_characteristics = "宗教发展与变革"
            key_legacy = "对后世产生宗教影响"
        
        period_type = determine_period_type(period_name, period_name_cn, start_year, end_year)
        
        # 检查时期是否已存在
        cursor.execute('''
            SELECT id FROM periods
            WHERE period_name = ? AND start_year = ?
        ''', (period_name, start_year))
        
        if not cursor.fetchone():
            print(f"✅ 插入时期: {period_name} ({start_year}-{end_year}) [{period_type}]")
            
            period_values = (
                period_name, start_year, end_year, period_type, region, description, era_characteristics, key_legacy
            )
            cursor.execute('''
                INSERT INTO periods (period_name, start_year, end_year, period_type, region, description, era_characteristics, key_legacy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', period_values)
            
            periods_inserted += 1
        else:
            print(f"⏭️ 时期已存在: {period_name} ({start_year})")
            periods_duplicates += 1
        
        cursor.execute('''
            SELECT id FROM periods
            WHERE period_name = ? AND start_year = ?
        ''', (period_name, start_year))
        period_result = cursor.fetchone()
        if not period_result:
            print(f"❌ 无法获取时期ID: {period_name}")
            continue
        
        period_id = period_result[0]
        
        events = period_data.get('events', [])
        for event in events:
            event_name = event.get('event_name', '')
            event_start_year = event.get('start_year', start_year)
            event_end_year = event.get('end_year', event_start_year)
            key_figures = event.get('key_figures', '')
            description = event.get('description', '')
            impact = event.get('impact', '')
            category = event.get('category', '')
            importance_level = event.get('importance_level', 5)
            event_region = event.get('region', region)
            source = event.get('source', '')
            
            cursor.execute('''
                SELECT id FROM events
                WHERE event_name = ? AND start_year = ?
            ''', (event_name, event_start_year))
            
            if not cursor.fetchone():
                print(f"  ✅ 插入事件: {event_name} ({event_start_year}) [{category}]")
                
                event_values = (
                    event_name, event_start_year, event_end_year, key_figures,
                    description, impact, category, event_region, importance_level, source
                )
                cursor.execute('''
                    INSERT INTO events (event_name, start_year, end_year, key_figures, description, impact, category, region, importance_level, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', event_values)
                
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
    
    print("\n📊 数据库统计：")
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE region = "European"')
    total_european = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM periods WHERE region = "Chinese"')
    total_chinese = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE region = "European"')
    total_european_events = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE region = "Chinese"')
    total_chinese_events = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE category = "宗教"')
    religious_events = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE category = "宗教" AND region = "Chinese"')
    chinese_religious_events = cursor.fetchone()[0]
    
    print(f"🇪🇺 欧洲时期总数: {total_european}")
    print(f"🇨🇳 中国时期总数: {total_chinese}")
    print(f"🇪🇺 欧洲事件总数: {total_european_events}")
    print(f"🇨🇳 中国事件总数: {total_chinese_events}")
    print(f"⛪ 宗教相关事件总数: {religious_events}")
    print(f"🏮️ 中国宗教事件总数: {chinese_religious_events}")
    
    conn.close()

if __name__ == "__main__":
    main()