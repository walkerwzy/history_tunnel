#!/bin/bash

# Historical Timeline API Server Startup Script

echo "🚀 Starting Historical Timeline API Server..."
echo "============================================"

# Create database tables if needed
echo "🗄️  Setting up database..."
python -c "
from enhanced_database_manager import EnhancedDatabaseManager
db = EnhancedDatabaseManager()
db.create_tables()
print('Database tables ready!')
"

# Start the API server
echo "🌐 Starting FastAPI server..."
echo "📡 API will be available at: http://localhost:8000"
echo "🎨 Frontend: Open timeline_visualization.html in browser"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python api_server.py