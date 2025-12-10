// admin-orders.js - Admin orders management page (FIXED VERSION)

const AdminOrdersPage = (() => {
  let currentFilter = 'active';
  
  /**
   * Initialize the page
   */
  async function init() {
    await loadOrders();
    setupFilterButtons();
  }
  
  /**
   * Load all orders (using admin endpoint)
   */
  async function loadOrders() {
    try {
      // Use admin endpoint instead of student endpoint
      await Orders.load('/api/admin/orders');
      renderOrders();
    } catch (error) {
      console.error('Error loading orders:', error);
      document.getElementById('orders-container').innerHTML = 
        '<p style="text-align: center; color: #888;">Unable to load orders.</p>';
    }
  }
  
  /**
   * Setup filter button listeners
   */
  function setupFilterButtons() {
    const filterActive = document.getElementById('filter-active');
    const filterCompleted = document.getElementById('filter-completed');
    const filterAll = document.getElementById('filter-all');
    
    if (filterActive) filterActive.addEventListener('click', () => filterOrders('active'));
    if (filterCompleted) filterCompleted.addEventListener('click', () => filterOrders('completed'));
    if (filterAll) filterAll.addEventListener('click', () => filterOrders('all'));
  }
  
  /**
   * Filter orders
   */
  function filterOrders(filter) {
    currentFilter = filter;
    renderOrders();
    updateFilterButtons();
  }
  
  /**
   * Update filter button styles
   */
  function updateFilterButtons() {
    ['active', 'completed', 'all'].forEach(filter => {
      const button = document.getElementById(`filter-${filter}`);
      if (button) {
        button.style.opacity = currentFilter === filter ? '1' : '0.6';
      }
    });
  }
  
  /**
   * Get filtered orders
   */
  function getFilteredOrders() {
    const allOrders = Orders.getAll();
    
    if (currentFilter === 'active') {
      return allOrders.filter(order => order.status === 'pending');
    } else if (currentFilter === 'completed') {
      return allOrders.filter(order => order.status === 'completed' || order.status === 'cancelled');
    }
    return allOrders;
  }
  
  /**
   * Render orders
   */
  function renderOrders() {
    const container = document.getElementById('orders-container');
    const filteredOrders = getFilteredOrders();
    
    if (filteredOrders.length === 0) {
      container.innerHTML = '<p style="text-align: center; color: #888;">No orders found.</p>';
      return;
    }
    
    container.innerHTML = filteredOrders.map(order => createOrderCard(order)).join('');
    
    // Load items for each order
    filteredOrders.forEach(order => loadOrderItems(order.order_id));
  }
  
  /**
   * Create order card HTML
   */
  function createOrderCard(order) {
    return `
      <div style="background: var(--bounty-white); padding: 1.5rem; border-radius: var(--radius); margin-bottom: 1rem; border-left: 4px solid ${Orders.getStatusColor(order.status)}; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <!-- Order Header -->
        <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #eee;">
          <div>
            <h3 style="margin: 0 0 0.5rem 0; color: var(--bounty-blue);">Order #${order.order_id}</h3>
            <p style="margin: 0.3rem 0; color: #666; font-size: 0.9rem;">
              <strong>Customer ID:</strong> ${order.student_id || 'Unknown'}
            </p>
            <p style="margin: 0.3rem 0; color: #666; font-size: 0.9rem;">
              <strong>Date:</strong> ${formatDateTime(order.date_created)}
            </p>
            <p style="margin: 0.3rem 0; font-size: 0.9rem;">
              <strong>Status:</strong> 
              <span style="color: ${Orders.getStatusColor(order.status)}; text-transform: uppercase; font-weight: 600;">
                ${order.status}
              </span>
            </p>
          </div>
          <div style="text-align: right;">
            <p style="margin: 0; font-size: 1.5rem; font-weight: bold; color: var(--bounty-brown);">
              ${formatCurrency(order.total_price)}
            </p>
          </div>
        </div>
        
        <!-- Order Items -->
        <div style="margin-bottom: 1rem;">
          <h4 style="margin: 0 0 0.5rem 0; color: var(--bounty-blue); font-size: 1rem;">Items:</h4>
          <div id="order-items-${order.order_id}" style="display: grid; gap: 0.5rem;">
            <p style="margin: 0; color: #888; font-size: 0.9rem;">Loading items...</p>
          </div>
        </div>
        
        <!-- Action Buttons -->
        ${createActionButtons(order)}
      </div>
    `;
  }
  
  /**
   * Create action buttons based on order status
   */
  function createActionButtons(order) {
    if (order.status === 'pending') {
      return `
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <button class="btn" onclick="AdminOrdersPage.updateStatus(${order.order_id}, 'completed')" 
                  style="flex: 1; min-width: 120px; background-color: #28a745;">
            Mark as Completed
          </button>
          <button class="btn" onclick="AdminOrdersPage.updateStatus(${order.order_id}, 'cancelled')" 
                  style="flex: 1; min-width: 120px; background-color: #dc3545;">
            Cancel Order
          </button>
        </div>
      `;
    }
    return `
      <p style="margin: 0; text-align: center; color: #888; font-size: 0.9rem; font-style: italic;">
        This order has been ${order.status}
      </p>
    `;
  }
  
  /**
   * Load items for a specific order
   */
  async function loadOrderItems(orderId) {
    try {
      const orderDetails = await Orders.getDetails(orderId);
      const itemsContainer = document.getElementById(`order-items-${orderId}`);
      
      if (itemsContainer && orderDetails.items) {
        itemsContainer.innerHTML = orderDetails.items.map(item => `
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: var(--bounty-light); border-radius: 4px;">
            <span style="color: #333;">
              <strong>${item.name}</strong>
            </span>
            <span style="color: #666;">
              x${item.count} @ ${formatCurrency(item.price)} = ${formatCurrency(parseFloat(item.price) * item.count)}
            </span>
          </div>
        `).join('');
      }
    } catch (error) {
      console.error(`Error loading items for order ${orderId}:`, error);
      const itemsContainer = document.getElementById(`order-items-${orderId}`);
      if (itemsContainer) {
        itemsContainer.innerHTML = '<p style="margin: 0; color: #dc3545; font-size: 0.9rem;">Failed to load items</p>';
      }
    }
  }
  
  /**
   * Update order status
   */
  async function updateStatus(orderId, newStatus) {
    const confirmMessage = newStatus === 'completed' 
      ? 'Mark this order as completed?' 
      : 'Cancel this order? This action cannot be undone.';
    
    if (!confirmAction(confirmMessage)) {
      return;
    }
    
    try {
      await apiPut(`/api/admin/orders/${orderId}`, { status: newStatus });
      
      const successMessage = newStatus === 'completed' 
        ? 'Order marked as completed!' 
        : 'Order cancelled successfully.';
      
      showAlert(successMessage, 'success');
      await loadOrders(); // Reload orders
    } catch (error) {
      console.error('Error updating order status:', error);
      showAlert('Failed to update order status. Please try again.', 'error');
    }
  }
  
  // Public API
  return {
    init,
    filterOrders,
    updateStatus
  };
})();

// Make it available globally
window.AdminOrdersPage = AdminOrdersPage;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  AdminOrdersPage.init();
});