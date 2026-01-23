#!/usr/bin/env python3
"""
使用 euro_history3.json 中的数据填充 periods 表的新字段：
- era_characteristics (时期特征)
- key_legacy (历史阶段和影响)
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

def extract_era_characteristics(period_name, period_data, events):
    """
    从时期数据中提取时期特征
    """
    characteristics = []
    
    # 基于时期名称的特征
    if 'civilization' in period_name.lower():
        characteristics.append("高度发达的城市文明")
        characteristics.append("复杂的社会结构")
        characteristics.append("先进的技术和艺术")
    
    elif 'empire' in period_name.lower():
        characteristics.append("大规模领土扩张")
        characteristics.append("中央集权统治")
        characteristics.append("多民族融合")
    
    elif 'republic' in period_name.lower():
        characteristics.append("公民政治参与")
        characteristics.append("法治传统")
        characteristics.append("选举制度")
    
    elif 'kingdom' in period_name.lower():
        characteristics.append("世袭君主制")
        characteristics.append("封建等级制度")
        characteristics.append("贵族统治")
    
    elif 'renaissance' in period_name.lower() or 'revival' in period_name.lower():
        characteristics.append("文化复兴")
        characteristics.append("人文主义兴起")
        characteristics.append("艺术创新")
    
    elif 'industrial' in period_name.lower():
        characteristics.append("工业化生产")
        characteristics.append("技术革新")
        characteristics.append("城市化进程")
    
    # 基于事件的特征
    if events:
        event_categories = []
        for event in events:
            category = event.get('category', '')
            if category and category not in event_categories:
                event_categories.append(category)
        
        if '政治变革' in event_categories:
            characteristics.append("政治制度变革")
        if '军事' in event_categories:
            characteristics.append("军事冲突频繁")
        if '文化艺术' in event_categories:
            characteristics.append("文化艺术繁荣")
        if '科技/生产力' in event_categories:
            characteristics.append("科技进步显著")
        if '经济' in event_categories:
            characteristics.append("经济发展活跃")
    
    return "; ".join(characteristics) if characteristics else "历史转型期"

def extract_key_legacy(period_name, period_data, events):
    """
    从时期数据中提取历史阶段和影响
    """
    legacy_points = []
    
    # 基于时期名称的历史影响
    if 'minoan' in period_name.lower():
        legacy_points.append("欧洲最早的城市文明雏形")
        legacy_points.append("宫殿经济模式的开创者")
        legacy_points.append("爱琴海文明的基础")
    
    elif 'mycenaean' in period_name.lower():
        legacy_points.append("希腊古典文明的直接源头")
        legacy_points.append("特洛伊战争的历史背景")
        legacy_points.append("线性文字B的使用者")
    
    elif 'classical greece' in period_name.lower():
        legacy_points.append("民主政治的诞生地")
        legacy_points.append("哲学思想的黄金时代")
        legacy_points.append("西方文明的基石")
    
    elif 'roman' in period_name.lower():
        if 'republic' in period_name.lower():
            legacy_points.append("共和政治制度的典范")
            legacy_points.append("法治传统的建立")
            legacy_points.append("公民权利概念的形成")
        elif 'empire' in period_name.lower():
            legacy_points.append("罗马和平的实现")
            legacy_points.append("法律体系的完善")
            legacy_points.append("基础设施建设的巅峰")
    
    elif 'migration period' in period_name.lower():
        legacy_points.append("现代欧洲民族格局的形成")
        legacy_points.append("古典文明向中世纪的过渡")
        legacy_points.append("基督教在欧洲的传播")
    
    elif 'byzantine' in period_name.lower():
        legacy_points.append("东罗马帝国的延续")
        legacy_points.append("基督教东正教的形成")
        legacy_points.append("古典文化的保护者")
    
    elif 'carolingian' in period_name.lower():
        legacy_points.append("神圣罗马帝国的雏形")
        legacy_points.append("加洛林文艺复兴")
        legacy_points.append("欧洲统一的早期尝试")
    
    elif 'holy roman empire' in period_name.lower():
        legacy_points.append("中世纪欧洲的政治秩序")
        legacy_points.append("德意志民族国家的形成")
        legacy_points.append("教皇与皇帝的权力斗争")
    
    elif 'french revolution' in period_name.lower():
        legacy_points.append("现代民主革命的开端")
        legacy_points.append("人权宣言的发表")
        legacy_points.append("民族主义思想的传播")
    
    # 基于具体事件的影响
    if events:
        for event in events:
            event_name = event.get('event_name', '')
            impact = event.get('impact', '')
            
            if '奥林匹克' in event_name:
                legacy_points.append("奥林匹克运动传统的创立")
            elif '梭伦' in event_name:
                legacy_points.append("雅典民主政治的奠基")
            elif '马拉松' in event_name:
                legacy_points.append("希腊战胜波斯的标志性胜利")
            elif '帕特农神庙' in event_name:
                legacy_points.append("古典建筑艺术的巅峰")
            elif '苏格拉底' in event_name:
                legacy_points.append("西方哲学理性主义传统的开端")
            elif '卢比孔河' in event_name:
                legacy_points.append("罗马共和制的终结")
    
    return "; ".join(legacy_points) if legacy_points else "对后世产生深远影响"

def main():
    """
    填充 periods 表的新字段
    """
    print("📂 加载 euro_history3.json...")
    
    file_path = 'cache/European/euro_history3.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            periods_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        return
    
    print(f"📊 共找到 {len(periods_data)} 个历史时期")

    # 连接数据库
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    updated_count = 0
    not_found_count = 0

    for period_name, period_data in periods_data.items():
        # 解析年份
        year_str = period_data.get('year', '')
        if year_str:
            try:
                start_year, end_year = parse_year_range(year_str)
            except ValueError:
                print(f"⚠️ 跳过无法解析年份的时期: {period_name}")
                continue
        else:
            continue
        
        # 获取事件列表
        events = period_data.get('events', [])
        
        # 提取特征和影响
        era_characteristics = extract_era_characteristics(period_name, period_data, events)
        key_legacy = extract_key_legacy(period_name, period_data, events)
        
        # 更新数据库
        cursor.execute('''
            UPDATE periods 
            SET era_characteristics = ?, key_legacy = ?
            WHERE period_name = ? AND start_year = ?
        ''', (era_characteristics, key_legacy, period_name, start_year))
        
        if cursor.rowcount > 0:
            print(f"✅ 更新时期: {period_name} ({start_year})")
            print(f"   特征: {era_characteristics[:50]}...")
            print(f"   影响: {key_legacy[:50]}...")
            updated_count += 1
        else:
            print(f"⚠️ 未找到时期: {period_name} ({start_year})")
            not_found_count += 1

    conn.commit()
    conn.close()

    print("\n🎉 数据填充完成！")
    print(f"✅ 成功更新: {updated_count} 个时期")
    print(f"⚠️ 未找到: {not_found_count} 个时期")

if __name__ == "__main__":
    main()