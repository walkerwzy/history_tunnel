/**
 * Historical Timeline API - Node.js Backend
 * REST API for historical timeline visualization
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const { v4: uuid } = require('uuid');

const app = express();
const PORT = process.env.PORT || 8000;
const DB_PATH = './data.db';

// Database connection
const db = new Database(DB_PATH);

// CORS middleware
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['*'],
    credentials: true,
}));

// Request logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    try {
        res.json({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            memory: process.memoryUsage()
        });
    } catch (error) {
        console.error('Health check error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Get all historical events with pagination support
 * Query params: offset, limit, region, min_importance, start_year, end_year
 */
app.get('/api/events', async (req, res) => {
    try {
        const { offset = 0, limit = 100, region, min_importance, start_year, end_year } = req.query;

        const events = await db.getEventsPaginated({
            offset,
            limit,
            region,
            min_importance,
            start_year,
            end_year
        });

        const total = await db.getStatistics();

        res.json({
            events,
            metadata: {
                total: total.total,
                offset: parseInt(offset),
                limit: parseInt(limit)
            }
        });
    } catch (error) {
        console.error('Get events error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Get timeline events with pagination
 * Query params: start_year, end_year, region, min_importance, offset, limit
 */
app.get('/api/timeline/paginated', async (req, res) => {
    try {
        const { start_year, end_year, region, min_importance, offset = 0, limit = 50 } = req.query;

        const events = await db.getEventsPaginated({
            start_year,
            end_year,
            region,
            min_importance,
            offset,
            limit
        });

        res.json({ events });
    } catch (error) {
        console.error('Timeline paginated error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Get events around a specific year
 * Query params: year, range_years, region, min_importance, limit
 */
app.get('/api/events/around/:year', async (req, res) => {
    try {
        const { year, range_years = 50, region, min_importance, limit = 100 } = req.query;

        const startYear = parseInt(year) - parseInt(range_years);
        const endYear = parseInt(year) + parseInt(range_years);

        const events = await db.getEventsPaginated({
            start_year: startYear,
            end_year: endYear,
            region,
            min_importance,
            offset: 0,
            limit
        });

        const total = await db.getEventsPaginated({
            start_year: startYear,
            end_year: endYear,
            region
        });

        res.json({
            events,
            metadata: {
                target_year: parseInt(year),
                year_range: range_years,
                count: events.length
            }
        });
    } catch (error) {
        console.error('Events around year error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Compare events between regions at a specific year
 * Query params: year, range_years
 */
app.get('/api/compare/:year', async (req, res) => {
    try {
        const { year, range_years = 20 } = req.query;

        const startYear = parseInt(year) - parseInt(range_years);
        const endYear = parseInt(year) + parseInt(range_years);

        const [europeanEvents, europeanTotal] = await Promise.all([
            db.getEventsPaginated({
                start_year: startYear,
                end_year: endYear,
                region: 'European',
                limit: 50
            }),
            db.getStatistics().then(stats => stats.events_by_region?.European || 0)
        ]);

        const [chineseEvents, chineseTotal] = await Promise.all([
            db.getEventsPaginated({
                start_year: startYear,
                end_year: endYear,
                region: 'Chinese',
                limit: 50
            }),
            db.getStatistics().then(stats => stats.events_by_region?.Chinese || 0)
        ]);

        res.json({
            target_year: parseInt(year),
            year_range: range_years,
            european: {
                events: europeanEvents,
                count: europeanTotal
            },
            chinese: {
                events: chineseEvents,
                count: chineseTotal
            },
            comparison: {
                european_total: europeanTotal,
                chinese_total: chineseTotal,
                total_events: europeanTotal + chineseTotal
            }
        });
    } catch (error) {
        console.error('Compare regions error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Search events by keyword
 * Query params: q (search query), region, limit
 */
app.get('/api/search', async (req, res) => {
    try {
        const { q, region, limit = 50 } = req.query;

        if (!q || q.length < 1) {
            return res.status(400).json({
                error: 'Query parameter "q" is required and must be at least 1 character'
            });
        }

        const events = await db.searchEvents(q, {
            region,
            limit
        });

        res.json({
            events,
            metadata: {
                query: q,
                count: events.length
            }
        });
    } catch (error) {
        console.error('Search events error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Get statistics about historical timeline data
 */
app.get('/api/statistics', async (req, res) => {
    try {
        const stats = await db.getStatistics();

        res.json(stats);
    } catch (error) {
        console.error('Statistics error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * 404 handler - serve frontend file
 */
app.get('*', (req, res) => {
    const filePath = 'timeline_visualization.html';

    res.sendFile(filePath, (err) => {
        if (err) {
            console.error('Error serving frontend:', err);
            res.status(404).json({
                error: 'Frontend file not found. Please ensure timeline_visualization.html is in the same directory as server.js'
            });
        } else {
            console.log('Serving frontend file:', filePath);
        }
    });
});

/**
 * Start server
 */
app.listen(PORT, () => {
    console.log(`Historical Timeline API running on port ${PORT}`);
    console.log(`Frontend accessible at http://localhost:${PORT}/timeline_visualization.html`);
    console.log(`API Documentation:`);
    console.log(`  GET  /api/events              - Get all events (paginated)`);
    console.log(`  GET  /api/timeline/paginated - Get timeline events (paginated)`);
    console.log(`  GET  /api/events/around/:year  - Get events around a year`);
    console.log(`  GET  /api/compare/:year      - Compare regions at a year`);
    console.log(`  GET  /api/search              - Search events by keyword`);
    console.log(`  GET  /api/statistics        - Get statistics`);
    console.log(`  GET  *                      - Serve frontend`);
});

/**
 * Graceful shutdown
 */
process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: shutting down gracefully');
    db.close();
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT signal received: shutting down gracefully');
    db.close();
    process.exit(0);
});