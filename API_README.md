# Historical Timeline API Backend

FastAPI-based backend server for the historical timeline visualization frontend.

## Features

- **RESTful API** for historical events data
- **Pagination support** for timeline scrolling
- **Advanced search** by keywords, regions, time ranges
- **Cross-regional comparisons**
- **Statistics and analytics**
- **CORS enabled** for frontend integration

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /api/events` - Get all historical events (for frontend)
- `GET /api/health` - Health check

### Timeline Endpoints

- `GET /api/timeline/paginated` - Paginated events with filtering
  - Query params: `start_year`, `end_year`, `region`, `min_importance`, `offset`, `limit`
- `GET /api/events/around/{year}` - Events around a specific year
  - Path param: `year`
  - Query params: `range_years`, `region`, `min_importance`, `limit`

### Search & Comparison

- `GET /api/compare/{year}` - Compare events between regions at specific year
  - Path param: `year`
  - Query params: `range_years`
- `GET /api/search` - Search events by keyword
  - Query params: `q` (required), `region`, `limit`

### Analytics

- `GET /api/statistics` - Get comprehensive statistics
  - Returns: total events, region distribution, categories, year range, importance stats

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

**Option A: Using the startup script (recommended)**
```bash
./start_server.sh
```

**Option B: Manual startup**
```bash
# Create database tables
python -c "
from enhanced_database_manager import EnhancedDatabaseManager
db = EnhancedDatabaseManager()
db.create_tables()
"

# Start server
python api_server.py
```

### 3. Access the API

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Frontend**: Open `timeline_visualization.html` in your browser

## Data Requirements

The API expects a SQLite database (`data.db`) with historical events data. The database should contain an `events` table with columns:

- `id` (INTEGER PRIMARY KEY)
- `event_name` (VARCHAR)
- `start_year` (INTEGER)
- `end_year` (INTEGER, optional)
- `key_figures` (TEXT)
- `description` (TEXT)
- `impact` (TEXT)
- `category` (VARCHAR)
- `region` (VARCHAR) - 'European' or 'Chinese'
- `importance_level` (INTEGER, 1-10)
- `source` (TEXT, optional)
- `created_at` (DATETIME)

## Development

### Project Structure

```
history/
├── api_server.py          # FastAPI server
├── enhanced_database_manager.py  # Database operations
├── database_manager.py     # Base database manager
├── requirements.txt        # Python dependencies
├── start_server.sh        # Startup script
├── timeline_visualization.html  # Frontend
└── data.db                 # SQLite database (auto-created)
```

### Adding New Endpoints

1. Add the endpoint function in `api_server.py`
2. Implement the database logic in `enhanced_database_manager.py` if needed
3. Add proper type hints and error handling
4. Update this README

### Database Operations

Use the `EnhancedDatabaseManager` class for all database operations:

```python
from enhanced_database_manager import EnhancedDatabaseManager

db = EnhancedDatabaseManager()

# Get paginated events
events, metadata = db.get_events_paginated(
    start_year=0,
    end_year=2026,
    region="European",
    limit=50
)

# Search events
events, metadata = db.search_events("war", region="European", limit=20)

# Get statistics
stats = db.get_statistics()
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database errors**: Check if the database file exists and has data
   ```bash
   ls -la data.db
   ```

3. **Port conflicts**: Change the port in `api_server.py` if 8000 is in use

4. **CORS issues**: The API includes CORS middleware, but check browser console for issues

### Logs

The server provides detailed logging. Check the console output for:
- Database connection status
- API request/response details
- Error messages with stack traces

## API Examples

### Get Events Around Year 1000
```bash
curl "http://localhost:8000/api/events/around/1000?range_years=50"
```

### Search for "war" events
```bash
curl "http://localhost:8000/api/search?q=war&limit=10"
```

### Get Statistics
```bash
curl "http://localhost:8000/api/statistics"
```

### Paginated Timeline
```bash
curl "http://localhost:8000/api/timeline/paginated?start_year=0&end_year=500&limit=20"
```