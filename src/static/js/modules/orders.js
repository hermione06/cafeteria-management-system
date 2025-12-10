// orders.js - Orders module (FIXED VERSION)

const Orders = (() => {
  let allOrders = [];
  let showingAll = false;
  let currentPage = 1;
  let ordersPerPage = 10;

  /**
   * Load orders from API
   * @param {string} endpoint - API endpoint to use (defaults to student endpoint)
   */
  async function load(endpoint = '/api/orders') {
    try {
      const data = await apiGet(endpoint);
      allOrders = (data.orders || data || []).sort((a, b) => 
        new Date(b.date_created) - new Date(a.date_created)
      );
      return allOrders;
    } catch (error) {
      console.error('Error loading orders:', error);
      throw error;
    }
  }

  /**
   * Get order details by ID
   */
  async function getDetails(orderId) {
    try {
      return await apiGet(`/api/orders/${orderId}`);
    } catch (error) {
      console.error(`Error loading order ${orderId}:`, error);
      throw error;
    }
  }

  /**
   * Get status color
   */
  function getStatusColor(status) {
    const colors = {
      pending: '#ffc107',
      completed: '#28a745',
      cancelled: '#dc3545'
    };
    return colors[status] || '#6c757d';
  }

  /**
   * Render orders list
   */
  function display(containerId, options = {}) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    let displayOrders;
    
    if (showingAll) {
      const startIndex = (currentPage - 1) * ordersPerPage;
      const endIndex = startIndex + ordersPerPage;
      displayOrders = allOrders.slice(startIndex, endIndex);
    } else {
      displayOrders = allOrders.slice(0, 5);
    }

    if (displayOrders.length === 0) {
      container.innerHTML = '<p style="color: #888;">No orders found.</p>';
      return;
    }

    const onClickHandler = options.onClick || 'Orders.viewDetails';
    
    container.innerHTML = displayOrders.map(order => `
      <div style="background: var(--bounty-light); padding: 1rem; border-radius: var(--radius); margin-bottom: 1rem; border-left: 4px solid ${getStatusColor(order.status)}; cursor: pointer; transition: transform 0.2s;" onclick="${onClickHandler}(${order.order_id})">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <p style="margin: 0;"><strong>Order #${order.order_id}</strong></p>
            <p style="margin: 0.3rem 0; font-size: 0.9rem;">${formatDate(order.date_created)}</p>
            <p style="margin: 0.3rem 0; font-size: 0.85rem; text-transform: uppercase; font-weight: 600; color: ${getStatusColor(order.status)};">${order.status}</p>
          </div>
          <div style="text-align: right;">
            <p style="margin: 0; font-weight: bold; font-size: 1.1rem;">${formatCurrency(order.total_price)}</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">Click to view details</p>
          </div>
        </div>
      </div>
    `).join('');
  }

  /**
   * Toggle between showing all or recent orders
   */
  function toggleShowAll() {
    showingAll = !showingAll;
    currentPage = 1;
    return showingAll;
  }

  /**
   * Change page for pagination
   */
  function changePage(direction) {
    const totalPages = Math.ceil(allOrders.length / ordersPerPage);
    currentPage += direction;
    if (currentPage < 1) currentPage = 1;
    if (currentPage > totalPages) currentPage = totalPages;
    return { currentPage, totalPages };
  }

  /**
   * Get pagination info
   */
  function getPaginationInfo() {
    return {
      currentPage,
      totalPages: Math.ceil(allOrders.length / ordersPerPage),
      showingAll
    };
  }

  /**
   * View order details in modal
   */
  async function viewDetails(orderId, modalContentId = 'order-details-content') {
    try {
      const order = await getDetails(orderId);
      
      const itemsTable = (order.items || []).map(item => {
        const itemTotal = parseFloat(item.price) * item.count;
        return `
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 0.5rem;">${item.name}</td>
            <td style="padding: 0.5rem; text-align: center;">${item.count}</td>
            <td style="padding: 0.5rem; text-align: right;">${formatCurrency(item.price)}</td>
            <td style="padding: 0.5rem; text-align: right; font-weight: bold;">${formatCurrency(itemTotal)}</td>
          </tr>
        `;
      }).join('');
      
      const detailsHTML = `
        <div style="background: white; padding: 2rem; border-radius: var(--radius); max-width: 600px; margin: 0 auto;">
          <h3 style="margin-top: 0; margin-bottom: 1rem;">Order #${orderId} Details</h3>
          
          <div style="margin-bottom: 1.5rem;">
            <p style="margin: 0.3rem 0;"><strong>Date:</strong> ${formatDateTime(order.date_created)}</p>
            <p style="margin: 0.3rem 0;"><strong>Status:</strong> <span style="color: ${getStatusColor(order.status)}; text-transform: uppercase; font-weight: 600;">${order.status}</span></p>
          </div>
          
          <h4 style="margin-bottom: 0.5rem;">Items:</h4>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 1rem;">
            <thead>
              <tr style="background: var(--bounty-light); border-bottom: 2px solid #ddd;">
                <th style="padding: 0.5rem; text-align: left;">Dish</th>
                <th style="padding: 0.5rem; text-align: center;">Quantity</th>
                <th style="padding: 0.5rem; text-align: right;">Price</th>
                <th style="padding: 0.5rem; text-align: right;">Total</th>
              </tr>
            </thead>
            <tbody>
              ${itemsTable}
            </tbody>
            <tfoot>
              <tr style="border-top: 2px solid #ddd;">
                <td colspan="3" style="padding: 0.7rem; text-align: right; font-weight: bold;">Order Total:</td>
                <td style="padding: 0.7rem; text-align: right; font-weight: bold; font-size: 1.1rem;">${formatCurrency(order.total_price)}</td>
              </tr>
            </tfoot>
          </table>
          
          <button class="btn" onclick="Modal.close('order-details-modal')" style="width: 100%;">Close</button>
        </div>
      `;
      
      document.getElementById(modalContentId).innerHTML = detailsHTML;
      Modal.show('order-details-modal');
      
    } catch (error) {
      showAlert('Failed to load order details. Please try again.', 'error');
    }
  }

  /**
   * Get statistics
   */
  function getStats() {
    const totalOrders = allOrders.length;
    const pendingOrders = allOrders.filter(o => o.status === 'pending').length;
    const totalSpent = allOrders
      .filter(o => o.status !== 'cancelled')
      .reduce((sum, o) => sum + parseFloat(o.total_price || 0), 0);
    
    return {
      totalOrders,
      pendingOrders,
      totalSpent
    };
  }

  /**
   * Get most recent order
   */
  function getMostRecent() {
    return allOrders.length > 0 ? allOrders[0] : null;
  }

  /**
   * Get all orders
   */
  function getAll() {
    return allOrders;
  }

  // Public API
  return {
    load,
    getDetails,
    display,
    toggleShowAll,
    changePage,
    getPaginationInfo,
    viewDetails,
    getStats,
    getMostRecent,
    getAll,
    getStatusColor
  };
})();

// Make it available globally
window.Orders = Orders;