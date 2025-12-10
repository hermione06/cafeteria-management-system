// admin-dashboard.js - Main admin dashboard script

// Load dashboard data
async function loadDashboard() {
  await Promise.all([
    AdminStats.load(),
    loadAnnouncementsAdmin()
  ]);
  
  Reports.initDates();
}

// Load statistics
async function loadStats() {
  await AdminStats.load();
}

// Load announcements (admin view)
async function loadAnnouncementsAdmin() {
  try {
    await Announcements.load();
    Announcements.displayAdmin('announcements-list');
  } catch (error) {
    console.error('Error loading announcements:', error);
    document.getElementById('announcements-list').innerHTML = 
      '<p style="color: #888;">Unable to load announcements.</p>';
  }
}

// Show/hide announcement form
function showAddAnnouncementForm() {
  document.getElementById('add-announcement-form').style.display = 'block';
}

function hideAddAnnouncementForm() {
  document.getElementById('add-announcement-form').style.display = 'none';
  document.getElementById('announcement-message').value = '';
}

// Submit announcement
async function submitAnnouncement() {
  const message = document.getElementById('announcement-message').value.trim();
  
  if (!message) {
    showAlert('Please enter an announcement message', 'warning');
    return;
  }
  
  try {
    await Announcements.create(message);
    showAlert('Announcement posted successfully!', 'success');
    hideAddAnnouncementForm();
    loadAnnouncementsAdmin();
  } catch (error) {
    console.error('Error posting announcement:', error);
    showAlert('Failed to post announcement. Please try again.', 'error');
  }
}

// Delete announcement (called from Announcements module)
async function deleteAnnouncementLocal(announcementId) {
  try {
    await Announcements.deleteAnnouncement(announcementId);
    showAlert('Announcement deleted successfully!', 'success');
    loadAnnouncementsAdmin();
  } catch (error) {
    console.error('Error deleting announcement:', error);
    showAlert('Failed to delete announcement. Please try again.', 'error');
  }
}

// Set date range shortcuts
function setDateRange(period) {
  Reports.setDateRange(period);
}

// Generate report
async function generateReport() {
  await Reports.generate();
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);