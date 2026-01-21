# 缓存功能实现总结

## 已实现功能

### 1. 缓存系统设计（cache_manager.py）

#### 文件结构
```
cache/
├── Chinese/
│   ├── Chinese_-1000_Raw.json      # 原始抓取内容
│   ├── Chinese_-1000_LLM.json      # LLM处理后的events
│   ├── Chinese_-500_Raw.json
│   ├── Chinese_-500_LLM.json
│   └── ... (其他年份)
└── European/
    ├── European_-1000_Raw.json
    ├── European_-1000_LLM.json
    └── ... (其他年份)
```

#### 缓存数据格式

**Raw JSON** (e.g., `Chinese_2020_Raw.json`):
```json
{
  "region": "Chinese",
  "year": 2020,
  "title": "2020",
  "extract": "维基百科抓取的原始内容...",
  "timestamp": "2026-01-17T03:06:00Z"
}
```

**LLM JSON** (e.g., `Chinese_2020_LLM.json`):
```json
{
  "region": "Chinese",
  "year": 2020,
  "events": [
    {
      "event_name": "新冠疫情爆发",
      "start_year": 2020,
      "description": "...",
      "category": "政治",
      ...
    }
  ],
  "timestamp": "2026-01-17T03:06:00Z"
}
```

#### CacheManager 类方法

| 方法 | 功能 |
|------|--------|
| `save_raw_data()` | 保存原始抓取数据 |
| `load_raw_data()` | 加载原始抓取数据 |
| `save_llm_data()` | 保存 LLM 处理结果 |
| `load_llm_data()` | 加载 LLM 处理结果 |
| `is_cached()` | 检查数据是否已缓存 |
| `clear_cache()` | 清空缓存（支持按地区/年份清空） |
| `get_cache_info()` | 获取缓存统计信息 |

### 2. Wikipedia Scraper 集成（wikipedia_scraper.py）

#### 修改内容

1. **添加缓存导入**:
   ```python
   from cache_manager import CacheManager
   ```

2. **添加 region 参数**:
   ```python
   def __init__(self, language: str = "en", user_agent: str = "TimelineProject/1.0", region: str = "European"):
   ```

3. **添加 cache 实例**:
   ```python
   self.cache = CacheManager()
   ```

4. **修改 get_year_page() 方法**:
   - 添加 `force_refresh` 参数
   - 先检查 Raw 缓存，命中则返回
   - 未命中则抓取并保存到 Raw 缓存

### 3. Timeline Generator 集成（timeline_generator.py）

#### 修改内容

1. **添加缓存导入**:
   ```python
   from cache_manager import CacheManager
   ```

2. **添加 cache 实例**:
   ```python
   self.cache = CacheManager()
   ```

3. **修改 scraper 初始化**:
   ```python
   self.scraper = WikipediaScraper(language="en" if region == "European" else "zh", region=region)
   ```

4. **修改 scrape_full_timeline() 方法**:
   - 添加 `force_refresh` 参数
   - **三层缓存逻辑**：
     1. 先检查 LLM 缓存（最高优先级）
     2. LLM 缓存未命中，检查 Raw 缓存
     3. Raw 缓存命中，用 Raw 数据调用 LLM 处理
     4. 都未命中，才从 Wikipedia 抓取
   - 保存 LLM 处理结果到 LLM 缓存

### 4. 缓存流程逻辑

```
┌─────────────────────────────────────────────┐
│  开始处理年份 Y                        │
└──────────────┬──────────────────────────┘
               │
               ▼
    ┌────────────────────────┐
    │ 检查 LLM 缓存    │
    └────┬────────────────┘
         │
         ▼
    ┌────────────┐     ┌────────────────┐
    │ 命中     │     │ 未命中        │
    └────┬──────┘     └────┬───────────┘
         │                  │
         │                  ▼
         │         ┌─────────────────────────┐
         │         │  使用缓存数据         │
         │         │ 存入数据库           │
         │         └─────────────────────┘
         │
         ▼
    ┌──────────────────────┐
    │ 检查 Raw 缓存     │
    └────┬────────────────┘
         │
         ▼
    ┌────────────┐     ┌────────────────┐
    │ 命中     │     │ 未命中        │
    └────┬──────┘     └────┬───────────┘
         │                  │
         │                  ▼
         │         ┌─────────────────────────┐
         │         │ 调用 LLM 处理     │
         │         │ 保存到 LLM 缓存      │
         │         │ 存入数据库           │
         │         └─────────────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │  从 Wikipedia 抓取    │
    │  保存到 Raw 缓存        │
    │  调用 LLM 处理         │
    │  保存到 LLM 缓存         │
    │  存入数据库               │
    └──────────────────────────┘
```

### 5. 使用方式

#### 正常使用（自动缓存）
```python
from timeline_generator import TimelineGenerator

generator = TimelineGenerator(
    region="Chinese",
    llm_api_key="your_key",
    llm_base_url="your_url",
    llm_model="gpt-4o-mini"
)

# 第一次运行：会抓取并缓存
result = generator.scrape_full_timeline(
    classical_years=100,
    min_importance=6
)

# 第二次运行：直接使用缓存（跳过抓取和 LLM）
result = generator.scrape_full_timeline(
    classical_years=100,
    min_importance=6
)
```

#### 强制刷新（重新抓取和处理）
```python
# force_refresh=True 会：
# 1. 重新从 Wikipedia 抓取
# 2. 重新调用 LLM 处理
# 3. 覆盖旧的 Raw 和 LLM 缓存
result = generator.scrape_full_timeline(
    classical_years=100,
    min_importance=6,
    force_refresh=True  # 全部重新处理
)
```

### 6. 优势总结

| 优势 | 说明 |
|--------|------|
| **避免重复抓取** | 相同年份只抓取一次，节省 API 调用 |
| **避免重复 LLM 处理** | 相同数据只处理一次，节省 API 成本 |
| **永久缓存** | JSON 文件持久化，重启程序后仍可用 |
| **中间过程保留** | Raw 和 LLM 数据都保存，便于调试和分析 |
| **灵活刷新** | `force_refresh` 参数控制何时重新处理 |
| **三层缓存** | LLM → Raw → Wikipedia，最大化缓存利用率 |

### 7. 已测试功能

- ✅ Raw 数据保存和加载
- ✅ LLM 数据保存和加载
- ✅ 缓存存在性检查
- ✅ 缓存清空功能
- ✅ 缓存统计信息
- ✅ Scraper Raw 缓存集成
- ✅ Scraper force_refresh 功能
- ✅ Timeline Generator LLM 缓存集成
- ✅ Timeline Generator Raw → LLM 流程
- ✅ Timeline Generator force_refresh 功能

### 8. 注意事项

1. **缓存目录**: `cache/` 不在版本控制中（建议添加到 `.gitignore`）
2. **数据库操作**: 缓存不影响数据库插入，数据库操作保持正常
3. **错误处理**: 缓存失败时会降级到抓取，保证可用性
4. **日志输出**: 缓存命中/未命中会打印日志，方便调试
5. **force_refresh=True**: 会完全重新抓取和处理，忽略所有缓存

### 9. 文件清单

- ✅ `cache_manager.py` - 缓存管理器（新建）
- ✅ `wikipedia_scraper.py` - 集成 Raw 缓存（修改）
- ✅ `timeline_generator.py` - 集成三层缓存逻辑（修改）
- ✅ `test_cache.py` - 缓存功能测试（新建）
- ✅ `test_cache_direct.py` - 直接缓存测试（新建）
- ✅ `cache_summary.md` - 本文档（新建）

## 下一步

缓存功能已完全实现并测试通过！可以在 notebook 或独立脚本中使用。
