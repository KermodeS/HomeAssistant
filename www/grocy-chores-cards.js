class GrocyChoresCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.chores = [];
    this.filters = {
      territorio: 'All',
      luogo_di_lavoro: 'All',
      date: 'All',
      person: 'All',
      type: 'All'
    };
    this.filterOptions = {
      territorio: new Set(['All']),
      luogo_di_lavoro: new Set(['All']),
      date: new Set(['All']),
      person: new Set(['All']),
      type: new Set(['All', 'chore', 'task'])
    };
  }

  set hass(hass) {
    this._hass = hass;

    if (!this.config) {
      return;
    }

    // Only fetch data if we need to
    if (!this.chores.length) {
      this.fetchData();
    }
  }

  setConfig(config) {
    if (!config.entity && !config.test_data) {
      throw new Error('Please define an entity or test_data');
    }
    this.config = config;

    // Initial render with loading state
    this.render({ loading: true });
  }

  async fetchData() {
    try {
      let data;
      
      if (this.config.test_data) {
        // Use test data file
        const response = await fetch(`/local/grocy-dashboard/${this.config.test_data}`);
        data = await response.json();
      } else if (this.config.entity) {
        // Use entity data
        data = this._hass.states[this.config.entity].attributes.chores;
        if (typeof data === 'string') {
          data = JSON.parse(data);
        }
      }

      if (data && Array.isArray(data)) {
        this.chores = data;
        
        // Extract filter options
        this.extractFilterOptions();
        
        // Render with data
        this.render({ loading: false });
      } else {
        this.render({ error: 'Invalid data format' });
      }
    } catch (error) {
      console.error('Error fetching grocy data:', error);
      this.render({ error: `Error fetching data: ${error.message}` });
    }
  }

  extractFilterOptions() {
    // Reset filter options (keeping 'All')
    this.filterOptions = {
      territorio: new Set(['All']),
      luogo_di_lavoro: new Set(['All']),
      date: new Set(['All']),
      person: new Set(['All']),
      type: new Set(['All', 'chore', 'task'])
    };
    
    // Extract unique values from chores
    this.chores.forEach(chore => {
      if (chore.territorio) this.filterOptions.territorio.add(chore.territorio);
      if (chore.luogo_di_lavoro) this.filterOptions.luogo_di_lavoro.add(chore.luogo_di_lavoro);
      if (chore.date) {
        // Standardize date options
        if (chore.date.toLowerCase().includes('today')) {
          this.filterOptions.date.add('Today');
        } else if (chore.date.toLowerCase().includes('tomorrow')) {
          this.filterOptions.date.add('Tomorrow');
        } else if (chore.dueStatus === 'overdue') {
          this.filterOptions.date.add('Overdue');
        } else {
          this.filterOptions.date.add(chore.date);
        }
      }
      if (chore.assigned_to) this.filterOptions.person.add(chore.assigned_to);
    });
  }

  applyFilters(chores) {
    return chores.filter(chore => {
      // Check each filter
      if (this.filters.territorio !== 'All' && chore.territorio !== this.filters.territorio) return false;
      if (this.filters.luogo_di_lavoro !== 'All' && chore.luogo_di_lavoro !== this.filters.luogo_di_lavoro) return false;
      if (this.filters.person !== 'All' && chore.assigned_to !== this.filters.person) return false;
      if (this.filters.type !== 'All' && chore.type !== this.filters.type) return false;
      
      // Date filter needs special handling
      if (this.filters.date !== 'All') {
        if (this.filters.date === 'Today' && !chore.date.toLowerCase().includes('today')) return false;
        if (this.filters.date === 'Tomorrow' && !chore.date.toLowerCase().includes('tomorrow')) return false;
        if (this.filters.date === 'Overdue' && chore.dueStatus !== 'overdue') return false;
        if (!['Today', 'Tomorrow', 'Overdue'].includes(this.filters.date) && chore.date !== this.filters.date) return false;
      }
      
      return true;
    });
  }

  handleFilterChange(filterType, value) {
    this.filters[filterType] = value;
    this.render({ loading: false });
  }

  getDueStatusStyle(dueStatus) {
    switch (dueStatus) {
      case 'overdue':
        return 'color: var(--error-color, red);';
      case 'today':
        return 'color: var(--warning-color, orange);';
      case 'tomorrow':
        return 'color: var(--info-color, blue);';
      default:
        return 'color: var(--primary-text-color, black);';
    }
  }

  getIconForDueStatus(dueStatus) {
    switch (dueStatus) {
      case 'overdue':
        return '⚠️';
      case 'today':
        return '🕒';
      case 'tomorrow':
        return '📅';
      default:
        return '📆';
    }
  }

  render({ loading = false, error = null } = {}) {
    // Generate filter dropdowns
    const filterControls = `
      <div class="filter-controls">
        <div class="filter">
          <label for="type-filter">Type:</label>
          <select id="type-filter" @change="${e => this.handleFilterChange('type', e.target.value)}">
            ${Array.from(this.filterOptions.type).map(option => 
              `<option value="${option}" ${this.filters.type === option ? 'selected' : ''}>${option}</option>`
            ).join('')}
          </select>
        </div>
        <div class="filter">
          <label for="territorio-filter">Territory:</label>
          <select id="territorio-filter" @change="${e => this.handleFilterChange('territorio', e.target.value)}">
            ${Array.from(this.filterOptions.territorio).map(option => 
              `<option value="${option}" ${this.filters.territorio === option ? 'selected' : ''}>${option}</option>`
            ).join('')}
          </select>
        </div>
        <div class="filter">
          <label for="luogo-filter">Location:</label>
          <select id="luogo-filter" @change="${e => this.handleFilterChange('luogo_di_lavoro', e.target.value)}">
            ${Array.from(this.filterOptions.luogo_di_lavoro).map(option => 
              `<option value="${option}" ${this.filters.luogo_di_lavoro === option ? 'selected' : ''}>${option}</option>`
            ).join('')}
          </select>
        </div>
        <div class="filter">
          <label for="date-filter">Date:</label>
          <select id="date-filter" @change="${e => this.handleFilterChange('date', e.target.value)}">
            ${Array.from(this.filterOptions.date).map(option => 
              `<option value="${option}" ${this.filters.date === option ? 'selected' : ''}>${option}</option>`
            ).join('')}
          </select>
        </div>
        <div class="filter">
          <label for="person-filter">Person:</label>
          <select id="person-filter" @change="${e => this.handleFilterChange('person', e.target.value)}">
            ${Array.from(this.filterOptions.person).map(option => 
              `<option value="${option}" ${this.filters.person === option ? 'selected' : ''}>${option}</option>`
            ).join('')}
          </select>
        </div>
      </div>
    `;

    // Filtered chores
    const filteredChores = this.applyFilters(this.chores);
    
    // Generate chore list items
    const choreItems = filteredChores.map(chore => `
      <div class="chore-item ${chore.type === 'task' ? 'task' : 'chore'}">
        <div class="chore-header">
          <div class="chore-name">${chore.name}</div>
          <div class="chore-date" style="${this.getDueStatusStyle(chore.dueStatus)}">
            ${this.getIconForDueStatus(chore.dueStatus)} ${chore.date}
          </div>
        </div>
        <div class="chore-details">
          <div class="chore-assigned">Assigned to: ${chore.assigned_to}</div>
          <div class="chore-location">
            <span class="territorio">${chore.territorio}</span> • 
            <span class="luogo">${chore.luogo_di_lavoro}</span>
          </div>
          ${chore.description ? `<div class="chore-description">${chore.description}</div>` : ''}
        </div>
        <div class="chore-badge">${chore.type === 'task' ? 'TASK' : 'CHORE'}</div>
      </div>
    `).join('');

    const content = loading 
      ? '<div class="loading">Loading Grocy data...</div>'
      : error 
        ? `<div class="error">${error}</div>`
        : filteredChores.length 
          ? choreItems 
          : '<div class="empty">No chores match the selected filters</div>';

    const title = this.config.title || 'Grocy Chores';
    const count = filteredChores.length;

    // Combine it all
    this.shadowRoot.innerHTML = `
      <ha-card>
        <style>
          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            color: var(--primary-text-color);
          }
          .card-header .name {
            font-size: 1.2em;
            font-weight: 500;
          }
          .card-header .count {
            font-size: 1em;
            color: var(--secondary-text-color);
          }
          .filter-controls {
            display: flex;
            flex-wrap: wrap;
            padding: 0 16px 8px;
            gap: 8px;
            border-bottom: 1px solid var(--divider-color, #e8e8e8);
          }
          .filter {
            display: flex;
            flex-direction: column;
            min-width: 120px;
            flex: 1;
          }
          .filter label {
            font-size: 0.8em;
            color: var(--secondary-text-color);
            margin-bottom: 4px;
          }
          .filter select {
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid var(--divider-color, #e8e8e8);
            background-color: var(--card-background-color, white);
            color: var(--primary-text-color);
          }
          .chore-list {
            padding: 16px;
            overflow-y: auto;
            max-height: 500px;
          }
          .chore-item {
            margin-bottom: 12px;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            background-color: var(--card-background-color, white);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            position: relative;
          }
          .chore-item.task {
            border-left-color: var(--info-color, blue);
          }
          .chore-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
          }
          .chore-name {
            font-weight: 500;
            font-size: 1.1em;
          }
          .chore-date {
            white-space: nowrap;
            font-size: 0.9em;
          }
          .chore-details {
            font-size: 0.9em;
            color: var(--secondary-text-color);
          }
          .chore-assigned {
            margin-bottom: 4px;
          }
          .chore-location {
            margin-bottom: 4px;
          }
          .chore-description {
            margin-top: 8px;
            font-style: italic;
          }
          .chore-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            font-size: 0.7em;
            padding: 2px 6px;
            border-radius: 4px;
            background-color: var(--primary-color, #03a9f4);
            color: white;
          }
          .chore-item.task .chore-badge {
            background-color: var(--info-color, blue);
          }
          .loading, .error, .empty {
            padding: 32px 16px;
            text-align: center;
            color: var(--secondary-text-color);
          }
          .error {
            color: var(--error-color, red);
          }
        </style>
        <div class="card-header">
          <div class="name">${title}</div>
          <div class="count">${count} ${count === 1 ? 'item' : 'items'}</div>
        </div>
        ${filterControls}
        <div class="chore-list">
          ${content}
        </div>
      </ha-card>
    `;

    // Add event listeners for filter changes
    if (!loading && !error) {
      const filterElements = this.shadowRoot.querySelectorAll('select');
      filterElements.forEach(el => {
        el.addEventListener('change', (e) => {
          const filterType = el.id.split('-')[0];
          if (filterType === 'luogo') {
            this.handleFilterChange('luogo_di_lavoro', e.target.value);
          } else {
            this.handleFilterChange(filterType, e.target.value);
          }
        });
      });
    }
  }

  getCardSize() {
    return 1 + Math.ceil(this.chores.length / 2);
  }
}

customElements.define('grocy-chores-card', GrocyChoresCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "grocy-chores-card",
  name: "Grocy Chores Card",
  description: "Card to display and filter Grocy chores"
});