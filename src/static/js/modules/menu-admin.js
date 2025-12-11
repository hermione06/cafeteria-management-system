// menu-admin.js - Admin menu management module

const MenuAdmin = (() => {
  
  /**
   * Show add modal
   */
  function showAddModal() {
    document.getElementById('modal-title').textContent = 'Add New Item';
    document.getElementById('item-form').reset();
    document.getElementById('item-id').value = '';
    document.getElementById('item-available').checked = true;
    Modal.show('item-modal');
  }

  /**
   * Edit item
   */
  function edit(itemId) {
    const item = Menu.getItemById(itemId);
    
    if (!item) {
      showAlert('Menu item not found!', 'error');
      return;
    }
    
    document.getElementById('modal-title').textContent = 'Edit Menu Item';
    document.getElementById('item-id').value = item.id;
    document.getElementById('item-name').value = item.name;
    document.getElementById('item-description').value = item.description || '';
    document.getElementById('item-price').value = item.price;
    document.getElementById('item-category').value = item.category || '';
    document.getElementById('item-picture').value = item.image_url || '';
    document.getElementById('item-available').checked = item.is_available;
    
    // Optional: stock_quantity if you're using it
    if (document.getElementById('item-stock')) {
      document.getElementById('item-stock').value = item.stock_quantity || 0;
    }
    
    Modal.show('item-modal');
  }

  /**
   * Save item (add or update)
   */
  async function save(event) {
    event.preventDefault();
    
    const itemId = document.getElementById('item-id').value;
    const itemData = {
      name: document.getElementById('item-name').value,
      description: document.getElementById('item-description').value,
      price: parseFloat(document.getElementById('item-price').value),
      category: document.getElementById('item-category').value.toLowerCase(),
      image_url: document.getElementById('item-picture').value || null,
      is_available: document.getElementById('item-available').checked
    };
    
    // Optional: add stock_quantity if you're using it
    if (document.getElementById('item-stock')) {
      itemData.stock_quantity = parseInt(document.getElementById('item-stock').value) || 0;
    }
    
    try {
      if (itemId) {
        // Update existing item
        await apiPut(`/api/menu/${itemId}`, itemData);
        showAlert('Item updated successfully!', 'success');
      } else {
        // Create new item
        await apiPost('/api/menu', itemData);
        showAlert('Item added successfully!', 'success');
      }
      
      Modal.close('item-modal');
      await Menu.load();
      Menu.displayAdmin('menu-container');
      
    } catch (error) {
      console.error('Error saving item:', error);
      showAlert(error.message || 'Failed to save item. Please try again.', 'error');
    }
  }

  /**
   * Toggle availability using the PATCH endpoint
   */
  async function toggleAvailability(itemId) {
    const item = Menu.getItemById(itemId);
    
    if (!item) {
      showAlert('Menu item not found!', 'error');
      return;
    }
    
    try {
      await apiPatch(`/api/menu/${itemId}/availability`, {
        is_available: !item.is_available
      });
      
      const status = !item.is_available ? 'available' : 'unavailable';
      showAlert(`Item marked as ${status}!`, 'success');
      
      await Menu.load();
      Menu.displayAdmin('menu-container');
      
    } catch (error) {
      console.error('Error toggling availability:', error);
      showAlert(error.message || 'Failed to update availability. Please try again.', 'error');
    }
  }

  /**
   * Delete item
   */
  async function deleteItem(itemId) {
    const item = Menu.getItemById(itemId);
    
    if (!item) {
      showAlert('Menu item not found!', 'error');
      return;
    }
    
    if (!confirmAction(`Are you sure you want to delete "${item.name}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      await apiDelete(`/api/menu/${itemId}`);
      showAlert('Item deleted successfully!', 'success');
      
      await Menu.load();
      Menu.displayAdmin('menu-container');
      
    } catch (error) {
      console.error('Error deleting item:', error);
      showAlert(error.message || 'Failed to delete item. Please try again.', 'error');
    }
  }

  // Public API
  return {
    showAddModal,
    edit,
    save,
    toggleAvailability,
    deleteItem  // Changed from deleteDish
  };
})();

// Make it available globally
window.MenuAdmin = MenuAdmin;