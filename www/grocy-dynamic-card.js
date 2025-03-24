// Save this as /config/www/grocy-dynamic-card.js
class GrocyDynamicCard extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.chores = [];
      this.filters = {
        territorio: 'All',
        luogo_di_lavoro: 'All',
        assigned_to: 'All'
      };
    }
  
    set hass(hass) {
      if (!this.config) return;
      this._hass = hass;
      
      // Update if we haven't rendered yet
      if (!this.hasRendered) {
        this.renderCard();
      }
    }
  
    setConfig(config) {
      this.config = config;
      this.hasRendered = false;
      
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 16px;">
            <h2>${config.title || 'Grocy Chores'}</h2>
            <div id="filters" style="margin-bottom: 16px;"></div>
            <div id="content">Loading chores...</div>
          </div>
          <style>
            select {
              padding: 8px;
              border-radius: 4px;
              border: 1px solid #ccc;
              background-color: var(--card-background-color, white);
              color: var(--primary-text-color, black);
              width: 100%;
            }
            .filter-row {
              display: flex;
              gap: 8px;
              margin-bottom: 8px;
            }
            .filter-item {
              flex: 1;
            }
            .filter-label {
              display: block;
              margin-bottom: 4px;
              font-size: 0.9em;
              color: var(--secondary-text-color, gray);
            }
            .chore-card {
              margin-bottom: 16px;
              padding: 12px;
              border-left: 4px solid var(--primary-color, #03a9f4);
              background: var(--card-background-color, #f5f5f5);
              border-radius: 4px;
            }
            .chore-title {
              font-weight: bold; 
              font-size: 1.1em;
              margin-bottom: 8px;
            }
            .chore-meta {
              display: flex;
              justify-content: space-between;
              margin-bottom: 8px;
            }
            .chore-location {
              margin-top: 8px;
            }
            .task-tag {
              display: inline-block;
              padding: 2px 6px;
              border-radius: 4px;
              background-color: var(--accent-color, #ff9800);
              color: white;
              font-size: 0.8em;
              margin-left: 8px;
            }
            .date-overdue {
              color: var(--error-color, #f44336);
              font-weight: bold;
            }
            .date-today {
              color: var(--warning-color, #ff9800);
              font-weight: bold;
            }
          </style>
        </ha-card>
      `;
      
      // Load data when config is set
      this.loadData();
    }
  
    async loadData() {
      try {
        // Fetch the summary and index files from the processed directory
        const summaryResponse = await fetch("/local/grocy_processed/summary.json");
        const indexResponse = await fetch("/local/grocy_processed/index.json");
        
        if (!summaryResponse.ok || !indexResponse.ok) {
          this.renderError("Could not load summary or index files");
          return;
        }
        
        const summary = await summaryResponse.json();
        const index = await indexResponse.json();
        
        // Load all chores based on the index
        const chores = [];
        for (const id in index) {
          try {
            const choreResponse = await fetch(`/local/grocy_processed/chore_${id}.json`);
            if (choreResponse.ok) {
              const chore = await choreResponse.json();
              chores.push(chore);
            }
          } catch (e) {
            console.error(`Error loading chore ${id}:`, e);
          }
        }
        
        this.chores = chores;
        this.renderCard();
      } catch (err) {
        this.renderError(`Error loading data: ${err.message}`);
      }
    }
    
    renderError(message) {
      const content = this.shadowRoot.querySelector('#content');
      if (content) {
        content.innerHTML = `<div style="color: var(--error-color, red); padding: 8px;">${message}</div>`;
      }
    }
    
    getFilterOptions() {
      // Extract unique values for filters
      const territorios = ['All', ...new Set(this.chores.map(c => c.territorio).filter(Boolean))];
      const locations = ['All', ...new Set(this.chores.map(c => c.luogo_di_lavoro).filter(Boolean))];
      const people = ['All', ...new Set(this.chores.map(c => c.assigned_to).filter(Boolean))];
      
      return { territorios, locations, people };
    }
    
    renderFilters() {
      const filtersDiv = this.shadowRoot.querySelector('#filters');
      if (!filtersDiv) return;
      
      const { territorios, locations, people } = this.getFilterOptions();
      
      filtersDiv.innerHTML = `
        <div class="filter-row">
          <div class="filter-item">
            <label class="filter-label">Territory</label>
            <select id="territorio-filter">
              ${territorios.map(t => 
                `<option value="${t}" ${this.filters.territorio === t ? 'selected' : ''}>${t}</option>`
              ).join('')}
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">Location</label>
            <select id="location-filter">
              ${locations.map(l => 
                `<option value="${l}" ${this.filters.luogo_di_lavoro === l ? 'selected' : ''}>${l}</option>`
              ).join('')}
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">Person</label>
            <select id="person-filter">
              ${people.map(p => 
                `<option value="${p}" ${this.filters.assigned_to === p ? 'selected' : ''}>${p}</option>`
              ).join('')}
            </select>
          </div>
        </div>
      `;
      
      // Add event listeners
      const territorioFilter = this.shadowRoot.querySelector('#territorio-filter');
      const locationFilter = this.shadowRoot.querySelector('#location-filter');
      const personFilter = this.shadowRoot.querySelector('#person-filter');
      
      if (territorioFilter) {
        territorioFilter.addEventListener('change', (e) => {
          this.filters.territorio = e.target.value;
          this.renderChores();
        });
      }
      
      if (locationFilter) {
        locationFilter.addEventListener('change', (e) => {
          this.filters.luogo_di_lavoro = e.target.value;
          this.renderChores();
        });
      }
      
      if (personFilter) {
        personFilter.addEventListener('change', (e) => {
          this.filters.assigned_to = e.target.value;
          this.renderChores();
        });
      }
    }
    
    renderChores() {
      const content = this.shadowRoot.querySelector('#content');
      if (!content) return;
      
      // Apply filters
      const filteredChores = this.chores.filter(chore => {
        if (this.filters.territorio !== 'All' && chore.territorio !== this.filters.territorio) return false;
        if (this.filters.luogo_di_lavoro !== 'All' && chore.luogo_di_lavoro !== this.filters.luogo_di_lavoro) return false;
        if (this.filters.assigned_to !== 'All' && chore.assigned_to !== this.filters.assigned_to) return false;
        return true;
      });
      
      const choresHtml = filteredChores.map(chore => {
        // Determine date class based on dueStatus
        let dateClass = '';
        if (chore.dueStatus === 'overdue') {
          dateClass = 'date-overdue';
        } else if (chore.dueStatus === 'today') {
          dateClass = 'date-today';
        }
        
        return `
          <div class="chore-card">
            <div class="chore-title">
              ${chore.name || 'Unnamed'}
              ${chore.type === 'task' ? '<span class="task-tag">Task</span>' : ''}
            </div>
            <div class="chore-meta">
              <span class="${dateClass}">📅 ${chore.date || 'No date'}</span>
              <span>👤 ${chore.assigned_to || 'Unassigned'}</span>
            </div>
            <div class="chore-location">
              <div>🏠 Territory: ${chore.territorio || 'Unknown'}</div>
              <div>📍 Location: ${chore.luogo_di_lavoro || 'Unknown'}</div>
            </div>
            ${chore.description ? `<div style="margin-top: 8px; font-style: italic;">${chore.description}</div>` : ''}
          </div>
        `;
      }).join('');
      
      content.innerHTML = filteredChores.length ? choresHtml : 'No chores found with current filters';
    }
    
    renderCard() {
      // Render filters first
      this.renderFilters();
      
      // Then render chores
      this.renderChores();
      
      this.hasRendered = true;
    }
  
    getCardSize() {
      return 1 + (this.chores ? Math.ceil(this.chores.length / 2) : 0);
    }
  }
  
  customElements.define('grocy-dynamic-card', GrocyDynamicCard);
  
  // Register with Home Assistant
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "grocy-dynamic-card",
    name: "Grocy Dynamic Card",
    description: "A card to display Grocy chores with dynamic data and filtering"
  });