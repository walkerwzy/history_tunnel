"""
FastAPI Backend for Historical Timeline Visualization

This module provides REST API endpoints for the timeline visualization frontend.
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
from enhanced_database_manager import EnhancedDatabaseManager
import os

app = FastAPI(
    title="Historical Timeline API",
    description="API for historical timeline visualization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database manager
db_manager = EnhancedDatabaseManager()

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FILE = os.path.join(SCRIPT_DIR, "timeline_visualization.html")

@app.get("/")
async def root():
    """Serve the frontend timeline visualization."""
    if os.path.exists(FRONTEND_FILE):
        with open(FRONTEND_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return {
            "message": "Historical Timeline API",
            "version": "1.0.0",
            "endpoints": [
                "/api/events",
                "/api/timeline/paginated",
                "/api/events/around/{year}",
                "/api/compare/{year}",
                "/api/search",
                "/api/statistics"
            ],
            "note": "Frontend file not found. Please ensure timeline_visualization.html is in the same directory as api_server.py"
        }

@app.get("/api/events")
async def get_all_events():
    """Get all historical events (for frontend loading)."""
    try:
        events, metadata = db_manager.get_events_paginated(
            offset=0,
            limit=10000  # Large limit to get all events
        )
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/timeline/paginated")
async def get_timeline_paginated(
    start_year: Optional[int] = Query(None, description="Start year filter"),
    end_year: Optional[int] = Query(None, description="End year filter"),
    region: Optional[str] = Query(None, description="Region filter (European/Chinese)"),
    min_importance: Optional[int] = Query(None, description="Minimum importance level"),
    offset: int = Query(0, description="Pagination offset", ge=0),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=200)
):
    """Get events with pagination support (for scrolling timeline)."""
    try:
        events, metadata = db_manager.get_events_paginated(
            start_year=start_year,
            end_year=end_year,
            region=region,
            min_importance=min_importance,
            offset=offset,
            limit=limit
        )
        return {
            "events": events,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/events/around/{year}")
async def get_events_around_year(
    year: int,
    range_years: int = Query(50, description="Years range around the target year", ge=1, le=500),
    region: Optional[str] = Query(None, description="Region filter"),
    min_importance: Optional[int] = Query(None, description="Minimum importance level"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=500)
):
    """Get events around a specific year."""
    try:
        start_year = year - range_years
        end_year = year + range_years

        events, metadata = db_manager.get_events_paginated(
            start_year=start_year,
            end_year=end_year,
            region=region,
            min_importance=min_importance,
            offset=0,
            limit=limit
        )

        return {
            "events": events,
            "metadata": metadata,
            "target_year": year,
            "year_range": range_years
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/compare/{year}")
async def compare_regions_at_year(
    year: int,
    range_years: int = Query(20, description="Years range for comparison", ge=1, le=100)
):
    """Compare events between regions at a specific year."""
    try:
        start_year = year - range_years
        end_year = year + range_years

        # Get European events
        european_events, euro_metadata = db_manager.get_events_paginated(
            start_year=start_year,
            end_year=end_year,
            region="European",
            offset=0,
            limit=50
        )

        # Get Chinese events
        chinese_events, china_metadata = db_manager.get_events_paginated(
            start_year=start_year,
            end_year=end_year,
            region="Chinese",
            offset=0,
            limit=50
        )

        return {
            "target_year": year,
            "year_range": range_years,
            "european": {
                "events": european_events,
                "count": euro_metadata["total"]
            },
            "chinese": {
                "events": chinese_events,
                "count": china_metadata["total"]
            },
            "comparison": {
                "european_total": euro_metadata["total"],
                "chinese_total": china_metadata["total"],
                "total_events": euro_metadata["total"] + china_metadata["total"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/search")
async def search_events(
    q: str = Query(..., description="Search query", min_length=1),
    region: Optional[str] = Query(None, description="Region filter"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=200)
):
    """Search events by keyword in name, description, or key figures."""
    try:
        events, metadata = db_manager.search_events(
            query=q,
            region=region,
            limit=limit
        )

        return {
            "events": events,
            "metadata": metadata,
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/statistics")
async def get_statistics():
    """Get statistics about the historical timeline data."""
    try:
        stats = db_manager.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn

    # Create database tables if they don't exist
    try:
        db_manager.create_tables()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

    # Start server
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("Frontend should load from: http://localhost:8000/static/timeline_visualization.html")

    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )