// cart.js - Shopping cart module for student menu

const Cart = (() => {
  
  /**
   * Get cart from sessionStorage
   */
  function get() {
    return JSON.parse(sessionStorage.getItem('cart') || '[]');
  }

  /**
   * Save cart to sessionStorage
   */
  function save(cart) {
    sessionStorage.setItem('cart', JSON.stringify(cart));
  }

  /**
   * Add item to cart
   */
  function add(dishId) {
    const dish = Menu.getDishById(dishId);
    
    if (!dish) {
      showAlert('Dish not found!', 'error');
      return;
    }
    
    if (!dish.is_available) {
      showAlert('This dish is currently unavailable.', 'warning');
      return;
    }
    
    let cart = get();
    
    // Check if item already exists in cart
    const existingItem = cart.find(item => item.dish_id === dishId);
    if (existingItem) {
      existingItem.count++;
    } else {
      cart.push({ 
        dish_id: dish.dish_id,
        name: dish.name,
        price: dish.price,
        picture_link: dish.picture_link,
        count: 1 
      });
    }
    
    save(cart);
    updateCount();
    showAlert(`${dish.name} added to cart!`, 'success');
  }

  /**
   * Remove item from cart
   */
  function remove(dishId) {
    let cart = get();
    cart = cart.filter(item => item.dish_id !== dishId);
    save(cart);
    updateCount();
  }

  /**
   * Update item quantity
   */
  function updateQuantity(dishId, count) {
    let cart = get();
    const item = cart.find(item => item.dish_id === dishId);
    
    if (item) {
      if (count <= 0) {
        remove(dishId);
      } else {
        item.count = count;
        save(cart);
        updateCount();
      }
    }
  }

  /**
   * Clear cart
   */
  function clear() {
    sessionStorage.removeItem('cart');
    updateCount();
  }

  /**
   * Get total items count
   */
  function getCount() {
    const cart = get();
    return cart.reduce((sum, item) => sum + item.count, 0);
  }

  /**
   * Get total price
   */
  function getTotal() {
    const cart = get();
    return cart.reduce((sum, item) => sum + (item.price * item.count), 0);
  }

  /**
   * Update cart count badge in navigation
   */
  function updateCount() {
    const totalItems = getCount();
    const cartBadge = document.getElementById('cart-count');
    
    if (cartBadge) {
      cartBadge.textContent = totalItems;
      cartBadge.style.display = totalItems > 0 ? 'inline' : 'none';
    }
  }

  // Public API
  return {
    get,
    add,
    remove,
    updateQuantity,
    clear,
    getCount,
    getTotal,
    updateCount
  };
})();

// Make it available globally
window.Cart = Cart;