class TimelineApp {
    constructor() {
        this.timelineTrack = document.getElementById('timelineTrack');
        this.allEvents = [];
        this.minYear = -3000;
        this.maxYear = 2026;
        this.currentActiveIndex = -1;
        this.currentYear = 0;
        this.userSelectedEventIndex = null;
        
        this.init();
    }

    async init() {
        await this.loadEvents();
        this.renderTimeline();
        this.setupScrollListener();
        this.setupSearchListener();
        this.updatePanelsByYear(this.currentYear);
        
        if (this.allEvents.length > 0) {
            setTimeout(() => {
                this.setInitialScrollPosition();
            }, 100);
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

    updatePanelsByYear(year) {
        this.currentYear = year;
        
        const europePeriod = HistoricalPeriods.getEuropePeriod(year);
        const chinaPeriod = HistoricalPeriods.getChinaPeriod(year);
        
        this.updatePeriodDisplay('europe', europePeriod);
        this.updatePeriodDisplay('china', chinaPeriod);
        
        this.updateEventDisplay('europe', null);
        this.updateEventDisplay('china', null);
    }

    updatePeriodDisplay(region, period) {
        const periodName = document.getElementById(`${region}PeriodName`);
        const periodRange = document.getElementById(`${region}PeriodRange`);
        
        periodName.textContent = period.name;
        const startDisplay = period.start < 0 ? `公元前${Math.abs(period.start)}年` : `${period.start}年`;
        const endDisplay = period.end < 0 ? `公元前${Math.abs(period.end)}年` : `${period.end}年`;
        periodRange.textContent = `${startDisplay} - ${endDisplay}`;
    }

    updateEventDisplay(region, event) {
        const separator = document.getElementById(`${region}Separator`);
        const noEventHint = document.getElementById(`${region}NoEvent`);
        const eventContent = document.getElementById(`${region}EventContent`);
        
        if (event) {
            separator.classList.remove('hidden');
            noEventHint.style.display = 'none';
            eventContent.style.display = 'flex';
            
            const yearEl = document.getElementById(`${region}EventYear`);
            const categoryEl = document.getElementById(`${region}EventCategory`);
            const titleEl = document.getElementById(`${region}EventTitle`);
            const descEl = document.getElementById(`${region}EventDesc`);
            const impactEl = document.getElementById(`${region}EventImpact`);
            const figuresEl = document.getElementById(`${region}EventFigures`);
            
            const yearDisplay = event.year < 0 
                ? `公元前${Math.abs(event.year)}年` 
                : `${event.year}年`;
            const categoryColor = this.getCategoryColor(event.category);
            
            yearEl.textContent = yearDisplay;
            categoryEl.textContent = event.category;
            categoryEl.style.color = categoryColor;
            categoryEl.style.borderColor = categoryColor;
            titleEl.textContent = event.name;
            descEl.textContent = event.description;
            
            if (event.impact) {
                impactEl.textContent = `影响：${event.impact}`;
                impactEl.style.display = 'block';
            } else {
                impactEl.style.display = 'none';
            }
            
            if (event.key_figures) {
                figuresEl.textContent = `人物：${event.key_figures}`;
                figuresEl.style.display = 'block';
            } else {
                figuresEl.style.display = 'none';
            }
        } else {
            separator.classList.add('hidden');
            noEventHint.style.display = 'block';
            eventContent.style.display = 'none';
        }
    }

    renderTimeline() {
        this.timelineTrack.innerHTML = '';
        
        this.allEvents.forEach((event, index) => {
            const isEuropean = event.region === 'European';
            const side = isEuropean ? 'left' : 'right';
            const categoryColor = this.getCategoryColor(event.category);
            
            const item = document.createElement('div');
            item.className = `timeline-item ${side}`;
            item.dataset.index = index;
            item.dataset.year = event.year;
            item.dataset.region = event.region;
            
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
            `;
            
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                this.userSelectedEventIndex = index;
                
                const year = parseInt(item.dataset.year);
                const region = item.dataset.region;
                
                document.querySelectorAll('.timeline-item').forEach(el => {
                    el.classList.remove('active', 'user-selected');
                });
                
                item.classList.add('active', 'user-selected');
                
                this.updatePanelsByYear(year);
                
                const selectedEvent = this.allEvents[index];
                if (selectedEvent) {
                    if (region === 'European') {
                        this.updateEventDisplay('europe', selectedEvent);
                        this.updateEventDisplay('china', null);
                    } else {
                        this.updateEventDisplay('china', selectedEvent);
                        this.updateEventDisplay('europe', null);
                    }
                }
            });
            
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
        
        this.timelineTrack.addEventListener('click', (e) => {
            if (e.target === this.timelineTrack) {
                this.userSelectedEventIndex = null;
                document.querySelectorAll('.timeline-item').forEach(el => {
                    el.classList.remove('user-selected');
                });
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
            const index = parseInt(closestItem.dataset.index);
            
            if (this.currentActiveIndex !== index) {
                // 如果之前有用户选中的事件，清除其样式并恢复自动更新
                if (this.userSelectedEventIndex !== null) {
                    const previousUserSelected = document.querySelector(`.timeline-item[data-index="${this.userSelectedEventIndex}"]`);
                    if (previousUserSelected) {
                        previousUserSelected.classList.remove('user-selected');
                    }
                    this.userSelectedEventIndex = null;
                }
                
                document.querySelectorAll('.timeline-item').forEach(el => {
                    el.classList.remove('active');
                });
                
                closestItem.classList.add('active');
                
                this.currentActiveIndex = index;
                
                const year = parseInt(closestItem.dataset.year);
                const region = closestItem.dataset.region;
                
                this.updatePanelsByYear(year);
                
                const event = this.allEvents[index];
                if (event) {
                    if (region === 'European') {
                        this.updateEventDisplay('europe', event);
                        this.updateEventDisplay('china', null);
                    } else {
                        this.updateEventDisplay('china', event);
                        this.updateEventDisplay('europe', null);
                    }
                }
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

    setupSearchListener() {
        const searchInput = document.getElementById('search-input');
        const searchResults = document.getElementById('search-results');
        let searchTimeout = null;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();

            clearTimeout(searchTimeout);

            if (query.length < 2) {
                searchResults.classList.remove('active');
                searchResults.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(() => {
                this.searchEvents(query);
            }, 300);
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('#search-container') && !e.target.closest('#search-results')) {
                searchResults.classList.remove('active');
            }
        });
    }

    searchEvents(query) {
        const searchResults = document.getElementById('search-results');

        const matches = this.allEvents.filter(event =>
            event.name.toLowerCase().includes(query.toLowerCase()) ||
            event.description.toLowerCase().includes(query.toLowerCase()) ||
            (event.key_figures && event.key_figures.toLowerCase().includes(query.toLowerCase()))
        );

        const limitedMatches = matches.slice(0, 10);

        if (limitedMatches.length === 0) {
            searchResults.innerHTML = '<div class="search-result-item" style="cursor: default; color: #888;">未找到相关事件</div>';
        } else {
            searchResults.innerHTML = limitedMatches.map(event => {
                const yearDisplay = event.year < 0 ? `公元前${Math.abs(event.year)}年` : `${event.year}年`;
                return `
                    <div class="search-result-item" data-event-year="${event.year}">
                        <div class="event-name">${event.name}</div>
                        <div class="event-info">${yearDisplay} · ${event.category} · ${event.region === 'European' ? '欧洲' : '中国'}</div>
                    </div>
                `;
            }).join('');

            searchResults.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    const year = parseInt(item.dataset.eventYear);
                    const event = this.allEvents.find(e => e.year === year);
                    const eventIndex = this.allEvents.findIndex(e => e.year === year);

                    if (event && eventIndex !== -1) {
                        const eventElement = document.querySelector(`.timeline-item[data-index="${eventIndex}"]`);
                        if (eventElement) {
                            eventElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            eventElement.click();
                        }
                    }

                    searchResults.classList.remove('active');
                    searchInput.value = '';
                });
            });
        }

        searchResults.classList.add('active');
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
