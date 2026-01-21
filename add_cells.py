import json

# 读取现有notebook
with open('european_timeline.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 定义要添加的新cells
new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 清空测试数据\n",
            "\n",
            "在开始生成真实数据前，先清空测试数据。"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 清空events表\n",
            "truncate_events = text(\"TRUNCATE TABLE events RESTART IDENTITY CASCADE\")\n",
            "with engine.connect() as conn:\n",
            "    conn.execute(truncate_events)\n",
            "    conn.commit()\n",
            "print(\"events表已清空！\")\n",
            "\n",
            "# 清空periods表\n",
            "truncate_periods = text(\"TRUNCATE TABLE periods RESTART IDENTITY CASCADE\")\n",
            "with engine.connect() as conn:\n",
            "    conn.execute(truncate_periods)\n",
            "    conn.commit()\n",
            "print(\"periods表已清空！\")\n",
            "\n",
            "# 验证清空结果\n",
            "with engine.connect() as conn:\n",
            "    result = conn.execute(text(\"SELECT COUNT(*) FROM events\"))\n",
            "    events_count = result.fetchone()[0]\n",
            "    result = conn.execute(text(\"SELECT COUNT(*) FROM periods\"))\n",
            "    periods_count = result.fetchone()[0]\n",
            "print(f\"当前数据: events={events_count}, periods={periods_count}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 生成真实的欧洲历史数据\n",
            "\n",
            "使用TimelineGenerator生成真实的欧洲历史事件和时期。"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 导入TimelineGenerator\n",
            "from timeline_generator import TimelineGenerator\n",
            "\n",
            "# 初始化欧洲时间轴生成器\n",
            "european_generator = TimelineGenerator(region=\"European\")\n",
            "\n",
            "# 生成真实的欧洲历史数据\n",
            "print(\"开始生成欧洲历史数据...\")\n",
            "result = european_generator.scrape_full_timeline(\n",
            "    classical_years=100,      # 古典时期：每100年\n",
            "    medieval_years=50,         # 中世纪：每50年\n",
            "    early_modern_years=25,     # 近代早期：每25年\n",
            "    nineteenth_century_years=10, # 19世纪：每10年\n",
            "    twentieth_century_years=5,    # 20世纪：每5年\n",
            "    twenty_first_century_years=1, # 21世纪：每年\n",
            "    min_importance=6,          # 只保留重要事件\n",
            ")\n",
            "print(f\"抓取完成: {result['events']} 个事件\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 生成真实的中国历史数据\n",
            "\n",
            "使用TimelineGenerator生成真实的中国历史事件和时期。"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 初始化中国时间轴生成器\n",
            "chinese_generator = TimelineGenerator(region=\"Chinese\")\n",
            "\n",
            "# 生成真实的中国历史数据\n",
            "print(\"开始生成中国历史数据...\")\n",
            "result = chinese_generator.scrape_from_dynasties(\n",
            "    max_events_per_dynasty=20,  # 每个朝代最多20个事件\n",
            "    min_importance=5,           # 最低重要程度\n",
            ")\n",
            "print(f\"抓取完成: {result['events']} 个事件\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 验证生成的数据\n",
            "\n",
            "查看数据库中的统计数据和示例数据。"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 获取统计信息\n",
            "stats = european_generator.get_statistics()\n",
            "print(f\"数据库统计:\")\n",
            "print(f\"  总事件数: {stats['total_events']}\")\n",
            "print(f\"  总时期数: {stats['total_periods']}\")\n",
            "if 'events_by_region' in stats:\n",
            "    print(f\"  按地区统计事件: {stats['events_by_region']}\")\n",
            "if 'periods_by_region' in stats:\n",
            "    print(f\"  按地区统计时期: {stats['periods_by_region']}\")\n",
            "\n",
            "# 查询示例：20世纪重要事件（欧洲）\n",
            "print(\"\\n示例：20世纪重要事件（欧洲）\")\n",
            "twentieth_century = european_generator.get_timeline(\n",
            "    start_year=1900,\n",
            "    end_year=2000,\n",
            "    min_importance=7,\n",
            "    limit=10\n",
            ")\n",
            "for event in twentieth_century:\n",
            "    print(f\"  {event['event_name']} ({event['start_year']}) - {event.get('category', 'N/A')}\")\n",
            "\n",
            "# 查询示例：唐朝时期事件（中国）\n",
            "print(\"\\n示例：唐朝时期事件（中国）\")\n",
            "tang_dynasty = chinese_generator.get_timeline(\n",
            "    start_year=618,\n",
            "    end_year=907,\n",
            "    min_importance=6,\n",
            "    limit=10\n",
            ")\n",
            "for event in tang_dynasty:\n",
            "    print(f\"  {event['event_name']} ({event['start_year']}) - {event.get('category', 'N/A')}\")"
        ]
    }
]

# 添加新cells到notebook
nb['cells'].extend(new_cells)

# 保存更新后的notebook
with open('european_timeline.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Successfully added new cells to notebook!')
