class TimelineApp {
    constructor() {
        this.leftTimeline = document.getElementById('leftTimeline');
        this.rightTimeline = document.getElementById('rightTimeline');
        this.yearDisplay = document.getElementById('yearDisplay');
        this.leftEvent = document.getElementById('leftEvent');
        this.rightEvent = document.getElementById('rightEvent');
        
        this.allEvents = [];
        this.minYear = -3000;
        this.maxYear = 2026;
        
        this.init();
    }

    async init() {
        await this.loadEvents();
        if (this.allEvents.length > 0) {
            this.renderTimelines();
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

    renderTimelines() {
        const leftEvents = this.allEvents.filter(e => e.region === 'European');
        const rightEvents = this.allEvents.filter(e => e.region === 'Chinese');
        
        this.renderEvents(leftEvents, this.leftTimeline, 'European');
        this.renderEvents(rightEvents, this.rightTimeline, 'Chinese');
    }

    renderEvents(events, container, region) {
        container.innerHTML = '';
        
        events.forEach(event => {
            const eventEl = document.createElement('div');
            eventEl.className = 'event-item';
            eventEl.dataset.year = event.year;
            eventEl.dataset.region = region;
            eventEl.dataset.name = event.name;
            eventEl.dataset.desc = event.description;
            eventEl.dataset.impact = event.impact || '';
            eventEl.dataset.keyFigures = event.key_figures || '';
            eventEl.dataset.category = event.category || '';
            
            const yearDisplay = event.year < 0 
                ? `BC ${Math.abs(event.year)}` 
                : `AD ${event.year}`;
            
            eventEl.innerHTML = `
                <div class="event-year">${yearDisplay}</div>
                <div class="event-name">${event.name}</div>
                <div class="event-description">${event.description}</div>
            `;
            container.appendChild(eventEl);
        });
    }

    setInitialScrollPosition() {
        const firstEvent = document.querySelector('.event-item');
        if (firstEvent) {
            const firstEventRect = firstEvent.getBoundingClientRect();
            const targetScroll = firstEventRect.top + window.scrollY - window.innerHeight / 2;
            window.scrollTo(0, Math.max(0, targetScroll));
        }
        this.updateDisplay();
    }

    setupScrollListener() {
        window.addEventListener('scroll', () => {
            this.updateDisplay();
        });
    }

    updateDisplay() {
        const scrollY = window.scrollY;
        const viewportCenter = scrollY + window.innerHeight / 2;
        
        const leftEvent = this.findClosestEvent('European', viewportCenter);
        const rightEvent = this.findClosestEvent('Chinese', viewportCenter);

        let currentYear = 0;

        if (leftEvent || rightEvent) {
            const leftYear = leftEvent ? parseInt(leftEvent.dataset.year) : null;
            const rightYear = rightEvent ? parseInt(rightEvent.dataset.year) : null;

            if (leftYear !== null && rightYear !== null) {
                currentYear = Math.round((leftYear + rightYear) / 2);
            } else if (leftYear !== null) {
                currentYear = leftYear;
            } else {
                currentYear = rightYear;
            }
        } else {
            currentYear = this.minYear;
        }

        const formattedYear = currentYear > 0 ? `AD ${currentYear}` : `BC ${Math.abs(currentYear)}`;
        this.yearDisplay.textContent = formattedYear;

        this.updateEventDisplay(leftEvent, this.leftEvent, 'European');
        this.updateEventDisplay(rightEvent, this.rightEvent, 'Chinese');

        document.querySelectorAll('.event-item').forEach(el => el.classList.remove('active'));
        if (leftEvent) leftEvent.classList.add('active');
        if (rightEvent) rightEvent.classList.add('active');
    }

    findClosestEvent(region, position) {
        const events = document.querySelectorAll(`.event-item[data-region="${region}"]`);
        let closest = null;
        let minDistance = Infinity;

        events.forEach(event => {
            const rect = event.getBoundingClientRect();
            const eventCenterDocument = window.scrollY + rect.top + rect.height / 2;
            const distance = Math.abs(eventCenterDocument - position);

            if (distance < minDistance) {
                minDistance = distance;
                closest = event;
            }
        });

        return closest;
    }

    updateEventDisplay(eventEl, displayEl, region) {
        if (eventEl) {
            const year = eventEl.dataset.year;
            const name = eventEl.dataset.name;
            const desc = eventEl.dataset.desc;
            const impact = eventEl.dataset.impact;
            const keyFigures = eventEl.dataset.keyFigures;
            const category = eventEl.dataset.category;

            const formattedYear = year > 0 ? `AD ${year}` : `BC ${Math.abs(year)}`;
            const categoryColor = this.getCategoryColor(category);

            displayEl.innerHTML = `
                <div class="event-year">${formattedYear}</div>
                <div class="event-category" style="color: ${categoryColor}">${category}</div>
                <div class="event-name">${name}</div>
                <div class="event-desc">${desc}</div>
                ${impact ? `<div class="event-impact">影响: ${impact}</div>` : ''}
                ${keyFigures ? `<div class="event-figures">人物: ${keyFigures}</div>` : ''}
            `;
        } else {
            displayEl.innerHTML = '<span class="no-event">--</span>';
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
        if (this.leftTimeline) {
            this.leftTimeline.innerHTML = `<div class="error">${message}</div>`;
        }
        if (this.rightTimeline) {
            this.rightTimeline.innerHTML = `<div class="error">${message}</div>`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TimelineApp();
});
