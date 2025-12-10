// menu-unlogged.js - Unlogged user menu page script

async function loadMenu() {
  try {
    await Menu.load();
    Menu.displayBasic('menu-container');
  } catch (error) {
    console.error('Error loading menu:', error);
    document.getElementById('menu-container').innerHTML = 
      '<p style="text-align: center; width: 100%; color: #888;">Unable to load menu. Please try again later.</p>';
  }
}

function filterMenu(filter) {
  Menu.setFilter(filter);
  Menu.displayBasic('menu-container');
  Menu.updateFilterButtons({
    'all': 'filter-all',
    'available': 'filter-available'
  });
}

document.addEventListener('DOMContentLoaded', loadMenu);