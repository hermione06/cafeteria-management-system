// modal.js - Modal utility functions

const Modal = (() => {
  
  /**
   * Show modal by ID
   */
  function show(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = modal.style.display === 'flex' ? 'flex' : 'block';
    }
  }

  /**
   * Close modal by ID
   */
  function close(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'none';
    }
  }

  /**
   * Initialize modal close on outside click
   */
  function initOutsideClick(...modalIds) {
    window.onclick = function(event) {
      modalIds.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
          close(modalId);
        }
      });
    };
  }

  /**
   * Initialize modal close on escape key
   */
  function initEscapeKey(...modalIds) {
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        modalIds.forEach(modalId => close(modalId));
      }
    });
  }

  // Public API
  return {
    show,
    close,
    initOutsideClick,
    initEscapeKey
  };
})();

// Make it available globally
window.Modal = Modal;