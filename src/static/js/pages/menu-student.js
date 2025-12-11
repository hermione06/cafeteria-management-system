// menu-student.js - Student menu page script

async function loadMenu() {
  try {
    // Students only see available items
    await Menu.load({ available: 'true' });
    Menu.displayStudent('menu-container');
    Cart.updateCount();
  } catch (error) {
    console.error('Error loading menu:', error);
    document.getElementById('menu-container').innerHTML = 
      '<p style="text-align: center; width: 100%; color: #888;">Unable to load menu. Please try again later.</p>';
  }
}

function filterMenu(filter) {
  Menu.setFilter(filter);
  Menu.displayStudent('menu-container');
  Menu.updateFilterButtons({
    'all': 'filter-all',
    'available': 'filter-available'
  });
}

document.addEventListener('DOMContentLoaded', loadMenu);