# Frontend Visualization Design - Stage 5

## Visual Requirements

### Core Concept: Time Tunnel (Wormhole Effect)
- **Metaphor**: Traveling through history as if falling through a wormhole
- **Perspective**: First-person view moving forward/backward in time
- **Navigation**: Mouse wheel scroll controls time travel speed and direction
- **Visual**: 3D tunnel effect with events as "stars" in the tunnel

### Layout Design
```
┌─────────────────────────────────────────────────────────────────┐
│                                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │              [Time Tunnel Visualization]                   │ │
│  │         (3D perspective, scrolling events)               │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌────────────────────┐  ┌────────────────────┐         │
│  │  European Period  │  │  Chinese Period   │         │
│  │  (Left Panel)     │  │  (Right Panel)    │         │
│  │                   │  │                   │         │
│  │  Year: 1945      │  │  Year: 1945      │         │
│  │  Period: WWII     │  │  Period: 民国    │         │
│  │  Events: 12      │  │  Events: 3        │         │
│  └────────────────────┘  └────────────────────┘         │
│                                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Event Details Card (shown on click)                 │ │
│  │  Event: WWII                                       │ │
│  │  Year: 1939-1945                                 │ │
│  │  Description: ...                                    │ │
│  │  Impact: ...                                        │ │
│  │  Category: Military                                   │ │
│  │  Importance: 9/10                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                           │
│  Controls:                                                │
│  - Mouse wheel: Navigate time                              │
│  - Click event: Show details                              │
│  - Search box: Filter events                              │
│  - Zoom buttons: Change view scale                         │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Architecture

### Frontend Stack
```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                      │
├─────────────────────────────────────────────────────────────┤
│ HTML5 + CSS3 + JavaScript                            │
│                                                           │
│  Libraries:                                               │
│  - Three.js (r128): 3D tunnel visualization          │
│  - D3.js (v7): Data binding and transitions          │
│  - GSAP: Smooth animations                              │
├─────────────────────────────────────────────────────────────┤
│                    API Layer                               │
│  - RESTful API for data fetching                          │
│  - WebSocket for real-time updates (optional)               │
│  - Client-side caching (localStorage)                        │
└─────────────────────────────────────────────────────────────┘
```

### Backend Architecture
```
┌─────────────────────────────────────────────────────────────┐
│              Python Backend (Flask/FastAPI)                │
├─────────────────────────────────────────────────────────────┤
│ API Endpoints:                                            │
│  - GET /api/timeline/paginated          → Paginated events │
│  - GET /api/events/around/:year        → Events around year│
│  - GET /api/compare/:year               → Cross-regional  │
│  - GET /api/search                       → Keyword search  │
│  - GET /api/statistics                    → Statistics    │
├─────────────────────────────────────────────────────────────┤
│ Data Layer:                                              │
│  - EnhancedDatabaseManager (SQLite/PostgreSQL)             │
│  - Caching layer (Redis/Memcached for performance)        │
│  - Pre-fetching for adjacent time ranges                  │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Basic 3D Tunnel (Three.js)
1. Setup Three.js scene with perspective camera
2. Create cylindrical tunnel geometry
3. Add particle system for "stars" effect
4. Implement continuous animation loop
5. Add mouse wheel event listener for navigation

### Phase 2: Data Integration
1. Connect to backend API
2. Load events for current time window
3. Map events to tunnel particles
4. Implement data binding (events → visual elements)
5. Add color coding by region (Europe: blue, China: red)

### Phase 3: Period Panels
1. Create left/right overlay panels
2. Fetch period info for current year
3. Display European period (left)
4. Display Chinese period (right)
5. Add smooth transitions on year change

### Phase 4: Event Interaction
1. Raycasting for click detection
2. Show event details card on click
3. Implement close functionality
4. Add hover effects (particle highlights)
5. Size particles by importance level

### Phase 5: Navigation & Controls
1. Implement scroll-based navigation
2. Add timeline slider control
3. Add search box
4. Add zoom in/out buttons
5. Add play/pause for automatic time travel

### Phase 6: Performance Optimization
1. Implement object pooling for particles
2. Use instanced mesh for many particles
3. Add client-side caching
4. Implement pre-fetching for adjacent ranges
5. Lazy load events based on viewport

## Data Flow

```
User Action (Scroll) → Update current year
                           ↓
                    Query backend API
                           ↓
                Fetch events for new time window
                           ↓
                 Update Three.js particles
                           ↓
                 Update period panels (L/R)
                           ↓
                Animate transitions
```

## Visual Design Details

### Color Scheme
```
European Events:  #4169E1 (Blue)
Chinese Events:    #DC143C (Crimson)
Military:           #FF6B6B (Red)
Political:          #4ECDC4 (Green)
Economic:           #FFD93D (Yellow)
Cultural:           #A66CFF (Purple)
Technology:         #45B7D1 (Teal)
```

### Particle Size Mapping
```
Importance Level 1-3:   2px radius
Importance Level 4-6:   4px radius
Importance Level 7-8:   8px radius
Importance Level 9-10:  12px radius
```

### Tunnel Animation
```
- Particles move toward camera (forward time)
- Speed proportional to scroll speed
- Parallax effect for depth perception
- Glow effect on high-importance events
- Trail effects for continuous time flow
```

## Performance Targets
- **Frame Rate**: 60 FPS minimum
- **Initial Load**: < 3 seconds
- **Page Loads**: < 1 second (with caching)
- **Events on Screen**: 500-1000 particles
- **Smooth Transitions**: < 200ms response time

## Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- WebGL support required

## Accessibility
- Keyboard navigation (arrow keys for time travel)
- Screen reader support for event cards
- High contrast mode
- Reduced motion option
