// student-order.js - Student place order page

const StudentOrderPage = (() => {
  let cart = [];
  
  /**
   * Initialize the page
   */
  async function init() {
    await loadMenu();
    loadCartFromStorage();
    updateCartDisplay();
  }
  
  /**
   * Load menu items
   */
  async function loadMenu() {
    try {
      await Menu.load();
      Menu.setFilter('available'); // Only show available items
      renderMenu();
    } catch (error) {
      console.error('Error loading menu:', error);
      document.getElementById('menu-items-grid').innerHTML = 
        '<p class="empty-message">Unable to load menu items.</p>';
    }
  }
  
  /**
   * Render menu items
   */
  function renderMenu() {
    const grid = document.getElementById('menu-items-grid');
    const dishes = Menu.getFiltered();
    
    if (dishes.length === 0) {
      grid.innerHTML = '<p class="empty-message">No items available.</p>';
      return;
    }
    
    grid.innerHTML = dishes.map(dish => `
      <div class="card">
        <img src="${dish.picture_link || '/static/images/placeholder.jpg'}" 
             alt="${dish.name}"
             onerror="this.src='/static/images/placeholder.jpg'">
        
        <h4>${dish.name}</h4>
        <p class="price">${formatCurrency(dish.price)}</p>
        
        <button class="btn" onclick="StudentOrderPage.addToCart(${dish.dish_id})">
          Add to Cart
        </button>
      </div>
    `).join('');
  }
  
  /**
   * Load cart from sessionStorage
   */
  function loadCartFromStorage() {
    const savedCart = sessionStorage.getItem('cart');
    if (savedCart) {
      cart = JSON.parse(savedCart);
    }
  }
  
  /**
   * Save cart to sessionStorage
   */
  function saveCartToStorage() {
    sessionStorage.setItem('cart', JSON.stringify(cart));
  }
  
  /**
   * Add item to cart
   */
  function addToCart(dishId) {
    const dish = Menu.getDishById(dishId);
    if (!dish) return;
    
    const existingItem = cart.find(item => item.dish_id === dishId);
    if (existingItem) {
      existingItem.count++;
    } else {
      cart.push({ 
        dish_id: dish.dish_id,
        name: dish.name,
        price: dish.price,
        count: 1 
      });
    }
    
    saveCartToStorage();
    updateCartDisplay();
  }
  
  /**
   * Remove item from cart
   */
  function removeFromCart(dishId) {
    cart = cart.filter(item => item.dish_id !== dishId);
    saveCartToStorage();
    updateCartDisplay();
  }
  
  /**
   * Update item quantity
   */
  function updateQuantity(dishId, change) {
    const item = cart.find(i => i.dish_id === dishId);
    if (!item) return;
    
    item.count += change;
    if (item.count <= 0) {
      removeFromCart(dishId);
    } else {
      saveCartToStorage();
      updateCartDisplay();
    }
  }
  
  /**
   * Update cart display
   */
  function updateCartDisplay() {
    const cartItemsDiv = document.getElementById('cart-items');
    
    if (cart.length === 0) {
      cartItemsDiv.innerHTML = '<p class="empty-message">Your cart is empty</p>';
      document.getElementById('cart-total').textContent = '$0.00';
      return;
    }
    
    cartItemsDiv.innerHTML = cart.map(item => `
      <div class="cart-item">
        <div class="cart-item-header">
          <strong>${item.name}</strong>
          <button onclick="StudentOrderPage.removeFromCart(${item.dish_id})" class="cart-item-remove">&times;</button>
        </div>
        
        <div class="cart-item-footer">
          <div class="quantity-controls">
            <button onclick="StudentOrderPage.updateQuantity(${item.dish_id}, -1)" class="btn">-</button>
            <span>${item.count}</span>
            <button onclick="StudentOrderPage.updateQuantity(${item.dish_id}, 1)" class="btn">+</button>
          </div>
          <strong class="cart-item-total">${formatCurrency(parseFloat(item.price) * item.count)}</strong>
        </div>
      </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.count), 0);
    document.getElementById('cart-total').textContent = formatCurrency(total);
  }
  
  /**
   * Clear cart
   */
  function clearCart() {
    if (confirmAction('Are you sure you want to clear your cart?')) {
      cart = [];
      saveCartToStorage();
      updateCartDisplay();
    }
  }
  
  /**
   * Checkout - Place order
   */
  async function checkout() {
    if (cart.length === 0) {
      UIUtils.showErrorModal('Cart Empty', 'Please add items to your cart before placing an order.');
      return;
    }
    
    UIUtils.setButtonLoading('checkout-btn', true);
    
    const total = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.count), 0);
    
    const orderData = {
      items: cart.map(item => ({
        dish_id: item.dish_id,
        count: item.count
      })),
      total_price: parseFloat(total.toFixed(2))
    };
    
    try {
      const result = await apiPost('/api/orders', orderData);
      
      if (result.success || result.order_id) {
        // Clear cart
        cart = [];
        sessionStorage.removeItem('cart');
        updateCartDisplay();
        
        // Show success message
        UIUtils.showSuccessModal(result.order_id || 'N/A', total);
      } else {
        throw new Error(result.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      UIUtils.showErrorModal('Order Failed', 'Unable to place order. Please try again.');
      UIUtils.setButtonLoading('checkout-btn', false);
    }
  }
  
  // Public API
  return {
    init,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    checkout
  };
})();

// Make it available globally
window.StudentOrderPage = StudentOrderPage;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  StudentOrderPage.init();
});