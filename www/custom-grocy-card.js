// Save as /config/www/custom-grocy-card.js
class CustomGrocyCard extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.chores = [];
      this.allChores = [];
      this.filters = {
        territory: 'All',
        location: 'All',
        person: 'All'
      };
    }
  
    set hass(hass) {
      this._hass = hass;
      if (this.config && this.firstRender) {
        this.loadData();
      }
    }
  
    setConfig(config) {
      if (!config.summary_entity || !config.index_entity) {
        throw new Error('Please define summary_entity and index_entity');
      }
      this.config = config;
      this.firstRender = true;
    }
  
    async loadData() {
      this.firstRender = false;
      if (!this._hass) return;
  
      try {
        const summaryEntity = this._hass.states[this.config.summary_entity];
        const indexEntity = this._hass.states[this.config.index_entity];
        
        if (!summaryEntity || !indexEntity) {
          this.renderError('Entities not found');
          return;
        }
  
        const summary = summaryEntity.attributes;
        const index = JSON.parse(indexEntity.state);
        
        // Load all chore details
        const allChores = [];
        for (const id in index) {
          const response = await fetch(`/local/grocy_processed/chore_${id}.json`);
          if (response.ok) {
            const chore = await response.json();
            allChores.push(chore);
          }
        }
        
        this.allChores = allChores;
        this.applyFilters();
      } catch (e) {
        this.renderError(`Error loading data: ${e.message}`);
      }
    }
  
    applyFilters() {
      this.chores = this.allChores.filter(chore => {
        if (this.filters.territory !== 'All' && chore.territorio !== this.filters.territory) return false;
        if (this.filters.location !== 'All' && chore.luogo_di_lavoro !== this.filters.location) return false;
        if (this.filters.person !== 'All' && chore.assigned_to !== this.filters.person) return false;
        return true;
      });
      
      this.render();
    }
  
    render() {
      const summaryEntity = this._hass?.states[this.config.summary_entity];
      if (!summaryEntity) {
        this.renderError('Summary entity not found');
        return;
      }
  
      const summary = summaryEntity.attributes;
      
      // Build filter dropdowns
      const territoryOptions = ['All', ...(summary.territories || [])];
      const locationOptions = ['All', ...(summary.locations || [])];
      const peopleOptions = ['All', ...(summary.people || [])];
  
      const filterHtml = `
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
          <div style="flex: 1; min-width: 120px;">
            <label style="display: block; margin-bottom: 4px; font-size: 0.9em;">Territory</label>
            <select id="territory-filter" style="width: 100%; padding: 4px; border-radius: 4px;">
              ${territoryOptions.map(t => `<option value="${t}" ${this.filters.territory === t ? 'selected' : ''}>${t}</option>`).join('')}
            </select>
          </div>
          <div style="flex: 1; min-width: 120px;">
            <label style="display: block; margin-bottom: 4px; font-size: 0.9em;">Location</label>
            <select id="location-filter" style="width: 100%; padding: 4px; border-radius: 4px;">
              ${locationOptions.map(l => `<option value="${l}" ${this.filters.location === l ? 'selected' : ''}>${l}</option>`).join('')}
            </select>
          </div>
          <div style="flex: 1; min-width: 120px;">
            <label style="display: block; margin-bottom: 4px; font-size: 0.9em;">Person</label>
            <select id="person-filter" style="width: 100%; padding: 4px; border-radius: 4px;">
              ${peopleOptions.map(p => `<option value="${p}" ${this.filters.person === p ? 'selected' : ''}>${p}</option>`).join('')}
            </select>
          </div>
        </div>
      `;
  
      // Render chores
      const choresHtml = this.chores.map(chore => `
        <div style="margin-bottom: 16px; padding: 12px; border-left: 4px solid var(--primary-color); background: var(--card-background-color); border-radius: 4px;">
          <div style="font-weight: bold; font-size: 1.1em;">${chore.name || 'Unnamed'}</div>
          <div style="margin-top: 4px; display: flex; justify-content: space-between;">
            <span>📅 ${chore.date || 'No date'}</span>
            <span>👤 ${chore.assigned_to || 'Unassigned'}</span>
          </div>
          <div style="margin-top: 8px;">
            ${chore.territorio ? `<div>🏠 Territory: ${chore.territorio}</div>` : ''}
            ${chore.luogo_di_lavoro ? `<div>📍 Location: ${chore.luogo_di_lavoro}</div>` : ''}
          </div>
          ${chore.description ? `<div style="margin-top: 8px; font-style: italic;">${chore.description}</div>` : ''}
        </div>
      `).join('');
  
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
              <div style="font-size: 1.4em; font-weight: 500;">${this.config.title || 'Grocy Chores'}</div>
              <div>${this.chores.length} items</div>
            </div>
            ${filterHtml}
            <div style="margin-top: 16px;">
              ${this.chores.length ? choresHtml : '<div>No chores match your filters</div>'}
            </div>
          </div>
        </ha-card>
      `;
  
      // Add event listeners
      this.shadowRoot.querySelector('#territory-filter').addEventListener('change', (e) => {
        this.filters.territory = e.target.value;
        this.applyFilters();
      });
      
      this.shadowRoot.querySelector('#location-filter').addEventListener('change', (e) => {
        this.filters.location = e.target.value;
        this.applyFilters();
      });
      
      this.shadowRoot.querySelector('#person-filter').addEventListener('change', (e) => {
        this.filters.person = e.target.value;
        this.applyFilters();
      });
    }
  
    renderError(message) {
      this.shadowRoot.innerHTML = `
        <ha-card>
          <div style="padding: 16px; color: var(--error-color);">
            ${message}
          </div>
        </ha-card>
      `;
    }
  
    getCardSize() {
      return 1 + Math.ceil(this.chores.length / 2);
    }
  }
  
  customElements.define('custom-grocy-card', CustomGrocyCard);
  
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "custom-grocy-card",
    name: "Custom Grocy Card",
    description: "Card for displaying Grocy chores with filtering"
  });