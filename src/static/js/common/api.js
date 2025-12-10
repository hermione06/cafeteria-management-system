// api.js - Common API helper functions

/**
 * Generic fetch wrapper with error handling
 */
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
}

/**
 * GET request
 */
async function apiGet(url) {
  return apiRequest(url, { method: 'GET' });
}

/**
 * POST request
 */
async function apiPost(url, data) {
  return apiRequest(url, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

/**
 * PUT request
 */
async function apiPut(url, data) {
  return apiRequest(url, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

/**
 * DELETE request
 */
async function apiDelete(url) {
  return apiRequest(url, { method: 'DELETE' });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
  alert(message);
}

/**
 * Confirm dialog
 */
function confirmAction(message) {
  return confirm(message);
}

/**
 * Format currency
 */
function formatCurrency(amount) {
  return `$${parseFloat(amount || 0).toFixed(2)}`;
}

/**
 * Format date
 */
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString();
}

/**
 * Format datetime
 */
function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString();
}