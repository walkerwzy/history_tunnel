"""
LangChain Data Processor for Historical Events

This module uses LangChain and LLM to process and structure historical data
from Wikipedia into the database schema format.
"""

import os
import json
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Try imports from the latest LangChain packages first (recommended as of 2025)
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fall back to community package for older versions
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        raise ImportError(
            "Could not import ChatOpenAI. Please install one of:\n"
            "  pip install langchain-openai  # Latest (recommended)\n"
            "  pip install langchain-community  # Alternative"
        )

# Import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

# Import Pydantic components
try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "Pydantic is required. Please install: pip install pydantic"
    )

# Import PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser


class EventSchema(BaseModel):
    """Pydantic model for historical events."""
    event_name: str = Field(description="历史事件的名称（中文）")
    start_year: int = Field(description="开始年份（公元前为负整数）")
    end_year: Optional[int] = Field(None, description="结束年份（整数），如果是单年事件则为null")
    key_figures: str = Field(description="事件中的关键人物列表（逗号分隔的字符串，中文）")
    description: str = Field(description="事件的简要概述（1-2句话，中文）")
    impact: str = Field(description="事件的历史影响和意义（中文）")
    category: str = Field(description="事件类别（中文）：政治、技术、军事、经济、文化、宗教、科学")
    importance_level: int = Field(description="重要性等级（1-10，10为最重要）")


class PeriodSchema(BaseModel):
    """Pydantic model for historical periods."""
    period_name: str = Field(description="历史时期的名称（中文）")
    start_year: int = Field(description="开始年份（公元前为负整数）")
    end_year: int = Field(description="结束年份（整数）")
    period_type: str = Field(description="时期类型：'continuous' 表示长期时代（如：中世纪），'independent' 表示特定时期（如：文艺复兴）")
    description: str = Field(description="该时期的简要描述（中文）")


class HistoricalDataProcessor:
    """Processor for structuring historical data using LangChain."""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize the LangChain processor.

        Args:
            api_key: OpenAI API key
            base_url: API base URL
            model: Model name to use
        """
        # print(f"args 2: {api_key}, {base_url}, {model}")
        load_dotenv(override=True)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided or set in environment")

        llm_kwargs = {
            "model": model,
            "temperature": 0.3,
            "api_key": self.api_key
        }

        if self.base_url:
            llm_kwargs["base_url"] = self.base_url

        self.llm = ChatOpenAI(**llm_kwargs)

        self.event_schemas = self._create_event_schemas()
        self.period_schemas = self._create_period_schemas()

    def _create_event_schemas(self) -> PydanticOutputParser:
        """Create structured output parser for events."""
        return PydanticOutputParser(pydantic_object=EventSchema)

    def _create_period_schemas(self) -> PydanticOutputParser:
        """Create structured output parser for periods."""
        return PydanticOutputParser(pydantic_object=PeriodSchema)

    def process_wikipedia_page_as_event(self, page_content: Dict, region: str) -> Optional[Dict]:
        """
        Process a Wikipedia page into an event structure.

        Args:
            page_content: Wikipedia page content dictionary
            region: Region (e.g., "European", "Chinese")

        Returns:
            Structured event data dictionary or None
        """
        title = page_content.get("title", "")
        extract = page_content.get("extract", "")

        if not extract:
            return None

        format_instructions = self.event_schemas.get_format_instructions()

        prompt = ChatPromptTemplate.from_template("""
你是一位历史学家，正在分析历史事件。从以下维基百科页面内容中提取结构化信息。

标题：{title}
内容：{content}
地区：{region}

提取以下信息（所有文本字段必须输出为中文）：
{format_instructions}

只返回 JSON 对象，不要其他文字。
""")

        formatted_prompt = prompt.format(
            title=title,
            content=extract[:2000],
            region=region,
            format_instructions=format_instructions
        )

        try:
            response = self.llm.invoke(formatted_prompt)
            event_schema = self.event_schemas.parse(response.content)

            # Convert Pydantic model to dict
            event_data = event_schema.model_dump() if hasattr(event_schema, "model_dump") else event_schema.dict()
            event_data["region"] = region
            event_data["source"] = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

            return event_data
        except Exception as e:
            print(f"Error processing page {title}: {e}")
            return None

    def process_wikipedia_page_as_period(self, page_content: Dict, region: str) -> Optional[Dict]:
        """
        Process a Wikipedia page into a period structure.

        Args:
            page_content: Wikipedia page content dictionary
            region: Region (e.g., "European", "Chinese")

        Returns:
            Structured period data dictionary or None
        """
        title = page_content.get("title", "")
        extract = page_content.get("extract", "")

        if not extract:
            return None

        format_instructions = self.period_schemas.get_format_instructions()

        prompt = ChatPromptTemplate.from_template("""
你是一位历史学家，正在分析历史时期。从以下维基百科页面内容中提取结构化信息。

标题：{title}
内容：{content}
地区：{region}

提取以下信息（所有文本字段必须输出为中文）：
{format_instructions}

只返回 JSON 对象，不要其他文字。
""")

        formatted_prompt = prompt.format(
            title=title,
            content=extract[:2000],
            region=region,
            format_instructions=format_instructions
        )

        try:
            response = self.llm.invoke(formatted_prompt)
            period_schema = self.period_schemas.parse(response.content)

            # Convert Pydantic model to dict
            period_data = period_schema.model_dump() if hasattr(period_schema, "model_dump") else period_schema.dict()
            period_data["region"] = region

            return period_data
        except Exception as e:
            print(f"Error processing period {title}: {e}")
            return None

    def extract_events_from_year_page(self, year: int, year_content: Dict, region: str) -> List[Dict]:
        """
        Extract events from a specific year page.

        Args:
            year: The year number
            year_content: Wikipedia year page content
            region: Region

        Returns:
            List of structured event dictionaries
        """
        extract = year_content.get("extract", "")
        if not extract:
            return []
        print(f"Extracting events from year {year} in {region}")
        format_instructions = self.event_schemas.get_format_instructions()

        prompt = ChatPromptTemplate.from_template("""
为指定年份和地区生成该年度可能发生的重大历史事件。如果页面内容中有相关信息，请结合使用；如果页面内容不足或没有相关信息，请主要基于历史知识生成合理的事件。

年份：{year}
内容：{content}
地区：{region}

提取该年度发生的重要事件。为每个事件提供以下信息（所有文本字段必须输出为中文）：
{format_instructions}

返回 JSON 数组格式的事件对象，不要其他文字。
""")

        formatted_prompt = prompt.format(
            year=year,
            content=extract[:3000],
            region=region,
            format_instructions=format_instructions
        )

        try:
            response = self.llm.invoke(formatted_prompt)
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                elif content.startswith("python"):
                    content = content[7:]
                content = content.strip()

            events = json.loads(content)

            if isinstance(events, list):
                for event in events:
                    event["region"] = region
                    event["source"] = f"https://en.wikipedia.org/wiki/{abs(year)}_{'BC' if year < 0 else ''}"
                return events
            elif isinstance(events, dict):
                events["region"] = region
                events["source"] = f"https://en.wikipedia.org/wiki/{abs(year)}_{'BC' if year < 0 else ''}"
                return [events]
            else:
                return []
        except Exception as e:
            print(f"Error extracting events from year {year}: {e}")
            return []

    def extract_events_from_dynasty_page(self, dynasty_name: str, dynasty_content: Dict, region: str, max_events: int = 20) -> List[Dict]:
        """
        Extract events from a Chinese dynasty page.

        Args:
            dynasty_name: The dynasty name (e.g., "唐朝", "宋朝")
            dynasty_content: Wikipedia dynasty page content
            region: Region
            max_events: Maximum number of events to extract

        Returns:
            List of structured event dictionaries
        """
        extract = dynasty_content.get("extract", "")
        if not extract:
            return []
        print(f"Extracting events from dynasty {dynasty_name} in {region}")
        format_instructions = self.event_schemas.get_format_instructions()

        prompt = ChatPromptTemplate.from_template("""
从以下朝代页面内容中提取重要的历史事件。

朝代：{dynasty}
内容：{content}
地区：{region}

提取该朝代期间发生的重大历史事件（最多 {max_events} 个）。为每个事件提供以下信息（所有文本字段必须输出为中文）：
{format_instructions}

请按时间顺序排列事件，并确保涵盖不同类别（政治、军事、文化、经济等）。

返回 JSON 数组格式的事件对象，不要其他文字。
""")

        formatted_prompt = prompt.format(
            dynasty=dynasty_name,
            content=extract[:5000],  # 使用更多内容，因为朝代页面更长
            region=region,
            max_events=max_events,
            format_instructions=format_instructions
        )

        try:
            response = self.llm.invoke(formatted_prompt)
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                elif content.startswith("python"):
                    content = content[7:]
                content = content.strip()

            events = json.loads(content)

            if isinstance(events, list):
                for event in events:
                    event["region"] = region
                    event["source"] = f"https://zh.wikipedia.org/wiki/{dynasty_name}"
                return events
            elif isinstance(events, dict):
                events["region"] = region
                events["source"] = f"https://zh.wikipedia.org/wiki/{dynasty_name}"
                return [events]
            else:
                return []
        except Exception as e:
            print(f"Error extracting events from dynasty {dynasty_name}: {e}")
            return []



    def validate_event(self, event: Dict) -> bool:
        """
        Validate an event data structure.

        Args:
            event: Event dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["event_name", "start_year", "region"]
        
        for field in required_fields:
            if field not in event or not event[field]:
                return False
        
        if not isinstance(event["start_year"], int):
            return False
        
        if "importance_level" in event:
            try:
                level = int(event["importance_level"])
                if level < 1 or level > 10:
                    return False
            except (ValueError, TypeError):
                return False
        
        return True



