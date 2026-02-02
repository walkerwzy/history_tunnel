class TimelineApp {
    constructor() {
        this.timelineTrack = document.getElementById('timelineTrack');
        this.allEvents = [];
        this.minYear = -3000;
        this.maxYear = 2026;
        this.currentActiveIndex = -1;
        
        this.init();
    }

    async init() {
        await this.loadEvents();
        if (this.allEvents.length > 0) {
            this.renderTimeline();
            this.setupScrollListener();
            setTimeout(() => {
                this.setInitialScrollPosition();
            }, 100);
        } else {
            this.showError('Failed to load events. Please check if the API server is running.');
        }
    }

    async loadEvents() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch('/api/events', {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const events = await response.json();
            
            this.allEvents = events.map(event => ({
                year: event.start_year,
                name: event.event_name,
                description: event.description,
                impact: event.impact || '',
                key_figures: event.key_figures || '',
                category: event.category || '',
                region: event.region || 'European',
                importance_level: event.importance_level || 5,
                end_year: event.end_year
            }));
            
            this.allEvents.sort((a, b) => a.year - b.year);
            
            if (this.allEvents.length > 0) {
                this.minYear = this.allEvents[0].year;
                this.maxYear = this.allEvents[this.allEvents.length - 1].year;
            }
            
            console.log(`Loaded ${this.allEvents.length} events`);
            
        } catch (error) {
            console.error('Failed to load events:', error);
            this.allEvents = [];
        }
    }

    renderTimeline() {
        this.timelineTrack.innerHTML = '';
        
        this.allEvents.forEach((event, index) => {
            const isEuropean = event.region === 'European';
            const side = isEuropean ? 'left' : 'right';
            const categoryColor = this.getCategoryColor(event.category);
            const regionColor = isEuropean ? '#4ecdc4' : '#ff6b6b';
            
            const item = document.createElement('div');
            item.className = `timeline-item ${side}`;
            item.dataset.index = index;
            item.dataset.year = event.year;
            
            const yearDisplay = event.year < 0 
                ? `BC ${Math.abs(event.year)}` 
                : `AD ${event.year}`;
            
            item.innerHTML = `
                <div class="event-node">
                    <div class="event-year">${yearDisplay}</div>
                    <div class="event-name">${event.name}</div>
                    <div class="event-description">${event.description}</div>
                </div>
                <div class="event-marker" style="background: ${categoryColor}"></div>
                <div class="event-bubble">
                    <div class="bubble-content">
                        <div class="bubble-header">
                            <span class="bubble-region" style="color: ${regionColor}; border-color: ${regionColor}">${isEuropean ? 'EU' : 'CN'}</span>
                            <span class="bubble-year">${yearDisplay}</span>
                            <span class="bubble-category" style="color: ${categoryColor}; border-color: ${categoryColor}">${event.category}</span>
                        </div>
                        <div class="bubble-name">${event.name}</div>
                        <div class="bubble-desc">${event.description}</div>
                        ${event.impact ? `<div class="bubble-impact">影响: ${event.impact}</div>` : ''}
                        ${event.key_figures ? `<div class="bubble-figures">人物: ${event.key_figures}</div>` : ''}
                    </div>
                </div>
            `;
            
            this.timelineTrack.appendChild(item);
        });
        
        requestAnimationFrame(() => {
            this.adjustItemHeights();
        });
    }

    adjustItemHeights() {
        const items = document.querySelectorAll('.timeline-item');
        items.forEach(item => {
            const eventNode = item.querySelector('.event-node');
            if (eventNode) {
                const nodeHeight = eventNode.scrollHeight;
                const minHeight = Math.max(60, nodeHeight + 20);
                item.style.minHeight = `${minHeight}px`;
            }
        });
    }

    setInitialScrollPosition() {
        const firstItem = document.querySelector('.timeline-item');
        if (firstItem) {
            const rect = firstItem.getBoundingClientRect();
            const targetScroll = rect.top + window.scrollY - window.innerHeight / 2;
            window.scrollTo(0, Math.max(0, targetScroll));
        }
        this.updateDisplay();
    }

    setupScrollListener() {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.updateDisplay();
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    updateDisplay() {
        const scrollY = window.scrollY;
        const viewportCenter = scrollY + window.innerHeight / 2;
        
        const allItems = document.querySelectorAll('.timeline-item');
        let closestItem = null;
        let minDistance = Infinity;
        
        allItems.forEach(item => {
            const rect = item.getBoundingClientRect();
            const itemCenter = window.scrollY + rect.top + rect.height / 2;
            const distance = Math.abs(itemCenter - viewportCenter);
            
            if (distance < minDistance) {
                minDistance = distance;
                closestItem = item;
            }
        });
        
        if (closestItem) {
            const index = closestItem.dataset.index;
            
            if (this.currentActiveIndex !== index) {
                document.querySelectorAll('.timeline-item').forEach(el => {
                    el.classList.remove('active');
                });
                
                closestItem.classList.add('active');
                
                this.currentActiveIndex = index;
            }
        }
    }

    getCategoryColor(category) {
        const colors = {
            '军事': '#ff6b6b',
            '政治': '#4ecdc4',
            '文化': '#ffe66d',
            '经济': '#a8e6cf'
        };
        return colors[category] || '#888';
    }

    showError(message) {
        if (this.timelineTrack) {
            this.timelineTrack.innerHTML = `<div class="error">${message}</div>`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TimelineApp();
});
