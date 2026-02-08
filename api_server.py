"""
FastAPI Backend for Historical Timeline Visualization

This module provides REST API endpoints for the timeline visualization frontend.
"""

from fastapi import FastAPI, HTTPException, Query, Request, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Dict, Optional, Literal
from enhanced_database_manager import EnhancedDatabaseManager
from pydantic import BaseModel, Field
import os
import csv
import io
from datetime import datetime
import hashlib

# Pydantic models for admin API
class EventBase(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=255)
    start_year: int
    end_year: Optional[int] = None
    key_figures: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    region: Literal["Chinese", "European"] = "Chinese"
    importance_level: int = Field(default=5, ge=1, le=10)
    source: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    event_name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    key_figures: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    region: Optional[Literal["Chinese", "European"]] = None
    importance_level: Optional[int] = Field(None, ge=1, le=10)
    source: Optional[str] = None

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
TIMELINE_FILE = os.path.join(SCRIPT_DIR, "timeline.html")
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
ADMIN_FILE = os.path.join(SCRIPT_DIR, "admin.html")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Security setup
security = HTTPBasic()
# Development mode flag - set to True to skip auth
DEV_MODE = True

async def verify_admin_credentials():
    """
    Verify admin credentials.
    For development: always return True (no auth required)
    Production: username + yyyyMMdd MD5 hash as password
    """
    # DEVELOPMENT MODE: Skip auth check
    if DEV_MODE:
        return True
    
    # PRODUCTION MODE: Use HTTP Basic Auth
    from fastapi import Depends
    from fastapi.security import HTTPBasicCredentials
    credentials: HTTPBasicCredentials = Depends(security)
    today_str = datetime.now().strftime("%Y%m%d")
    expected_password = hashlib.md5(f"{credentials.username}{today_str}".encode()).hexdigest()
    if credentials.password != expected_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

@app.get("/")
async def root():
    """Serve the main timeline visualization."""
    if os.path.exists(FRONTEND_FILE):
        with open(FRONTEND_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return {
            "message": "Historical Timeline API",
            "version": "1.0.0",
            "endpoints": [
                "/timeline",
                "/api/events",
                "/api/timeline/paginated",
                "/api/events/around/{year}",
                "/api/compare/{year}",
                "/api/search",
                "/api/statistics"
            ],
            "note": "Frontend file not found. Please ensure timeline_visualization.html is in the same directory as api_server.py"
        }

@app.get("/timeline")
async def serve_timeline():
    """Serve new dual timeline visualization."""
    if os.path.exists(TIMELINE_FILE):
        return FileResponse(TIMELINE_FILE, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Timeline file not found")

@app.get("/admin")
async def serve_admin():
    """Serve admin dashboard."""
    if os.path.exists(ADMIN_FILE):
        return FileResponse(ADMIN_FILE, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Admin file not found")

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

@app.get("/login/{uname}")
async def login_md5(uname: str):
    """
    Generate MD5 hash for login.
    Returns MD5(username + yyyyMMdd format date).
    """
    from datetime import datetime
    today_str = datetime.now().strftime("%Y%m%d")
    input_str = f"{uname}{today_str}"
    hash_str = hashlib.md5(input_str.encode()).hexdigest()
    return hash_str
    # return {
    #     "username": uname,
    #     "date": today_str,
    #     "input": input_str,
    #     "md5": hash_str
    # }

# ==================== ADMIN API ENDPOINTS ====================

@app.get("/admin/auth")
async def admin_auth_check():
    """Check if admin is authenticated."""
    await verify_admin_credentials()
    return {"authenticated": True, "mode": "development"}

@app.get("/admin/api/events")
async def admin_list_events(
    region: Optional[str] = Query(None, description="Region filter"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000)
):
    """List events with pagination for admin."""
    await verify_admin_credentials()
    try:
        events, metadata = db_manager.get_events_paginated(
            region=region, offset=offset, limit=limit
        )
        return {"events": events, "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/admin/api/events/{event_id}")
async def admin_get_event(event_id: int):
    """Get a single event by ID."""
    await verify_admin_credentials()
    event = db_manager.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/admin/api/events", status_code=status.HTTP_201_CREATED)
async def admin_create_event(event: EventCreate):
    """Create a new event."""
    await verify_admin_credentials()
    # Check for duplicates
    if db_manager.check_duplicate_event(event.event_name, event.start_year):
        raise HTTPException(status_code=409, detail="Event with same name and year already exists")
    
    event_dict = event.model_dump()
    event_id = db_manager.insert_event(event_dict)
    
    if event_id:
        return {"id": event_id, "message": "Event created successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create event")

@app.put("/admin/api/events/{event_id}")
async def admin_update_event(event_id: int, event: EventUpdate):
    """Update an existing event."""
    await verify_admin_credentials()
    # Check if event exists
    existing = db_manager.get_event_by_id(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check for duplicates if name/year changed
    update_data = event.model_dump(exclude_unset=True)
    if "event_name" in update_data or "start_year" in update_data:
        new_name = update_data.get("event_name", existing["event_name"])
        new_year = update_data.get("start_year", existing["start_year"])
        if db_manager.check_duplicate_event(new_name, new_year, exclude_id=event_id):
            raise HTTPException(status_code=409, detail="Event with same name and year already exists")
    
    success = db_manager.update_event(event_id, update_data)
    if success:
        return {"message": "Event updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update event")

@app.delete("/admin/api/events/{event_id}")
async def admin_delete_event(event_id: int):
    """Delete an event."""
    await verify_admin_credentials()
    success = db_manager.delete_event(event_id)
    if success:
        return {"message": "Event deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Event not found")

@app.get("/admin/api/template")
async def admin_download_template():
    """Download TSV template for batch upload."""
    headers = ["event_name", "start_year", "end_year", "key_figures", "description", 
               "impact", "category", "region", "importance_level", "source"]
    example = ["示例事件", "2024", "2025", "关键人物", "事件描述", "事件影响", 
               "政治", "Chinese", "8", "https://example.com"]
    
    content = "\t".join(headers) + "\n" + "\t".join(example) + "\n"
    
    return Response(
        content=content,
        media_type="text/tab-separated-values",
        headers={"Content-Disposition": "attachment; filename=events_template.tsv"}
    )

@app.post("/admin/api/events/batch")
async def admin_batch_upload(file: UploadFile = File(...)):
    """Batch upload events from TSV file."""
    await verify_admin_credentials()
    if not file.filename or not file.filename.endswith('.tsv'):
        raise HTTPException(status_code=400, detail="Only TSV files are allowed")
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    reader = csv.DictReader(io.StringIO(content_str), delimiter='\t')
    
    success_count = 0
    failed_rows = []
    duplicate_rows = []
    
    for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
        try:
            # Validate required fields
            if not row.get('event_name') or not row.get('start_year'):
                failed_rows.append({"row": row_num, "error": "Missing required fields: event_name, start_year"})
                continue
            
            # Parse data
            event_data = {
                "event_name": row['event_name'],
                "start_year": int(row['start_year']),
                "end_year": int(row['end_year']) if row.get('end_year') else None,
                "key_figures": row.get('key_figures', ''),
                "description": row.get('description', ''),
                "impact": row.get('impact', ''),
                "category": row.get('category', ''),
                "region": row.get('region', 'Chinese'),
                "importance_level": int(row['importance_level']) if row.get('importance_level') else 5,
                "source": row.get('source', '')
            }
            
            # Check for duplicates
            if db_manager.check_duplicate_event(event_data['event_name'], event_data['start_year']):
                duplicate_rows.append({"row": row_num, "event_name": event_data['event_name']})
                continue
            
            # Insert event
            event_id = db_manager.insert_event(event_data)
            if event_id:
                success_count += 1
            else:
                failed_rows.append({"row": row_num, "error": "Database insertion failed"})
                
        except ValueError as e:
            failed_rows.append({"row": row_num, "error": f"Invalid data format: {str(e)}"})
        except Exception as e:
            failed_rows.append({"row": row_num, "error": str(e)})
    
    return {
        "success_count": success_count,
        "failed_count": len(failed_rows),
        "duplicate_count": len(duplicate_rows),
        "failed_rows": failed_rows,
        "duplicate_rows": duplicate_rows
    }

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
    print("Admin page at: http://localhost:8000/admin")
    print("Frontend should load from: http://localhost:8000/static/timeline_visualization.html")

    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
