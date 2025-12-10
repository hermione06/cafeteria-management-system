// menu-admin-page.js - Admin menu page script

async function loadMenu() {
  try {
    await Menu.load();
    Menu.displayAdmin('menu-container');
  } catch (error) {
    console.error('Error loading menu:', error);
    document.getElementById('menu-container').innerHTML = 
      '<p style="text-align: center; width: 100%; color: #888;">Unable to load menu. Please try again later.</p>';
  }
}

function filterMenu(filter) {
  Menu.setFilter(filter);
  Menu.displayAdmin('menu-container');
  Menu.updateFilterButtons({
    'all': 'filter-all',
    'available': 'filter-available',
    'unavailable': 'filter-unavailable'
  });
}

function showAddModal() {
  MenuAdmin.showAddModal();
}

function closeModal() {
  Modal.close('item-modal');
}

async function saveItem(event) {
  await MenuAdmin.save(event);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadMenu();
  Modal.initOutsideClick('item-modal');
});