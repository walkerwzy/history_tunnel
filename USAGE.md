# 历史大事年表生成器 - 使用文档

## 项目概述

本项目提供了一个可复用的历史大事年表生成系统，支持多个地区（如欧洲、中国等）的历史数据采集、处理和存储。

## 模块结构

```
history/
├── wikipedia_scraper.py      # Wikipedia API数据抓取
├── langchain_processor.py    # LangChain数据处理
├── database_manager.py       # PostgreSQL数据库管理
├── timeline_generator.py     # 主生成器类（整合所有组件）
└── generate_timeline.py       # 使用示例脚本
```

## 安装依赖

```bash
# 激活conda环境
conda activate pyth310

# 安装必要的包
conda install -c conda-forge psycopg2-binary sqlalchemy requests python-dotenv pandas

# 安装LangChain相关包
pip install langchain langchain-openai langchain-community
```

## 快速开始

### 1. 基本使用

```python
from timeline_generator import TimelineGenerator

# 初始化生成器
generator = TimelineGenerator(region="European")

# 从Wikipedia抓取真实历史数据
result = generator.scrape_full_timeline(
    classical_years=100,      # 古典时期：每100年
    medieval_years=50,         # 中世纪：每50年
    early_modern_years=25,     # 近代早期：每25年
    nineteenth_century_years=10, # 19世纪：每10年
    twentieth_century_years=5,    # 20世纪：每5年
    twenty_first_century_years=1, # 21世纪：每年
    min_importance=6,          # 只保留重要事件
)
print(f"抓取了 {result['events']} 个真实历史事件")
```

### 2. 查询历史事件

```python
# 按时间范围查询
events = generator.get_timeline(
    start_year=1900,
    end_year=2000,
    min_importance=7,  # 只显示重要性>=7的事件
    limit=50
)

for event in events:
    print(f"{event['event_name']} ({event['start_year']})")
    print(f"  描述: {event['description']}")
    print(f"  分类: {event['category']}")
    print(f"  重要性: {event['importance_level']}")
```

### 3. 关键词搜索

```python
# 搜索包含特定关键词的事件
war_events = generator.search_events(keyword="war", limit=20)

for event in war_events:
    print(f"{event['event_name']}: {event['description'][:100]}...")
```

### 4. 跨地区对比

```python
# 查看某一年其他地区发生的事件
cross_events = generator.get_cross_regional_view(
    year=1945,
    other_regions=["Chinese", "Islamic", "African"],
    importance_threshold=7
)

for region, events in cross_events.items():
    print(f"{region}:")
    for event in events[:3]:
        print(f"  - {event['event_name']} ({event['start_year']})")
```

## 高级功能

### 数据采集

#### 从Wikipedia抓取真实历史数据

```python
# 抓取特定年份范围的事件
result = generator.scrape_year_range(
    start_year=1900,
    end_year=1920,
    process_with_llm=True,  # 使用LangChain处理
    progress_callback=lambda x: print(x)  # 进度回调
)

# 抓取关键历史事件
result = generator.scrape_key_events(
    num_events=100,
    process_with_llm=True
)
```

### 数据库配置

```python
from timeline_generator import TimelineGenerator

# 使用默认数据库（Neon）
generator = TimelineGenerator(region="European")

# 或使用自定义数据库连接字符串
generator = TimelineGenerator(
    region="European",
    db_connection_string="postgresql://user:password@host:port/dbname"
)
```

### 支持不同地区

```python
# 欧洲历史
european_gen = TimelineGenerator(region="European")

# 中国历史
chinese_gen = TimelineGenerator(region="Chinese")

# 其他地区
african_gen = TimelineGenerator(region="African")
```

## 数据库表结构

### events表（事件表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| event_name | VARCHAR(255) | 事件名称 |
| start_year | INTEGER | 开始年份（负数表示公元前） |
| end_year | INTEGER | 结束年份（可选） |
| key_figures | TEXT | 关键人物 |
| description | TEXT | 事件概述 |
| impact | TEXT | 事件影响 |
| category | VARCHAR(100) | 事件分类 |
| region | VARCHAR(100) | 地域 |
| importance_level | INTEGER | 重要程度（1-10） |
| source | TEXT | 数据来源 |
| created_at | TIMESTAMP | 创建时间 |

### periods表（时期表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键 |
| period_name | VARCHAR(255) | 时期名称 |
| start_year | INTEGER | 开始年份 |
| end_year | INTEGER | 结束年份 |
| period_type | VARCHAR(50) | 时期类型（continuous/independent） |
| description | TEXT | 时期描述 |
| region | VARCHAR(100) | 地域 |
| created_at | TIMESTAMP | 创建时间 |

## API配置

### OpenAI API配置

```python
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# 方式1: 环境变量
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# 方式2: 代码中设置
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
```

### NVIDIA NIM API配置

```python
# 使用NVIDIA NIM
os.environ["OPENAI_API_KEY"] = "nvidia-api-key"
os.environ["OPENAI_BASE_URL"] = "https://integrate.api.nvidia.com/v1"

generator = TimelineGenerator(
    region="European",
    llm_model="gpt-4o-mini"  # 或其他支持模型
)
```

## 完整示例

### 生成欧洲历史年表

```python
from timeline_generator import TimelineGenerator

def generate_european_timeline():
    generator = TimelineGenerator(region="European")

    # 从Wikipedia抓取真实历史数据
    result = generator.scrape_full_timeline(
        classical_years=100,      # 古典时期：每100年
        medieval_years=50,         # 中世纪：每50年
        early_modern_years=25,     # 近代早期：每25年
        nineteenth_century_years=10, # 19世纪：每10年
        twentieth_century_years=5,    # 20世纪：每5年
        twenty_first_century_years=1, # 21世纪：每年
        min_importance=6,          # 只保留重要事件
        progress_callback=lambda x: print(f"抓取进度: {x}")
    )

    # 查询20世纪重要事件
    twentieth_century = generator.get_timeline(
        start_year=1900,
        end_year=2000,
        min_importance=8,
        limit=20
    )

    # 搜索战争相关事件
    wars = generator.search_events("war", limit=15)

    # 获取统计信息
    stats = generator.get_statistics()

    return {
        "scraped": result,
        "timeline": twentieth_century,
        "wars": wars,
        "statistics": stats
    }

if __name__ == "__main__":
    data = generate_european_timeline()
    print(f"抓取完成！数据库中现有 {data['statistics']['total_events']} 个事件")
```

### 生成中国历史年表

```python
from timeline_generator import TimelineGenerator

def generate_chinese_timeline():
    generator = TimelineGenerator(region="Chinese")

    # 从Wikipedia按朝代抓取中国历史数据
    result = generator.scrape_from_dynasties(
        max_events_per_dynasty=20,  # 每个朝代最多提取20个事件
        min_importance=5,           # 最低重要程度
        progress_callback=lambda x: print(f"抓取进度: {x}")
    )

    # 查询唐朝时期（618-907年）
    tang_dynasty = generator.get_timeline(
        start_year=618,
        end_year=907,
        min_importance=6,
        limit=30
    )

    # 搜索"统一"相关事件
    unification_events = generator.search_events("统一", limit=20)

    # 与欧洲历史对比（同一时间）
    cross_events = generator.get_cross_regional_view(
        year=756,  # 唐朝中期
        other_regions=["European"],
        importance_threshold=7
    )

    return {
        "scraped": result,
        "tang_dynasty": tang_dynasty,
        "unifications": unification_events,
        "cross_comparison": cross_events
    }

if __name__ == "__main__":
    data = generate_chinese_timeline()
    print(f"中国历史数据抓取完成！共 {data['scraped']['events']} 个事件")
```

## 性能优化

1. **批量插入**：使用`batch_insert_events`和`batch_insert_periods`提高插入性能
2. **索引优化**：已为常用查询字段创建索引
3. **限制结果**：使用`limit`参数避免返回过多数据
4. **重要性过滤**：使用`min_importance`减少不必要的结果

## 故障排除

### 问题1: API认证失败

```
Error code: 401 - unauthorized client detected
```

**解决方案**：
- 检查`OPENAI_API_KEY`是否正确
- 确认`OPENAI_BASE_URL`配置正确
- 验证API密钥权限

### 问题2: 数据库连接失败

```
psycopg2.OperationalError: could not connect to server
```

**解决方案**：
- 检查数据库连接字符串格式
- 确认数据库服务运行正常
- 验证网络连接

### 问题3: LangChain不可用

```
Warning: LangChain processor not available (no API key)
```

**解决方案**：
- 不配置LLM也可使用基本功能
- 使用`process_with_llm=False`跳过LLM处理
- 数据以简化格式存储

## 后续扩展

1. **前端可视化**：集成d3.js实现交互式时间轴
2. **更多数据源**：添加Europeana、Britannica等API
3. **智能分类**：使用LLM自动分类事件
4. **事件关联**：发现和关联相关历史事件
5. **多语言支持**：支持中文、法文等Wikipedia

## 许可证

MIT License
