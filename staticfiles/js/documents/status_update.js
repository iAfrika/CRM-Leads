/**
 * Status Update functionality for documents
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeStatusUpdate();
    initializeInlineStatusUpdates();
    initializeTopStatusUpdate();
});

/**
 * Initialize status update modal functionality
 */
function initializeStatusUpdate() {
    const statusUpdateForm = document.getElementById('statusUpdateForm');
    if (statusUpdateForm) {
        statusUpdateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const documentId = formData.get('document_id');
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value || 
                            document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            fetch(`/documents/${documentId}/update-status/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatusDisplay(data);
                    showNotification('Status updated successfully!', 'success');
                    
                    // Refresh page after a short delay to update other elements
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showNotification('Failed to update status: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while updating the status.', 'error');
            });
        });
    }
}

/**
 * Initialize inline status updates (for list views)
 */
function initializeInlineStatusUpdates() {
    const statusSelects = document.querySelectorAll('.status-select');
    
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const invoiceId = this.dataset.invoiceId;
            const currentStatus = this.dataset.currentStatus;
            const newStatus = this.value;
            
            // If user selected the current status, do nothing
            if (newStatus === currentStatus) {
                return;
            }
            
            // Confirm the change
            if (!confirm(`Are you sure you want to change the status to "${this.options[this.selectedIndex].text}"?`)) {
                this.value = currentStatus; // Reset to original value
                return;
            }
            
            updateInlineStatus(invoiceId, newStatus, this, currentStatus);
        });
    });
}

/**
 * Update status via AJAX for inline updates
 */
function updateInlineStatus(invoiceId, newStatus, selectElement, currentStatus) {
    const formData = new FormData();
    formData.append('status', newStatus);
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value || 
                    document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch(`/documents/${invoiceId}/update-status/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the dataset
            selectElement.dataset.currentStatus = newStatus;
            
            // If status is final, replace dropdown with badge
            if (newStatus === 'PAID' || newStatus === 'CANCELLED') {
                const statusContainer = selectElement.closest('.status-dropdown');
                if (statusContainer) {
                    statusContainer.innerHTML = `
                        <span class="status-badge status-${newStatus.toLowerCase()}">
                            ${data.new_status_display}
                        </span>
                    `;
                }
            }
            
            showNotification('Status updated successfully!', 'success');
        } else {
            showNotification('Failed to update status: ' + data.error, 'error');
            selectElement.value = currentStatus; // Reset to original value
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while updating the status.', 'error');
        selectElement.value = currentStatus; // Reset to original value
    });
}

/**
 * Update status display on the page
 */
function updateStatusDisplay(data) {
    const statusBadge = document.getElementById('current-status-badge');
    if (statusBadge) {
        statusBadge.textContent = data.new_status_display;
        statusBadge.className = `status-badge status-${data.new_status.toLowerCase()}`;
    }
    
    // Hide update button if status is now final
    if (data.new_status === 'PAID' || data.new_status === 'CANCELLED') {
        const updateBtn = document.querySelector('.status-update-btn');
        if (updateBtn) {
            updateBtn.style.display = 'none';
        }
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    // Remove any existing notifications
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        padding: 12px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background: ${getNotificationColor(type, 'bg')};
        color: ${getNotificationColor(type, 'text')};
        border: 1px solid ${getNotificationColor(type, 'border')};
        max-width: 300px;
        font-size: 14px;
        font-weight: 500;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

/**
 * Get notification colors based on type
 */
function getNotificationColor(type, property) {
    const colors = {
        success: {
            bg: '#d4edda',
            text: '#155724',
            border: '#c3e6cb'
        },
        error: {
            bg: '#f8d7da',
            text: '#721c24',
            border: '#f5c6cb'
        },
        info: {
            bg: '#d1ecf1',
            text: '#0c5460',
            border: '#bee5eb'
        },
        warning: {
            bg: '#fff3cd',
            text: '#856404',
            border: '#ffeaa7'
        }
    };
    
    return colors[type] ? colors[type][property] : colors.info[property];
}

/**
 * Add CSS animations if not already present
 */
function addNotificationAnimations() {
    if (!document.getElementById('notification-animations')) {
        const style = document.createElement('style');
        style.id = 'notification-animations';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Initialize top status update form functionality
 */
function initializeTopStatusUpdate() {
    const topStatusUpdateForm = document.getElementById('topStatusUpdateForm');
    if (topStatusUpdateForm) {
        topStatusUpdateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const documentId = formData.get('document_id');
            const newStatus = formData.get('status');
            
            if (!newStatus) {
                showNotification('Please select a status to update to.', 'error');
                return;
            }
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value || 
                            document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            // Disable form while processing
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            
            fetch(`/documents/${documentId}/update-status/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatusDisplay(data);
                    showNotification('Status updated successfully!', 'success');
                    
                    // Refresh page after a short delay to update other elements
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showNotification('Failed to update status: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while updating the status.', 'error');
            })
            .finally(() => {
                // Re-enable form
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            });
        });
    }
}

// Initialize animations when script loads
addNotificationAnimations();

// Make functions available globally
window.showNotification = showNotification;
