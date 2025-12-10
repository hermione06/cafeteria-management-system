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
  function edit(dishId) {
    const dish = Menu.getDishById(dishId);
    
    if (!dish) {
      showAlert('Dish not found!', 'error');
      return;
    }
    
    document.getElementById('modal-title').textContent = 'Edit Menu Item';
    document.getElementById('item-id').value = dish.dish_id;
    document.getElementById('item-name').value = dish.name;
    document.getElementById('item-description').value = dish.description || '';
    document.getElementById('item-price').value = dish.price;
    document.getElementById('item-picture').value = dish.picture_link || '';
    document.getElementById('item-available').checked = dish.is_available;
    Modal.show('item-modal');
  }

  /**
   * Save item (add or update)
   */
  async function save(event) {
    event.preventDefault();
    
    const dishId = document.getElementById('item-id').value;
    const itemData = {
      name: document.getElementById('item-name').value,
      description: document.getElementById('item-description').value,
      price: parseFloat(document.getElementById('item-price').value),
      picture_link: document.getElementById('item-picture').value || null,
      is_available: document.getElementById('item-available').checked
    };
    
    try {
      if (dishId) {
        await apiPut(`/api/dishes/${dishId}`, itemData);
        showAlert('Item updated successfully!', 'success');
      } else {
        await apiPost('/api/dishes', itemData);
        showAlert('Item added successfully!', 'success');
      }
      
      Modal.close('item-modal');
      await Menu.load();
      Menu.displayAdmin('menu-container');
      
    } catch (error) {
      console.error('Error saving item:', error);
      showAlert('Failed to save item. Please try again.', 'error');
    }
  }

  /**
   * Toggle availability
   */
  async function toggleAvailability(dishId) {
    const dish = Menu.getDishById(dishId);
    
    if (!dish) {
      showAlert('Dish not found!', 'error');
      return;
    }
    
    try {
      await apiPut(`/api/dishes/${dishId}`, {
        name: dish.name,
        description: dish.description,
        price: dish.price,
        picture_link: dish.picture_link,
        is_available: !dish.is_available
      });
      
      showAlert(`Item marked as ${!dish.is_available ? 'available' : 'unavailable'}!`, 'success');
      await Menu.load();
      Menu.displayAdmin('menu-container');
      
    } catch (error) {
      console.error('Error toggling availability:', error);
      showAlert('Failed to update availability. Please try again.', 'error');
    }
  }

  /**
   * Delete item
   */
  async function deleteDish(dishId) {
    const dish = Menu.getDishById(dishId);
    
    if (!dish) {
      showAlert('Dish not found!', 'error');
      return;
    }
    
    if (!confirmAction(`Are you sure you want to delete "${dish.name}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      await apiDelete(`/api/dishes/${dishId}`);
      showAlert('Item deleted successfully!', 'success');
      await Menu.load();
      Menu.displayAdmin('menu-container');
      
    } catch (error) {
      console.error('Error deleting item:', error);
      showAlert('Failed to delete item. Please try again.', 'error');
    }
  }

  // Public API
  return {
    showAddModal,
    edit,
    save,
    toggleAvailability,
    deleteDish
  };
})();

// Make it available globally
window.MenuAdmin = MenuAdmin;