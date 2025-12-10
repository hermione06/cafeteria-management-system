// announcements.js - Announcements module

const Announcements = (() => {
  let allAnnouncements = [];
  let showingAll = false;

  /**
   * Load announcements from API
   */
  async function load() {
    try {
      const data = await apiGet('/api/announcements');
      allAnnouncements = data.announcements || data || [];
      return allAnnouncements;
    } catch (error) {
      console.error('Error loading announcements:', error);
      throw error;
    }
  }

  /**
   * Display announcements in container
   */
  function display(containerId, showAll = false) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    if (allAnnouncements.length === 0) {
      container.innerHTML = '<p style="color: #888;">No announcements at this time.</p>';
      return;
    }

    const announcementsToShow = showAll ? allAnnouncements : allAnnouncements.slice(0, 5);
    
    container.innerHTML = announcementsToShow.map(ann => `
      <div class="announcement-item">
        <p>${ann.message}</p>
        <small>${formatDate(ann.date_posted)}</small>
      </div>
    `).join('');
  }

  /**
   * Display announcements with admin controls (delete button)
   */
  function displayAdmin(containerId, onDelete) {
    const container = document.getElementById(containerId);
    
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    if (allAnnouncements.length === 0) {
      container.innerHTML = '<p style="color: #888;">No announcements posted.</p>';
      return;
    }

    container.innerHTML = allAnnouncements.slice(0, 10).map(ann => `
      <div style="background: var(--bounty-white); padding: 1rem; border-radius: var(--radius); margin-bottom: 1rem; border-left: 4px solid var(--bounty-blue); display: flex; justify-content: space-between; align-items: start; gap: 1rem;">
        <div style="flex: 1;">
          <p style="margin: 0 0 0.5rem 0;">${ann.message}</p>
          <small>${formatDateTime(ann.date_posted)}</small>
        </div>
        <button class="btn" onclick="Announcements.deleteAnnouncement(${ann.announcement_id})" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Delete</button>
      </div>
    `).join('');
  }

  /**
   * Toggle between showing all or limited announcements
   */
  function toggleShowAll(containerId) {
    showingAll = !showingAll;
    display(containerId, showingAll);
    return showingAll;
  }

  /**
   * Create new announcement (admin only)
   */
  async function create(message) {
    try {
      await apiPost('/api/announcements', { message });
      await load();
      return true;
    } catch (error) {
      console.error('Error creating announcement:', error);
      throw error;
    }
  }

  /**
   * Delete announcement (admin only)
   */
  async function deleteAnnouncement(announcementId) {
    if (!confirmAction('Are you sure you want to delete this announcement?')) {
      return false;
    }

    try {
      await apiDelete(`/api/announcements/${announcementId}`);
      await load();
      return true;
    } catch (error) {
      console.error('Error deleting announcement:', error);
      throw error;
    }
  }

  /**
   * Get all announcements
   */
  function getAll() {
    return allAnnouncements;
  }

  /**
   * Get count of announcements
   */
  function count() {
    return allAnnouncements.length;
  }

  // Public API
  return {
    load,
    display,
    displayAdmin,
    toggleShowAll,
    create,
    deleteAnnouncement,
    getAll,
    count
  };
})();

// Make it available globally
window.Announcements = Announcements;