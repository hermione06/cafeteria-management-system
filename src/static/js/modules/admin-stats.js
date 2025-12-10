// admin-stats.js - Admin statistics module

const AdminStats = (() => {
  
  /**
   * Load and display statistics
   */
  async function load() {
    try {
      const data = await apiGet('/api/admin/stats');
      display(data);
      return data;
    } catch (error) {
      console.error('Error loading stats:', error);
      throw error;
    }
  }

  /**
   * Display statistics in the dashboard
   */
  function display(data) {
    const stats = {
      'stat-orders-today': data.orders_today || 0,
      'stat-revenue-today': formatCurrency(data.revenue_today),
      'stat-total-orders': data.total_orders || 0,
      'stat-total-revenue': formatCurrency(data.total_revenue),
      'stat-active-dishes': data.active_dishes || 0,
      'stat-total-dishes': data.total_dishes || 0,
      'stat-avg-order': formatCurrency(data.avg_order_value),
      'stat-pending-orders': data.pending_orders || 0
    };

    Object.entries(stats).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) {
        element.textContent = value;
      }
    });
  }

  // Public API
  return {
    load,
    display
  };
})();

// Make it available globally
window.AdminStats = AdminStats;