// reports.js - Reports module (Admin only)

const Reports = (() => {
  
  /**
   * Set date range shortcuts
   */
  function setDateRange(period) {
    const endDate = new Date();
    const startDate = new Date();
    
    if (period === 'today') {
      // Already set to today
    } else if (period === 'week') {
      startDate.setDate(endDate.getDate() - 7);
    } else if (period === 'month') {
      startDate.setMonth(endDate.getMonth() - 1);
    }
    
    document.getElementById('report-start-date').value = startDate.toISOString().split('T')[0];
    document.getElementById('report-end-date').value = endDate.toISOString().split('T')[0];
  }

  /**
   * Initialize report dates to today
   */
  function initDates() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('report-end-date').value = today;
    document.getElementById('report-start-date').value = today;
  }

  /**
   * Generate report
   */
  async function generate() {
    const startDate = document.getElementById('report-start-date').value;
    const endDate = document.getElementById('report-end-date').value;
    
    if (!startDate || !endDate) {
      showAlert('Please select both start and end dates', 'warning');
      return;
    }
    
    const reportOptions = {
      start_date: startDate,
      end_date: endDate,
      include_sales: document.getElementById('include-sales').checked,
      include_orders: document.getElementById('include-orders').checked,
      include_dishes: document.getElementById('include-dishes').checked,
      include_revenue: document.getElementById('include-revenue').checked
    };
    
    try {
      const data = await apiPost('/api/admin/reports', reportOptions);
      display(data);
    } catch (error) {
      console.error('Error generating report:', error);
      showAlert('Failed to generate report. Please try again.', 'error');
    }
  }

  /**
   * Display report
   */
  function display(data) {
    const container = document.getElementById('reports-container');
    
    if (!container) {
      console.error('Reports container not found');
      return;
    }

    let html = `
      <div style="background: var(--bounty-white); padding: 1.5rem; border-radius: var(--radius);">
        <h4 style="margin-top: 0;">Report Generated</h4>
        <p style="margin-bottom: 1.5rem;">
          <strong>Period:</strong> ${data.start_date} to ${data.end_date}
        </p>
    `;
    
    // Sales Summary
    if (data.sales_summary) {
      html += `
        <div style="margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #eee;">
          <h5 style="margin-bottom: 0.5rem;">Sales Summary</h5>
          <p style="margin: 0.3rem 0;"><strong>Total Orders:</strong> ${data.sales_summary.total_orders || 0}</p>
          <p style="margin: 0.3rem 0;"><strong>Total Revenue:</strong> ${formatCurrency(data.sales_summary.total_revenue)}</p>
          <p style="margin: 0.3rem 0;"><strong>Average Order Value:</strong> ${formatCurrency(data.sales_summary.avg_order_value)}</p>
        </div>
      `;
    }
    
    // Orders Analysis
    if (data.orders_analysis) {
      html += `
        <div style="margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #eee;">
          <h5 style="margin-bottom: 0.5rem;">Orders Analysis</h5>
          <p style="margin: 0.3rem 0;"><strong>Completed Orders:</strong> ${data.orders_analysis.completed || 0}</p>
          <p style="margin: 0.3rem 0;"><strong>Pending Orders:</strong> ${data.orders_analysis.pending || 0}</p>
          <p style="margin: 0.3rem 0;"><strong>Cancelled Orders:</strong> ${data.orders_analysis.cancelled || 0}</p>
        </div>
      `;
    }
    
    // Popular Dishes
    if (data.popular_dishes && data.popular_dishes.length > 0) {
      html += `
        <div style="margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #eee;">
          <h5 style="margin-bottom: 0.5rem;">Top 5 Popular Dishes</h5>
          <ol style="margin: 0; padding-left: 1.5rem;">
            ${data.popular_dishes.slice(0, 5).map(dish => `
              <li style="margin: 0.3rem 0;">
                <strong>${dish.name}</strong> - ${dish.order_count} orders, ${formatCurrency(dish.total_revenue)} revenue
              </li>
            `).join('')}
          </ol>
        </div>
      `;
    }
    
    // Revenue Breakdown
    if (data.revenue_breakdown) {
      html += `
        <div style="margin-bottom: 1rem;">
          <h5 style="margin-bottom: 0.5rem;">Revenue Breakdown</h5>
          <p style="margin: 0.3rem 0;"><strong>Total Items Sold:</strong> ${data.revenue_breakdown.total_items_sold || 0}</p>
          <p style="margin: 0.3rem 0;"><strong>Average Items per Order:</strong> ${(data.revenue_breakdown.avg_items_per_order || 0).toFixed(2)}</p>
        </div>
      `;
    }
    
    html += `
        <small style="display: block; margin-top: 1rem;">Generated: ${formatDateTime(new Date())}</small>
      </div>
    `;
    
    container.innerHTML = html;
  }

  // Public API
  return {
    setDateRange,
    initDates,
    generate,
    display
  };
})();

// Make it available globally
window.Reports = Reports;