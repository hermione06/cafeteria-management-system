// utils.js - Shared utility functions for UI components

const UIUtils = (() => {
  
  /**
   * Create and show error modal
   */
  function showErrorModal(title, message) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      animation: fadeIn 0.3s ease;
    `;
    
    const errorBox = document.createElement('div');
    errorBox.style.cssText = `
      background: white;
      padding: 2.5rem 2rem;
      border-radius: var(--radius);
      text-align: center;
      max-width: 450px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      animation: slideIn 0.4s ease;
    `;
    
    errorBox.innerHTML = `
      <div style="font-size: 4rem; color: #dc3545; margin-bottom: 1rem;">⚠</div>
      <h2 style="color: var(--bounty-blue); margin: 0 0 1rem 0;">${title}</h2>
      <p style="color: #666; margin: 1rem 0 1.5rem 0; font-size: 1rem;">
        ${message}
      </p>
      <button class="btn" onclick="UIUtils.closeModal('error-overlay')" style="width: 100%;">
        OK
      </button>
    `;
    
    overlay.appendChild(errorBox);
    overlay.id = 'error-overlay';
    document.body.appendChild(overlay);
    
    addModalAnimations();
  }

  /**
   * Create and show success modal with countdown
   */
  function showSuccessModal(orderId, total, redirectUrl = '/home', countdown = 3) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      animation: fadeIn 0.3s ease;
    `;
    
    const successBox = document.createElement('div');
    successBox.style.cssText = `
      background: white;
      padding: 3rem 2rem;
      border-radius: var(--radius);
      text-align: center;
      max-width: 500px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      animation: slideIn 0.4s ease;
    `;
    
    successBox.innerHTML = `
      <div style="font-size: 4rem; color: #28a745; margin-bottom: 1rem;">✓</div>
      <h2 style="color: var(--bounty-blue); margin: 0 0 1rem 0;">Order Placed Successfully!</h2>
      <p style="color: #666; margin: 0.5rem 0; font-size: 1.1rem;">
        <strong>Order #${orderId}</strong>
      </p>
      <p style="color: #666; margin: 0.5rem 0;">
        Total: <strong style="color: var(--bounty-brown);">${formatCurrency(total)}</strong>
      </p>
      <p style="color: #888; margin: 1.5rem 0; font-size: 0.9rem;">
        You will be redirected in <span id="countdown">${countdown}</span> seconds...
      </p>
      <button class="btn" onclick="UIUtils.redirectTo('${redirectUrl}')" style="width: 100%; margin-top: 1rem;">
        Go to Home Now
      </button>
    `;
    
    overlay.appendChild(successBox);
    overlay.id = 'success-overlay';
    document.body.appendChild(overlay);
    
    addModalAnimations();
    startCountdown(countdown, redirectUrl);
  }

  /**
   * Close modal by ID
   */
  function closeModal(modalId) {
    const overlay = document.getElementById(modalId);
    if (overlay) {
      overlay.remove();
    }
  }

  /**
   * Redirect to URL
   */
  function redirectTo(url) {
    if (window.currentCountdownInterval) {
      clearInterval(window.currentCountdownInterval);
    }
    window.location.href = url;
  }

  /**
   * Start countdown timer
   */
  function startCountdown(seconds, redirectUrl) {
    let remaining = seconds;
    const countdownInterval = setInterval(() => {
      remaining--;
      const countdownEl = document.getElementById('countdown');
      if (countdownEl) {
        countdownEl.textContent = remaining;
      }
      
      if (remaining <= 0) {
        clearInterval(countdownInterval);
        window.location.href = redirectUrl;
      }
    }, 1000);
    
    window.currentCountdownInterval = countdownInterval;
  }

  /**
   * Add modal animations CSS
   */
  function addModalAnimations() {
    if (!document.getElementById('modal-animations')) {
      const style = document.createElement('style');
      style.id = 'modal-animations';
      style.textContent = `
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideIn {
          from { transform: translateY(-50px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }
  }

  /**
   * Set button loading state
   */
  function setButtonLoading(buttonId, loading, originalText = 'Submit') {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    if (loading) {
      button.disabled = true;
      button.dataset.originalText = button.textContent;
      button.textContent = 'Processing...';
    } else {
      button.disabled = false;
      button.textContent = button.dataset.originalText || originalText;
    }
  }

  // Public API
  return {
    showErrorModal,
    showSuccessModal,
    closeModal,
    redirectTo,
    setButtonLoading
  };
})();

// Make it available globally
window.UIUtils = UIUtils;