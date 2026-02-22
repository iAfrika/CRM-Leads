// reports/static/js/report_list.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize interactive elements
    initializeReportList();
});

/**
 * Initialize all interactive elements on the report list page
 */
function initializeReportList() {
    // Set up tab navigation
    setupTabs();
    
    // Set up favorite toggles
    setupFavoriteToggles();
    
    // Set up delete confirmations
    setupDeleteConfirmations();
    
    // Set up sorting functionality
    setupTableSorting();
    
    // Set up search functionality
    setupSearch();
}

/**
 * Set up tab navigation
 */
function setupTabs() {
    const tabs = document.querySelectorAll('.reports-tabs .tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            // This is handled by the href, but we can add additional functionality here
            // For example, we could add a loading indicator
            
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
        });
    });
}

/**
 * Set up favorite toggles
 */
function setupFavoriteToggles() {
    const favoriteButtons = document.querySelectorAll('form[action*="toggle_favorite"] button');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const form = this.closest('form');
            const reportId = form.action.split('/').filter(Boolean).pop();
            
            // Send AJAX request to toggle favorite status
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(new FormData(form))
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle button appearance
                    if (data.is_favorite) {
                        button.classList.remove('btn-outline-warning');
                        button.classList.add('btn-warning');
                        button.title = 'Remove from favorites';
                    } else {
                        button.classList.remove('btn-warning');
                        button.classList.add('btn-outline-warning');
                        button.title = 'Add to favorites';
                    }
                    
                    // Show success message
                    showNotification(data.message, 'success');
                } else {
                    // Show error message
                    showNotification(data.message || 'An error occurred', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while updating favorite status', 'error');
            });
        });
    });
}

/**
 * Set up delete confirmations
 */
function setupDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('form[action*="delete_report"] button');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // The onclick attribute handles the confirmation dialog
            // This function can be used to add additional functionality
            
            // For example, we could add a loading state to the button
            button.disabled = true;
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Re-enable the button after submission (in case the user cancels)
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalHTML;
            }, 500);
        });
    });
}

/**
 * Set up table sorting
 */
function setupTableSorting() {
    const tableHeaders = document.querySelectorAll('.reports-table th');
    
    tableHeaders.forEach(header => {
        // Skip the actions column
        if (header.textContent.trim() === 'Actions') return;
        
        header.style.cursor = 'pointer';
        header.title = 'Click to sort';
        
        // Add sort icons
        const sortIcon = document.createElement('i');
        sortIcon.classList.add('fas', 'fa-sort', 'ml-1');
        sortIcon.style.marginLeft = '0.5rem';
        sortIcon.style.opacity = '0.3';
        header.appendChild(sortIcon);
        
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Get the index of the clicked column
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            
            // Determine sort direction
            const currentDirection = this.getAttribute('data-sort') || 'none';
            let newDirection = 'asc';
            
            if (currentDirection === 'asc') {
                newDirection = 'desc';
            } else if (currentDirection === 'desc') {
                newDirection = 'asc';
            }
            
            // Update sort direction attribute
            tableHeaders.forEach(h => h.setAttribute('data-sort', 'none'));
            this.setAttribute('data-sort', newDirection);
            
            // Update sort icons
            tableHeaders.forEach(h => {
                const icon = h.querySelector('i');
                icon.className = 'fas fa-sort ml-1';
                icon.style.opacity = '0.3';
            });
            
            const icon = this.querySelector('i');
            icon.className = `fas fa-sort-${newDirection === 'asc' ? 'up' : 'down'} ml-1`;
            icon.style.opacity = '1';
            
            // Sort the rows
            rows.sort((a, b) => {
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();
                
                // Check if the values are dates
                const aDate = new Date(aValue);
                const bDate = new Date(bValue);
                
                if (!isNaN(aDate) && !isNaN(bDate)) {
                    return newDirection === 'asc' ? aDate - bDate : bDate - aDate;
                }
                
                // Regular string comparison
                return newDirection === 'asc' 
                    ? aValue.localeCompare(bValue) 
                    : bValue.localeCompare(aValue);
            });
            
            // Reorder the rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

/**
 * Set up search functionality
 */
function setupSearch() {
    // Check if search input exists
    const searchContainer = document.querySelector('.reports-header');
    if (!searchContainer) return;
    
    // Create search input
    const searchDiv = document.createElement('div');
    searchDiv.className = 'reports-search';
    searchDiv.style.marginTop = '1rem';
    searchDiv.style.width = '100%';
    searchDiv.style.position = 'relative';
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search reports...';
    searchInput.className = 'search-input';
    searchInput.style.width = '100%';
    searchInput.style.padding = '0.5rem 1rem 0.5rem 2.5rem';
    searchInput.style.borderRadius = '0.5rem';
    searchInput.style.border = '1px solid #e5e7eb';
    
    const searchIcon = document.createElement('i');
    searchIcon.className = 'fas fa-search';
    searchIcon.style.position = 'absolute';
    searchIcon.style.left = '1rem';
    searchIcon.style.top = '50%';
    searchIcon.style.transform = 'translateY(-50%)';
    searchIcon.style.color = '#9ca3af';
    
    searchDiv.appendChild(searchIcon);
    searchDiv.appendChild(searchInput);
    searchContainer.appendChild(searchDiv);
    
    // Add search functionality
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('.reports-table tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Show/hide empty state
        const noResults = document.querySelector('.no-results');
        const visibleRows = document.querySelectorAll('.reports-table tbody tr:not([style*="display: none"])');
        
        if (visibleRows.length === 0 && searchTerm !== '') {
            if (!noResults) {
                const noResultsDiv = document.createElement('div');
                noResultsDiv.className = 'no-results';
                noResultsDiv.style.padding = '2rem';
                noResultsDiv.style.textAlign = 'center';
                noResultsDiv.style.color = '#6b7280';
                noResultsDiv.innerHTML = `No reports found matching "<strong>${searchTerm}</strong>"`;
                
                const table = document.querySelector('.reports-table');
                table.style.display = 'none';
                table.parentNode.appendChild(noResultsDiv);
            } else {
                noResults.innerHTML = `No reports found matching "<strong>${searchTerm}</strong>"`;
                noResults.style.display = 'block';
            }
        } else if (noResults) {
            noResults.style.display = 'none';
            document.querySelector('.reports-table').style.display = '';
        }
    });
}

/**
 * Get CSRF token from cookies
 */
function getCsrfToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1];
    
    return cookieValue;
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    // Check if notifications container exists
    let container = document.querySelector('.notifications-container');
    
    if (!container) {
        container = document.createElement('div');
        container.className = 'notifications-container';
        container.style.position = 'fixed';
        container.style.top = '1rem';
        container.style.right = '1rem';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.backgroundColor = type === 'success' ? '#ecfdf5' : type === 'error' ? '#fee2e2' : '#eff6ff';
    notification.style.color = type === 'success' ? '#065f46' : type === 'error' ? '#b91c1c' : '#1e40af';
    notification.style.padding = '1rem';
    notification.style.borderRadius = '0.5rem';
    notification.style.marginBottom = '0.5rem';
    notification.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.justifyContent = 'space-between';
    notification.style.minWidth = '300px';
    
    // Add icon based on type
    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle' : 
                    type === 'error' ? 'fas fa-exclamation-circle' : 
                    'fas fa-info-circle';
    icon.style.marginRight = '0.5rem';
    
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '&times;';
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontSize = '1.25rem';
    closeButton.style.marginLeft = '0.5rem';
    closeButton.style.color = 'inherit';
    closeButton.style.opacity = '0.7';
    closeButton.addEventListener('click', () => {
        notification.remove();
    });
    
    const contentDiv = document.createElement('div');
    contentDiv.style.display = 'flex';
    contentDiv.style.alignItems = 'center';
    contentDiv.appendChild(icon);
    contentDiv.appendChild(messageSpan);
    
    notification.appendChild(contentDiv);
    notification.appendChild(closeButton);
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
} 