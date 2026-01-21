"""
LangChain SQLDatabase Integration for Natural Language Queries

This module provides natural language query capabilities using
LangChain's SQLDatabase and SQLDatabaseToolkit.
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv(override=True)

# Import LangChain SQL components
try:
    from langchain_community.utilities import SQLDatabase
except ImportError:
    raise ImportError(
        "SQLDatabase not found. Install:\n"
        "  pip install langchain-community"
    )

# Import SQLDatabaseToolkit and create_sql_agent
try:
    from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
except ImportError:
    raise ImportError(
        "SQLDatabaseToolkit or create_sql_agent not found. Install:\n"
        "  pip install langchain-community"
    )

# Import LLM
from langchain_openai import ChatOpenAI


class TimelineNLQueryEngine:
    """Natural language query engine for timeline database."""

    def __init__(self,
                 db_connection_string: str,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: str = "gpt-4o-mini"):
        """
        Initialize natural language query engine.

        Args:
            db_connection_string: Database connection string (SQLite or PostgreSQL)
            api_key: OpenAI API key
            base_url: API base URL (for custom endpoints)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be provided or set in environment")

        # Create LangChain SQLDatabase object
        self.db = SQLDatabase.from_uri(db_connection_string)

        # Initialize LLM
        llm_kwargs = {
            "model": model,
            "temperature": 0,
            "api_key": self.api_key
        }

        if self.base_url:
            llm_kwargs["base_url"] = self.base_url

        self.llm = ChatOpenAI(**llm_kwargs)

        # Create SQL toolkit
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

        # Create agent executor
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type="tool-calling",
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def query(self, question: str) -> str:
        """
        Execute a natural language query.

        Args:
            question: Natural language question about historical events

        Returns:
            Answer text
        """
        try:
            result = self.agent_executor.invoke({"input": question})
            return result.get("output", "No response")
        except Exception as e:
            return f"Error processing query: {e}"

    def get_available_tables(self) -> list[str]:
        """Get list of available tables in database."""
        return list(self.db.get_usable_table_names())

    def get_table_schema(self, table_name: str) -> str:
        """Get schema for a specific table."""
        return self.db.get_table_info([table_name])

    def get_all_schemas(self) -> str:
        """Get schema for all tables."""
        return self.db.get_table_info()


def create_sql_query_engine(db_connection_string: str = "sqlite:///data.db",
                          api_key: Optional[str] = None,
                          base_url: Optional[str] = None,
                          model: str = "gpt-4o-mini") -> TimelineNLQueryEngine:
    """
    Convenience function to create a natural language query engine.

    Args:
        db_connection_string: Database connection string
        api_key: OpenAI API key
        base_url: API base URL
        model: Model name

    Returns:
        TimelineNLQueryEngine instance
    """
    return TimelineNLQueryEngine(
        db_connection_string=db_connection_string,
        api_key=api_key,
        base_url=base_url,
        model=model
    )
