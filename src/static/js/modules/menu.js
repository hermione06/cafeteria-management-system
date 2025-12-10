// menu.js - Core menu module for all menu pages

const Menu = (() => {
  let allDishes = [];
  let currentFilter = 'all';

  /**
   * Load dishes from API
   */
  async function load() {
    try {
      const data = await apiGet('/api/dishes');
      allDishes = data.dishes || data || [];
      return allDishes;
    } catch (error) {
      console.error('Error loading menu:', error);
      throw error;
    }
  }

  /**
   * Get all dishes
   */
  function getAll() {
    return allDishes;
  }

  /**
   * Get dish by ID
   */
  function getDishById(dishId) {
    return allDishes.find(d => d.dish_id === dishId);
  }

  /**
   * Get filtered dishes based on current filter
   */
  function getFiltered() {
    if (currentFilter === 'available') {
      return allDishes.filter(dish => dish.is_available);
    } else if (currentFilter === 'unavailable') {
      return allDishes.filter(dish => !dish.is_available);
    }
    return allDishes;
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
   * Display menu items (basic view - for unlogged users)
   */
  function displayBasic(containerId) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    const filteredDishes = getFiltered();

    if (filteredDishes.length === 0) {
      container.innerHTML = '<p style="text-align: center; width: 100%; color: #888;">No dishes found.</p>';
      return;
    }

    container.innerHTML = filteredDishes.map(dish => `
      <div class="card">
        <img src="${dish.picture_link || '/static/images/placeholder.jpg'}" 
             alt="${dish.name}" 
             onerror="this.src='/static/images/placeholder.jpg'"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: var(--radius); margin-bottom: 1rem;">
        
        <h3 style="color: var(--bounty-blue); margin-bottom: 0.5rem;">${dish.name}</h3>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">${dish.description || 'No description available'}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 1.2rem; font-weight: bold; color: var(--bounty-brown);">${formatCurrency(dish.price)}</span>
          <span style="font-size: 0.85rem; color: ${dish.is_available ? '#28a745' : '#dc3545'}; font-weight: 500;">
            ${dish.is_available ? '✓ Available' : '✗ Unavailable'}
          </span>
        </div>
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

    const filteredDishes = getFiltered();

    if (filteredDishes.length === 0) {
      container.innerHTML = '<p style="text-align: center; width: 100%; color: #888;">No dishes found.</p>';
      return;
    }

    container.innerHTML = filteredDishes.map(dish => `
      <div class="card">
        <img src="${dish.picture_link || '/static/images/placeholder.jpg'}" 
             alt="${dish.name}" 
             onerror="this.src='/static/images/placeholder.jpg'"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: var(--radius); margin-bottom: 1rem;">
        
        <h3 style="color: var(--bounty-blue); margin-bottom: 0.5rem;">${dish.name}</h3>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">${dish.description || 'No description available'}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <span style="font-size: 1.2rem; font-weight: bold; color: var(--bounty-brown);">${formatCurrency(dish.price)}</span>
          <span style="font-size: 0.85rem; color: ${dish.is_available ? '#28a745' : '#dc3545'}; font-weight: 500;">
            ${dish.is_available ? '✓ Available' : '✗ Unavailable'}
          </span>
        </div>
        
        ${dish.is_available ? `
          <button class="btn" style="width: 100%;" onclick="Cart.add(${dish.dish_id})">
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

    const filteredDishes = getFiltered();

    if (filteredDishes.length === 0) {
      container.innerHTML = '<p style="text-align: center; width: 100%; color: #888;">No dishes found.</p>';
      return;
    }

    container.innerHTML = filteredDishes.map(dish => `
      <div class="card">
        <img src="${dish.picture_link || '/static/images/placeholder.jpg'}" 
             alt="${dish.name}" 
             onerror="this.src='/static/images/placeholder.jpg'"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: var(--radius); margin-bottom: 1rem;">
        
        <h3 style="color: var(--bounty-blue); margin-bottom: 0.5rem;">${dish.name}</h3>
        <p style="color: #666; font-size: 0.9rem; margin-bottom: 1rem;">${dish.description || 'No description available'}</p>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <span style="font-size: 1.2rem; font-weight: bold; color: var(--bounty-brown);">${formatCurrency(dish.price)}</span>
          <span style="font-size: 0.85rem; color: ${dish.is_available ? '#28a745' : '#dc3545'}; font-weight: 500;">
            ${dish.is_available ? '✓ Available' : '✗ Unavailable'}
          </span>
        </div>
        
        <!-- Admin Controls -->
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button class="btn" onclick="MenuAdmin.edit(${dish.dish_id})" style="flex: 1; min-width: 80px; font-size: 0.85rem;">
            Edit
          </button>
          <button class="btn" onclick="MenuAdmin.toggleAvailability(${dish.dish_id})" 
                  style="flex: 1; min-width: 100px; font-size: 0.85rem; background-color: ${dish.is_available ? '#ffc107' : '#28a745'};">
            ${dish.is_available ? 'Mark Unavailable' : 'Mark Available'}
          </button>
          <button class="btn" onclick="MenuAdmin.deleteDish(${dish.dish_id})" 
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

  // Public API
  return {
    load,
    getAll,
    getDishById,
    getFiltered,
    setFilter,
    getFilter,
    displayBasic,
    displayStudent,
    displayAdmin,
    updateFilterButtons
  };
})();

// Make it available globally
window.Menu = Menu;