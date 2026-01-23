# AGENTS.md

## Overview

This file contains instructions for agentic coding agents working in the historical timeline project repository. The project builds a FastAPI-based API server for historical event visualization with SQLite database storage and web scraping capabilities.

## Build Commands

### Dependency Management
```bash
# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# Install development dependencies (add to pyproject.toml if needed)
pip install black isort flake8 mypy pytest pytest-cov
```

### Building the Project
```bash
# Build distribution packages
python -m build

# Or using uv
uv build
```

### Running the Application
```bash
# Start the FastAPI server
python api_server.py

# Or using uvicorn directly
uvicorn api_server:app --reload --host 127.0.0.1 --port 8000

# Start with environment variables
LLM_API_KEY=your_key python api_server.py
```

### Database Setup
```bash
# Create database tables (runs automatically on server start)
python -c "from enhanced_database_manager import EnhancedDatabaseManager; db = EnhancedDatabaseManager(); db.create_tables()"
```

## Lint Commands

The project currently doesn't have linting configured. Recommended setup:

### Code Formatting
```bash
# Format code with Black
black .

# Check formatting without changes
black --check .

# Sort imports with isort
isort .

# Check import sorting
isort --check-only .
```

### Linting
```bash
# Lint with flake8
flake8 . --max-line-length=88 --extend-ignore=E203,W503

# Type checking with mypy
mypy . --ignore-missing-imports
```

### Pre-commit Setup (Recommended)
Add to `.pre-commit-config.yaml`:
```yaml
repos:
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
  - id: black

- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks:
  - id: isort

- repo: https://github.com/pycqa/flake8
  rev: 7.0.0
  hooks:
  - id: flake8
```

## Test Commands

The project currently has no test files (they were cleaned up). Recommended test setup:

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_database_manager.py

# Run single test function
pytest tests/test_database_manager.py::test_insert_event

# Run tests matching pattern
pytest -k "test_get_events"

# Run tests in verbose mode
pytest -v

# Run tests with debugging
pytest --pdb
```

### Test Structure
```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
├── test_database_manager.py
├── test_api_server.py
├── test_timeline_generator.py
└── test_data/
    └── sample_events.json
```

### Example Test File
```python
import pytest
from database_manager import DatabaseManager

@pytest.fixture
def db_manager():
    """Fixture for database manager with test database."""
    return DatabaseManager("sqlite:///test.db")

def test_insert_event(db_manager):
    """Test inserting an event."""
    event = {
        "event_name": "Test Event",
        "start_year": -100,
        "description": "Test description"
    }
    result = db_manager.insert_event(event)
    assert result is not None
```

## Code Style Guidelines

### General Principles

- **Python Version**: Use Python 3.10+ features (f-strings, union types, etc.)
- **Code Quality**: Follow PEP 8 style guide
- **Type Safety**: Use type hints for all function parameters and return values
- **Documentation**: Write comprehensive docstrings for all classes and public functions
- **Error Handling**: Handle exceptions appropriately with meaningful messages
- **Logging**: Use `print()` for development, `logging` module for production code

### Naming Conventions

- **Classes**: PascalCase
  ```python
  class DatabaseManager:
  class TimelineGenerator:
  ```

- **Functions/Methods**: snake_case
  ```python
  def get_events_paginated():
  def scrape_from_dynasties():
  ```

- **Variables**: snake_case
  ```python
  start_year = 100
  event_name = "Olympics"
  ```

- **Constants**: UPPER_CASE
  ```python
  CHINESE_DYNASTIES = ["汉朝", "唐朝"]
  DEFAULT_LIMIT = 50
  ```

- **Files**: snake_case with .py extension
  ```python
  api_server.py
  database_manager.py
  timeline_generator.py
  ```

- **Private Members**: Prefix with single underscore
  ```python
  def _build_query(self):
  _connection_string = None
  ```

### Import Organization

```python
# Standard library imports
import os
import time
from typing import List, Dict, Optional

# Third-party imports (empty line separator)
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text

# Local imports (empty line separator)
from database_manager import DatabaseManager
from cache_manager import CacheManager
```

### Type Hints

- Use complete type annotations
- Use `Optional` for nullable parameters
- Use `Union` for multiple possible types
- Use `List`, `Dict`, `Tuple` for collections

```python
from typing import List, Dict, Optional, Tuple

def get_events_paginated(
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    region: Optional[str] = None,
    limit: int = 50
) -> Tuple[List[Dict], Dict]:
    """Get paginated events with metadata."""
    pass

def process_event(event: Dict[str, str]) -> Optional[int]:
    """Process single event, return ID or None."""
    pass
```

### Function Documentation

Use Google-style docstrings:

```python
def get_events_around_year(
    year: int,
    range_years: int = 50,
    region: Optional[str] = None,
    limit: int = 100
) -> Dict:
    """
    Get historical events around a specific year.

    Args:
        year: Target year for the query
        range_years: Number of years before/after target (default: 50)
        region: Optional region filter ("European" or "Chinese")
        limit: Maximum number of events to return (default: 100)

    Returns:
        Dictionary containing events and metadata

    Raises:
        ValueError: If year is invalid
        DatabaseError: If database query fails
    """
    pass
```

### Class Documentation

```python
class TimelineGenerator:
    """
    Generator for creating historical timelines.

    This class integrates web scraping, LLM processing, and database
    storage to create comprehensive historical timelines for different
    regions (European, Chinese, etc.).

    Attributes:
        region: Target region for timeline generation
        scraper: Wikipedia scraper instance
        processor: LangChain data processor (optional)
        db: Database manager instance
    """
    pass
```

### Error Handling

- Catch specific exceptions when possible
- Provide meaningful error messages
- Don't suppress exceptions without logging
- Use context managers for resources

```python
try:
    with self.engine.connect() as conn:
        result = conn.execute(query, params)
        return result.fetchall()
except SQLAlchemyError as e:
    raise DatabaseError(f"Failed to execute query: {e}") from e
except Exception as e:
    logger.error(f"Unexpected error in database query: {e}")
    raise
```

### Database Operations

- Use SQLAlchemy ORM/text for queries
- Always use parameterized queries
- Handle transactions properly
- Close connections automatically

```python
# Good: Parameterized query
query = text("""
    SELECT * FROM events
    WHERE start_year >= :start_year
    AND region = :region
""")
result = conn.execute(query, {
    "start_year": start_year,
    "region": region
})

# Bad: String concatenation (SQL injection risk)
query = f"SELECT * FROM events WHERE region = '{region}'"
```

### Async/Await

- Use async functions in FastAPI endpoints
- Handle async database operations properly
- Use await for I/O operations

```python
@app.get("/api/events")
async def get_events():
    """Get all events asynchronously."""
    try:
        events = await db_manager.get_events_async()
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Logging

Use the logging module instead of print for production:

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: Dict) -> None:
    """Process historical data."""
    logger.info(f"Processing {len(data)} events")
    try:
        # processing logic
        logger.debug("Data processing completed successfully")
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        raise
```

### File Structure

```
history/
├── api_server.py              # FastAPI application
├── database_manager.py         # Base database operations
├── enhanced_database_manager.py # Extended database features
├── timeline_generator.py       # Timeline generation logic
├── wikipedia_scraper.py        # Web scraping utilities
├── langchain_processor.py      # LLM data processing
├── cache_manager.py            # Caching functionality
├── data.db                     # SQLite database
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
├── uv.lock                     # uv lockfile
└── AGENTS.md                   # This file
```

### Commit Messages

Follow conventional commit format:
- `feat: add new timeline visualization endpoint`
- `fix: handle empty database queries gracefully`
- `docs: update API documentation`
- `refactor: simplify database query logic`

### Environment Variables

- Use `.env` files for local development
- Document required environment variables in README
- Never commit secrets to version control

```python
# .env
LLM_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///data.db
```

### Security Considerations

- Sanitize user inputs
- Use parameterized queries
- Validate API inputs with Pydantic models
- Handle CORS appropriately for frontend integration

```python
from pydantic import BaseModel, Field

class EventFilter(BaseModel):
    start_year: Optional[int] = Field(None, ge=-10000, le=2100)
    region: Optional[str] = Field(None, regex="^(European|Chinese)$")
    limit: int = Field(50, ge=1, le=200)
```

This guide ensures consistent, maintainable, and high-quality code across the historical timeline project.