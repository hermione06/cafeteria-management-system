// student-dashboard.js - Main student dashboard script

// Load dashboard
async function loadDashboard() {
  try {
    // Fetch profile
    const profile = await apiGet('/api/profile');
    document.getElementById('student-name').textContent = profile.name || 'Student';

    // Load orders
    await Orders.load();
    
    // Display stats
    const stats = Orders.getStats();
    document.getElementById('total-orders').textContent = stats.totalOrders;
    document.getElementById('pending-orders').textContent = stats.pendingOrders;
    document.getElementById('total-spent').textContent = formatCurrency(stats.totalSpent);

    // Load most recent order
    const recentOrder = Orders.getMostRecent();
    if (recentOrder) {
      await loadMostRecentOrder(recentOrder);
    }

    // Render orders
    renderOrders();
    
  } catch (err) {
    console.error('Error loading dashboard:', err);
    document.getElementById('orders-container').innerHTML = 
      '<p style="color: #888;">Unable to load orders.</p>';
  }
}

// Load most recent order with rating prompts
async function loadMostRecentOrder(order) {
  try {
    const orderDetails = await Orders.getDetails(order.order_id);
    
    document.getElementById('recent-order-section').style.display = 'block';
    document.getElementById('recent-order-id').textContent = order.order_id;
    document.getElementById('recent-order-date').textContent = formatDate(order.date_created);
    document.getElementById('recent-order-status').textContent = order.status;
    document.getElementById('recent-order-total').textContent = formatCurrency(order.total_price);
    
    // Display items
    const itemsHtml = (orderDetails.items || []).map(item => `
      <p style="margin: 0.3rem 0;">• ${item.name} x${item.count}</p>
    `).join('');
    document.getElementById('recent-order-items').innerHTML = itemsHtml;
    
    // Display rating options
    Ratings.displayForOrder(orderDetails, 'rating-items');
    
  } catch (err) {
    console.error('Error loading recent order:', err);
  }
}

// Render orders list
function renderOrders() {
  Orders.display('orders-container', {
    onClick: 'viewOrderDetails'
  });
  
  const paginationInfo = Orders.getPaginationInfo();
  
  if (paginationInfo.showingAll) {
    document.getElementById('pagination-container').style.display = 'block';
    document.getElementById('page-info').textContent = 
      `Page ${paginationInfo.currentPage} of ${paginationInfo.totalPages}`;
  } else {
    document.getElementById('pagination-container').style.display = 'none';
  }
}

// Toggle all orders view
function toggleAllOrders() {
  const showingAll = Orders.toggleShowAll();
  document.getElementById('toggle-orders-btn').textContent = 
    showingAll ? 'Show Recent Only' : 'View All Orders';
  renderOrders();
}

// Change page
function changePage(direction) {
  Orders.changePage(direction);
  renderOrders();
}

// View order details
async function viewOrderDetails(orderId) {
  await Orders.viewDetails(orderId);
}

// Open rating modal
function openRatingModal(dishId, orderId, dishName) {
  Ratings.open(dishId, orderId, dishName);
}

// Close rating modal
function closeRatingModal() {
  Ratings.close();
}

// Close order details modal
function closeOrderDetailsModal() {
  Modal.close('order-details-modal');
}

// Select rating
function selectRating(rating) {
  Ratings.selectRating(rating);
}

// Submit rating
async function submitRating(event) {
  const success = await Ratings.submit(event);
  if (success) {
    loadDashboard(); // Reload to update
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  Ratings.init();
  Modal.initOutsideClick('rating-modal', 'order-details-modal');
});