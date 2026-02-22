/**
 * Modern Admin Interface JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all components
  initAlerts();
  initToggles();
  initSearch();
  initSort();
  initPermissionCheckboxes();
});

/**
 * Alert handling
 */
function initAlerts() {
  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });

  // Add close button functionality
  const closeButtons = document.querySelectorAll('.alert-close');
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const alert = this.closest('.alert');
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    });
  });
}

/**
 * Toggle switches
 */
function initToggles() {
  const toggles = document.querySelectorAll('.toggle-switch');
  toggles.forEach(toggle => {
    toggle.addEventListener('change', async function() {
      const url = this.dataset.url;
      const csrfToken = getCookie('csrftoken');
      
      if (!url) return;
      
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
          },
          body: `is_active=${this.checked}`
        });
        
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        showAlert(data.status === 'success' ? 'success' : 'error', data.message);
      } catch (error) {
        console.error('Error:', error);
        showAlert('error', 'There was an error processing your request');
        this.checked = !this.checked; // Revert toggle
      }
    });
  });
}

/**
 * Search functionality
 */
function initSearch() {
  const searchForm = document.getElementById('search-form');
  if (!searchForm) return;
  
  const searchInput = document.getElementById('search-input');
  const clearButton = document.getElementById('clear-search');
  
  if (clearButton) {
    clearButton.addEventListener('click', function() {
      searchInput.value = '';
      searchForm.submit();
    });
  }
}

/**
 * Table sorting
 */
function initSort() {
  const sortHeaders = document.querySelectorAll('th.sortable');
  sortHeaders.forEach(header => {
    header.addEventListener('click', function() {
      const url = new URL(window.location);
      const direction = this.classList.contains('sorted-asc') ? 'desc' : 'asc';
      const column = this.dataset.column;
      
      if (column) {
        url.searchParams.set('sort', column);
        url.searchParams.set('dir', direction);
        window.location = url.toString();
      }
    });
  });
}

/**
 * Permission checkboxes
 */
function initPermissionCheckboxes() {
  const checkboxes = document.querySelectorAll('.permission-checkbox');
  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', async function() {
      const userId = document.getElementById('user-select')?.value;
      const viewId = this.dataset.viewId;
      const isActive = this.checked;
      
      if (!userId || !viewId) return;
      
      try {
        const response = await fetch(window.location.href, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: `user_id=${userId}&view_id=${viewId}&is_active=${isActive}`
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
          showAlert('success', data.message);
        } else {
          showAlert('error', data.message);
          this.checked = !isActive; // Revert checkbox
        }
      } catch (error) {
        console.error('Error:', error);
        showAlert('error', 'There was an error updating permissions');
        this.checked = !isActive; // Revert checkbox
      }
    });
  });
}

/**
 * Show an alert message
 */
function showAlert(type, message) {
  const alertsContainer = document.getElementById('alerts-container');
  if (!alertsContainer) return;
  
  const alert = document.createElement('div');
  alert.className = `alert alert-${type}`;
  alert.innerHTML = `
    <button type="button" class="alert-close">&times;</button>
    <span>${message}</span>
  `;
  
  alertsContainer.appendChild(alert);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 300);
  }, 5000);
  
  // Add click handler for close button
  alert.querySelector('.alert-close').addEventListener('click', function() {
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 300);
  });
}

/**
 * Get a cookie by name (for CSRF token)
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
} 