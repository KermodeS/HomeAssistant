class GrocyChoresDashboard extends HTMLElement {
  static get properties() {
    return {
      hass: {},
      config: {},
      chores: [],
      filteredChores: [],
      filterValues: {},
      selectedChore: null
    };
  }
  
  constructor() {
    super();
    this.chores = [];
    this.filteredChores = [];
    this.filterValues = {};
    this.selectedChore = null;
  }
  
  setConfig(config) {
    if (!config.data_path) {
      throw new Error('You need to define a data_path');
    }
    
    this.config = config;
    this.title = config.title || 'Grocy Chores';
    this.dataPath = config.data_path;
    this.refreshInterval = config.refresh_interval || 3600;
    this.filters = config.filters || [];
    
    // Initialize filter values
    this.filters.forEach(filter => {
      this.filterValues[filter.field] = 'all';
    });

    this.initialized = false;
  }
  
  set hass(hass) {
    this._hass = hass;
    
    if (!this.initialized) {
      this.initialized = true;
      this.loadChoresData();
      // Set up auto-refresh
      setInterval(() => this.loadChoresData(), this.refreshInterval * 1000);
    }
  }
  
  async loadChoresData() {
    try {
      const response = await fetch(this.dataPath + '?t=' + new Date().getTime());
      if (response.ok) {
        const data = await response.json();
        this.chores = data;
        this.applyFilters();
        this.requestUpdate();
      } else {
        console.error('Failed to load chores data:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading chores data:', error);
    }
  }
  
  applyFilters() {
    this.filteredChores = this.chores.filter(chore => {
      let include = true;
      
      // Apply each active filter
      Object.entries(this.filterValues).forEach(([field, value]) => {
        if (value !== 'all' && chore[field] !== value) {
          include = false;
        }
      });
      
      return include;
    });
  }
  
  handleFilterChange(field, value) {
    this.filterValues[field] = value;
    this.applyFilters();
    this.requestUpdate();
  }
  
  showChoreDetails(chore) {
    this.selectedChore = chore;
    this.requestUpdate();
  }
  
  closeDetails() {
    this.selectedChore = null;
    this.requestUpdate();
  }
  
  getDueStatusInfo(dueStatus) {
    switch(dueStatus) {
      case 'overdue':
        return { icon: 'mdi:alert-circle', color: 'var(--error-color)' };
      case 'today':
        return { icon: 'mdi:clock-alert', color: 'var(--warning-color)' };
      case 'tomorrow':
        return { icon: 'mdi:calendar-today', color: 'var(--info-color)' };
      default:
        return { icon: 'mdi:calendar', color: 'var(--primary-color)' };
    }
  }
  
  requestUpdate() {
    this.innerHTML = '';
    this.render();
  }
  
  render() {
    // If showing details view
    if (this.selectedChore) {
      this.renderChoreDetails();
      return;
    }
    
    // Main card view
    const card = document.createElement('ha-card');
    card.header = this.title;
    
    // Filters section
    const filtersDiv = document.createElement('div');
    filtersDiv.className = 'filters';
    this.filters.forEach(filter => {
      const filterContainer = document.createElement('div');
      filterContainer.className = 'filter';
      
      const icon = document.createElement('ha-icon');
      icon.icon = filter.icon;
      filterContainer.appendChild(icon);
      
      const select = document.createElement('select');
      select.onchange = (e) => this.handleFilterChange(filter.field, e.target.value);
      
      // Add 'All' option
      const allOption = document.createElement('option');
      allOption.value = 'all';
      allOption.text = `All ${filter.name}`;
      select.appendChild(allOption);
      
      // Get unique values for this filter
      const uniqueValues = [...new Set(this.chores.map(chore => chore[filter.field]))];
      uniqueValues.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.text = value;
        if (this.filterValues[filter.field] === value) {
          option.selected = true;
        }
        select.appendChild(option);
      });
      
      filterContainer.appendChild(select);
      filtersDiv.appendChild(filterContainer);
    });
    card.appendChild(filtersDiv);
    
    // Chores list
    const content = document.createElement('div');
    content.className = 'card-content';
    
    if (this.filteredChores.length === 0) {
      const emptyMsg = document.createElement('div');
      emptyMsg.className = 'empty-message';
      emptyMsg.textContent = 'No chores match the selected filters';
      content.appendChild(emptyMsg);
    } else {
      const list = document.createElement('div');
      list.className = 'chores-list';
      
      this.filteredChores.forEach(chore => {
        const choreItem = document.createElement('div');
        choreItem.className = 'chore-item';
        choreItem.onclick = () => this.showChoreDetails(chore);
        
        const statusInfo = this.getDueStatusInfo(chore.dueStatus);
        
        // Chore header with name and due date
        const header = document.createElement('div');
        header.className = 'chore-header';
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'chore-name';
        nameDiv.style.color = statusInfo.color;
        nameDiv.textContent = chore.name;
        header.appendChild(nameDiv);
        
        const dateDiv = document.createElement('div');
        dateDiv.className = 'chore-date';
        
        const dateIcon = document.createElement('ha-icon');
        dateIcon.icon = statusInfo.icon;
        dateIcon.style.color = statusInfo.color;
        dateDiv.appendChild(dateIcon);
        
        const dateText = document.createElement('span');
        dateText.textContent = chore.date;
        dateDiv.appendChild(dateText);
        
        header.appendChild(dateDiv);
        choreItem.appendChild(header);
        
        // Chore details
        const details = document.createElement('div');
        details.className = 'chore-details';
        
        // Assigned to
        const assignedDiv = document.createElement('div');
        assignedDiv.className = 'chore-assigned';
        
        const userIcon = document.createElement('ha-icon');
        userIcon.icon = 'mdi:account';
        assignedDiv.appendChild(userIcon);
        
        const assignedText = document.createElement('span');
        assignedText.textContent = chore.assigned_to;
        assignedDiv.appendChild(assignedText);
        
        details.appendChild(assignedDiv);
        
        // Location
        if (chore.luogo_di_lavoro) {
          const locationDiv = document.createElement('div');
          locationDiv.className = 'chore-location';
          
          const locationIcon = document.createElement('ha-icon');
          locationIcon.icon = 'mdi:map-marker';
          locationDiv.appendChild(locationIcon);
          
          const locationText = document.createElement('span');
          locationText.textContent = `${chore.luogo_di_lavoro} (${chore.territorio})`;
          locationDiv.appendChild(locationText);
          
          details.appendChild(locationDiv);
        }
        
        choreItem.appendChild(details);
        list.appendChild(choreItem);
      });
      
      content.appendChild(list);
    }
    
    card.appendChild(content);
    this.appendChild(card);
    
    // Add styling
    this.addStyles();
  }
  
  renderChoreDetails() {
    const chore = this.selectedChore;
    const statusInfo = this.getDueStatusInfo(chore.dueStatus);
    
    const card = document.createElement('ha-card');
    
    // Header with back button
    const header = document.createElement('div');
    header.className = 'card-header';
    
    const backButton = document.createElement('ha-icon-button');
    backButton.icon = 'mdi:arrow-left';
    backButton.onclick = () => this.closeDetails();
    header.appendChild(backButton);
    
    const title = document.createElement('div');
    title.className = 'title';
    title.textContent = 'Chore Details';
    header.appendChild(title);
    
    card.appendChild(header);
    
    // Chore content
    const content = document.createElement('div');
    content.className = 'card-content';
    
    // Chore name
    const nameDiv = document.createElement('h2');
    nameDiv.style.color = statusInfo.color;
    nameDiv.textContent = chore.name;
    content.appendChild(nameDiv);
    
    // Status badge
    const statusDiv = document.createElement('div');
    statusDiv.className = 'status-badge';
    statusDiv.style.color = statusInfo.color;
    statusDiv.style.borderColor = statusInfo.color;
    
    const statusIcon = document.createElement('ha-icon');
    statusIcon.icon = statusInfo.icon;
    statusDiv.appendChild(statusIcon);
    
    const statusText = document.createElement('span');
    statusText.textContent = chore.dueStatus === 'today' ? 'Due today' : 
                            chore.dueStatus === 'overdue' ? 'Overdue' : 
                            chore.dueStatus === 'tomorrow' ? 'Due tomorrow' : 'Upcoming';
    statusDiv.appendChild(statusText);
    
    content.appendChild(statusDiv);
    
    // Details table
    const detailsTable = document.createElement('table');
    detailsTable.className = 'details-table';
    
    const rows = [
      { label: 'Date', value: chore.date },
      { label: 'Assigned to', value: chore.assigned_to },
      { label: 'Territorio', value: chore.territorio },
      { label: 'Luogo di lavoro', value: chore.luogo_di_lavoro },
      { label: 'Description', value: chore.description, multiline: true },
      { label: 'References', value: chore.references, multiline: true },
      { label: 'Equipment', value: chore.equipment, multiline: true }
    ];
    
    rows.forEach(row => {
      const tr = document.createElement('tr');
      
      const th = document.createElement('th');
      th.textContent = row.label;
      tr.appendChild(th);
      
      const td = document.createElement('td');
      if (row.multiline) {
        td.innerHTML = row.value.replace(/\n/g, '<br>');
      } else {
        td.textContent = row.value;
      }
      tr.appendChild(td);
      
      detailsTable.appendChild(tr);
    });
    
    content.appendChild(detailsTable);
    
    // Action buttons
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'action-buttons';
    
    const completeBtn = document.createElement('mwc-button');
    completeBtn.raised = true;
    completeBtn.textContent = 'Mark as Completed';
    actionsDiv.appendChild(completeBtn);
    
    content.appendChild(actionsDiv);
    
    card.appendChild(content);
    this.appendChild(card);
    
    // Add styling
    this.addStyles();
  }
  
  addStyles() {
    const style = document.createElement('style');
    style.textContent = `
      ha-card {
        margin-top: 8px;
        overflow: hidden;
      }
      
      .filters {
        display: flex;
        flex-wrap: wrap;
        padding: 8px 16px;
        background: var(--secondary-background-color);
        border-top: 1px solid var(--divider-color);
        border-bottom: 1px solid var(--divider-color);
      }
      
      .filter {
        display: flex;
        align-items: center;
        margin-right: 16px;
        margin-bottom: 8px;
      }
      
      .filter ha-icon {
        margin-right: 8px;
        color: var(--secondary-text-color);
      }
      
      .filter select {
        background: var(--card-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        padding: 4px 8px;
      }
      
      .chores-list {
        padding: 0;
      }
      
      .chore-item {
        padding: 16px;
        border-bottom: 1px solid var(--divider-color);
        cursor: pointer;
      }
      
      .chore-item:hover {
        background: var(--secondary-background-color);
      }
      
      .chore-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
      }
      
      .chore-name {
        font-weight: 500;
      }
      
      .chore-date {
        display: flex;
        align-items: center;
        font-size: 14px;
        padding: 2px 8px;
        border-radius: 12px;
        background: var(--secondary-background-color);
      }
      
      .chore-date ha-icon {
        margin-right: 4px;
      }
      
      .chore-details {
        display: flex;
        flex-direction: column;
        font-size: 14px;
        color: var(--secondary-text-color);
      }
      
      .chore-assigned, .chore-location {
        display: flex;
        align-items: center;
        margin-top: 4px;
      }
      
      .chore-assigned ha-icon, .chore-location ha-icon {
        margin-right: 8px;
        width: 14px;
        height: 14px;
      }
      
      .empty-message {
        padding: 32px 16px;
        text-align: center;
        color: var(--secondary-text-color);
      }
      
      .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 16px;
        border: 1px solid;
        margin-bottom: 16px;
      }
      
      .status-badge ha-icon {
        margin-right: 8px;
      }
      
      .details-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
      }
      
      .details-table th {
        text-align: left;
        padding: 8px 8px 8px 0;
        vertical-align: top;
        width: 30%;
        color: var(--secondary-text-color);
        font-weight: normal;
      }
      
      .details-table td {
        padding: 8px 0;
        vertical-align: top;
      }
      
      .action-buttons {
        margin-top: 16px;
        display: flex;
        justify-content: flex-end;
      }
    `;
    
    this.appendChild(style);
  }
  
  getCardSize() {
    return 3 + (this.filteredChores.length || 1) * 0.5;
  }
}

customElements.define('grocy-chores-dashboard', GrocyChoresDashboard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "grocy-chores-dashboard",
  name: "Grocy Chores Dashboard",
  description: "A card that displays Grocy chores with filtering options"
});