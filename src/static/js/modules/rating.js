// ratings.js - Ratings module

const Ratings = (() => {
  let selectedRating = 0;

  /**
   * Initialize rating modal
   */
  function init() {
    // Set up modal close handlers
    const ratingModal = document.getElementById('rating-modal');
    if (ratingModal) {
      window.onclick = function(event) {
        if (event.target === ratingModal) {
          close();
        }
      };
    }
  }

  /**
   * Open rating modal
   */
  function open(dishId, orderId, dishName) {
    document.getElementById('rating-modal-title').textContent = `Rate: ${dishName}`;
    document.getElementById('rating-dish-id').value = dishId;
    document.getElementById('rating-order-id').value = orderId;
    document.getElementById('rating-comment').value = '';
    selectedRating = 0;
    
    // Reset stars
    document.querySelectorAll('.rating-star').forEach(star => {
      star.style.opacity = '0.3';
    });
    
    Modal.show('rating-modal');
  }

  /**
   * Close rating modal
   */
  function close() {
    Modal.close('rating-modal');
  }

  /**
   * Select rating (1-5 stars)
   */
  function selectRating(rating) {
    selectedRating = rating;
    document.querySelectorAll('.rating-star').forEach((star, index) => {
      star.style.opacity = index < rating ? '1' : '0.3';
    });
  }

  /**
   * Submit rating
   */
  async function submit(event) {
    if (event) event.preventDefault();
    
    if (selectedRating === 0) {
      showAlert('Please select a rating', 'warning');
      return false;
    }
    
    const dishId = document.getElementById('rating-dish-id').value;
    const orderId = document.getElementById('rating-order-id').value;
    const comment = document.getElementById('rating-comment').value.trim();
    
    try {
      await apiPost('/api/ratings', {
        dish_id: parseInt(dishId),
        score: selectedRating,
        comment: comment || null
      });
      
      showAlert('Rating submitted successfully!', 'success');
      close();
      return true;
    } catch (error) {
      console.error('Error submitting rating:', error);
      showAlert('Failed to submit rating. Please try again.', 'error');
      return false;
    }
  }

  /**
   * Display rating items for an order
   */
  function displayForOrder(order, containerId) {
    const container = document.getElementById(containerId);
    
    if (!container || !order.items) {
      return;
    }

    container.innerHTML = order.items.map(item => `
      <div style="background: white; padding: 0.8rem; border-radius: var(--radius); margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
        <span>${item.name}</span>
        <button class="btn" onclick="Ratings.open(${item.dish_id}, ${order.order_id}, '${item.name}')" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;">Rate</button>
      </div>
    `).join('');
  }

  // Public API
  return {
    init,
    open,
    close,
    selectRating,
    submit,
    displayForOrder
  };
})();

// Make it available globally
window.Ratings = Ratings;