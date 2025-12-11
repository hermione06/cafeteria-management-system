// menu.js - Core menu module for all menu pages

const Menu = (() => {
  let allItems = [];
  let currentFilter = 'all';
  let pagination = null;

  /**
   * Load menu items from API
   * @param {Object} options - Query parameters (category, available, search, page, per_page)
   */
  async function load(options = {}) {
    try {
      // Build query string
      const params = new URLSearchParams();
      
      // Add available filter if specified
      if (options.available !== undefined) {
        params.append('available', options.available);
      }
      
      if (options.category) {
        params.append('category', options.category);
      }
      
      if (options.search) {
        params.append('search', options.search);
      }
      
      if (options.page) {
        params.append('page', options.page);
      }
      
      if (options.per_page) {
        params.append('per_page', options.per_page);
      }
      
      // Fetch from Flask API endpoint
      const queryString = params.toString();
      const url = queryString ? `/api/menu?${queryString}` : '/api/menu';
      
      const data = await apiGet(url);
      
      allItems = data.items || [];
      pagination = data.pagination || null;
      
      return allItems;
    } catch (error) {
      console.error('Error loading menu:', error);
      throw error;
    }
  }

  /**
   * Get all menu items
   */
  function getAll() {
    return allItems;
  }

  /**
   * Get menu item by ID
   */
  function getItemById(itemId) {
    return allItems.find(item => item.id === itemId);
  }

  /**
   * Get filtered items based on current filter
   */
  function getFiltered() {
    if (currentFilter === 'available') {
      return allItems.filter(item => item.is_available);
    } else if (currentFilter === 'unavailable') {
      return allItems.filter(item => !item.is_available);
    }
    return allItems;
  }

  /**
   * Set filter
   */
  function setFilter(filter) {
    currentFilter = filter;
    return currentFilter;
  }

  /**
   * Get current filter
   */
  function getFilter() {
    return currentFilter;
  }

  /**
   * Get pagination info
   */
  function getPagination() {
    return pagination;
  }

  /**
   * Display menu items (basic view - for unlogged users)
   */
  function displayBasic(containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    const filteredItems = getFiltered();

    if (filteredItems.length === 0) {
      container.innerHTML = '<p style="text-align: center; width: 100%; color: #888;">No menu items found.</p>';
      return;
    }

    container.innerHTML = filteredItems.map(item => `
      <div class="card">
        <img src="${item.image_url || '/static/images/placeholder.jpg'}" 
             alt="${escapeHtml(item.name)}" 
             onerror="this.src='/static/images/placeholder.jpg'"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: var(--radius); margin-bottom: 1rem;">
        
        <h3 style="color: var(--bounty-blue); margin-bottom: 0.5rem;">${escapeHtml(item.name)}</h3>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">${escapeHtml(item.description || 'No description available')}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 1.2rem; font-weight: bold; color: var(--bounty-brown);">${formatCurrency(item.price)}</span>
          <span style="font-size: 0.85rem; color: ${item.is_available ? '#28a745' : '#dc3545'}; font-weight: 500;">
            ${item.is_available ? '✓ Available' : '✗ Unavailable'}
          </span>
        </div>
        ${item.category ? `<div style="margin-top: 0.5rem;"><span style="font-size: 0.8rem; color: #999; text-transform: capitalize;">${escapeHtml(item.category)}</span></div>` : ''}
      </div>
    `).join('');
  }

  /**
   * Display menu items (student view with cart functionality)
   */
  function displayStudent(containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    const filteredItems = getFiltered();

    if (filteredItems.length === 0) {
      container.innerHTML = '<p style="text-align: center; width: 100%; color: #888;">No menu items found.</p>';
      return;
    }

    container.innerHTML = filteredItems.map(item => `
      <div class="card">
        <img src="${item.image_url || '/static/images/placeholder.jpg'}" 
             alt="${escapeHtml(item.name)}" 
             onerror="this.src='/static/images/placeholder.jpg'"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: var(--radius); margin-bottom: 1rem;">
        
        <h3 style="color: var(--bounty-blue); margin-bottom: 0.5rem;">${escapeHtml(item.name)}</h3>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">${escapeHtml(item.description || 'No description available')}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <span style="font-size: 1.2rem; font-weight: bold; color: var(--bounty-brown);">${formatCurrency(item.price)}</span>
          <span style="font-size: 0.85rem; color: ${item.is_available ? '#28a745' : '#dc3545'}; font-weight: 500;">
            ${item.is_available ? '✓ Available' : '✗ Unavailable'}
          </span>
        </div>
        ${item.category ? `<div style="margin-bottom: 1rem;"><span style="font-size: 0.8rem; color: #999; text-transform: capitalize;">${escapeHtml(item.category)}</span></div>` : ''}
        
        ${item.is_available ? `
          <button class="btn" style="width: 100%;" onclick="Cart.add(${item.id})">
            Add to Cart
          </button>
        ` : `
          <button class="btn" style="width: 100%; opacity: 0.5; cursor: not-allowed;" disabled>
            Currently Unavailable
          </button>
        `}
      </div>
    `).join('');
  }

  /**
   * Display menu items (admin view with management controls)
   */
  function displayAdmin(containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    const filteredItems = getFiltered();

    if (filteredItems.length === 0) {
      container.innerHTML = '<p style="text-align: center; width: 100%; color: #888;">No menu items found.</p>';
      return;
    }

    container.innerHTML = filteredItems.map(item => `
      <div class="card">
        <img src="${item.image_url || '/static/images/placeholder.jpg'}" 
             alt="${escapeHtml(item.name)}" 
             onerror="this.src='/static/images/placeholder.jpg'"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: var(--radius); margin-bottom: 1rem;">
        
        <h3 style="color: var(--bounty-blue); margin-bottom: 0.5rem;">${escapeHtml(item.name)}</h3>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">${escapeHtml(item.description || 'No description available')}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <span style="font-size: 1.2rem; font-weight: bold; color: var(--bounty-brown);">${formatCurrency(item.price)}</span>
          <span style="font-size: 0.85rem; color: ${item.is_available ? '#28a745' : '#dc3545'}; font-weight: 500;">
            ${item.is_available ? '✓ Available' : '✗ Unavailable'}
          </span>
        </div>
        ${item.category ? `<div style="margin-bottom: 1rem;"><span style="font-size: 0.8rem; color: #999; text-transform: capitalize;">${escapeHtml(item.category)}</span></div>` : ''}
        
        <!-- Admin Controls -->
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button class="btn" onclick="MenuAdmin.edit(${item.id})" style="flex: 1; min-width: 80px; font-size: 0.85rem;">
            Edit
          </button>
          <button class="btn" onclick="MenuAdmin.toggleAvailability(${item.id})" 
                  style="flex: 1; min-width: 100px; font-size: 0.85rem; background-color: ${item.is_available ? '#ffc107' : '#28a745'};">
            ${item.is_available ? 'Mark Unavailable' : 'Mark Available'}
          </button>
          <button class="btn" onclick="MenuAdmin.deleteItem(${item.id})" 
                  style="flex: 1; min-width: 80px; font-size: 0.85rem; background-color: #dc3545;">
            Delete
          </button>
        </div>
      </div>
    `).join('');
  }

  /**
   * Update filter buttons
   */
  function updateFilterButtons(filterIds) {
    Object.entries(filterIds).forEach(([filter, buttonId]) => {
      const button = document.getElementById(buttonId);
      if (button) {
        button.style.opacity = currentFilter === filter ? '1' : '0.6';
      }
    });
  }

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Public API
  return {
    load,
    getAll,
    getItemById,
    getFiltered,
    setFilter,
    getFilter,
    getPagination,
    displayBasic,
    displayStudent,
    displayAdmin,
    updateFilterButtons
  };
})();

// Make it available globally
window.Menu = Menu;