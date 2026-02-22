// reports/static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard components
    initializeDashboard();
});

/**
 * Initialize all dashboard components
 */
function initializeDashboard() {
    // Initialize stat cards
    initializeStatCards();
    
    // Initialize charts if any
    initializeCharts();
    
    // Set up favorite toggles
    setupFavoriteToggles();
}

/**
 * Initialize stat cards with animations
 */
function initializeStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    // Add animation to stat cards
    statCards.forEach((card, index) => {
        // Add a slight delay to each card for a staggered effect
        const delay = index * 100;
        
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, delay);
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Animate stat values with counting effect
    const statValues = document.querySelectorAll('.stat-card-value');
    
    statValues.forEach(value => {
        const finalValue = parseFloat(value.textContent.replace(/[^0-9.-]+/g, ''));
        
        if (!isNaN(finalValue)) {
            // Start from zero
            value.textContent = '0';
            
            // Determine if it's a percentage or a number
            const isPercentage = value.textContent.includes('%');
            const hasCurrency = value.textContent.includes('$');
            
            // Animate to final value
            animateValue(value, 0, finalValue, 1500, isPercentage, hasCurrency);
        }
    });
}

/**
 * Animate a value from start to end over a duration
 */
function animateValue(element, start, end, duration, isPercentage = false, hasCurrency = false) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentValue = Math.floor(progress * (end - start) + start);
        
        // Format the value
        let formattedValue = currentValue.toString();
        
        if (hasCurrency) {
            formattedValue = '$' + currentValue.toLocaleString();
        } else if (isPercentage) {
            formattedValue = currentValue + '%';
        } else {
            formattedValue = currentValue.toLocaleString();
        }
        
        element.textContent = formattedValue;
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    
    window.requestAnimationFrame(step);
}

/**
 * Initialize charts if any
 */
function initializeCharts() {
    const chartContainers = document.querySelectorAll('.chart-container');
    
    if (chartContainers.length === 0) return;
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Charts will not be initialized.');
        return;
    }
    
    chartContainers.forEach(container => {
        const canvas = container.querySelector('canvas');
        const chartType = container.dataset.chartType || 'bar';
        const reportType = container.dataset.reportType;
        
        if (canvas && reportType) {
            // Create chart based on report type
            createChart(canvas, chartType.toLowerCase(), reportType);
        }
    });
}

/**
 * Create a chart
 */
function createChart(canvas, chartType, reportType) {
    // Get the 2D context of the canvas
    const ctx = canvas.getContext('2d');
    
    // Default options for all charts
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    padding: 20,
                    font: {
                        size: 12
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                padding: 10,
                titleFont: {
                    size: 14
                },
                bodyFont: {
                    size: 13
                },
                displayColors: false
            }
        }
    };
    
    // Sample data - in a real application, this would come from an API
    const sampleData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: getChartLabel(reportType),
            data: [12, 19, 3, 5, 2, 3],
            backgroundColor: getChartColor(reportType, 0.2),
            borderColor: getChartColor(reportType, 1),
            borderWidth: 2
        }]
    };
    
    // Create the chart
    new Chart(ctx, {
        type: chartType,
        data: sampleData,
        options: defaultOptions
    });
}

/**
 * Get chart label based on report type
 */
function getChartLabel(reportType) {
    switch (reportType.toLowerCase()) {
        case 'banking':
            return 'Banking Transactions';
        case 'sales':
            return 'Sales Revenue';
        case 'clients':
            return 'Client Acquisition';
        case 'expenses':
            return 'Expense Breakdown';
        default:
            return 'Report Data';
    }
}

/**
 * Get chart color based on report type
 */
function getChartColor(reportType, alpha = 1) {
    switch (reportType.toLowerCase()) {
        case 'banking':
            return `rgba(59, 130, 246, ${alpha})`;
        case 'sales':
            return `rgba(16, 185, 129, ${alpha})`;
        case 'clients':
            return `rgba(217, 119, 6, ${alpha})`;
        case 'expenses':
            return `rgba(239, 68, 68, ${alpha})`;
        default:
            return `rgba(107, 114, 128, ${alpha})`;
    }
}

/**
 * Set up favorite toggles
 */
function setupFavoriteToggles() {
    const favoriteButtons = document.querySelectorAll('.favorite-toggle');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const reportId = this.dataset.reportId;
            const isFavorite = this.classList.contains('active');
            
            // Send AJAX request to toggle favorite status
            fetch(`/reports/toggle-favorite/${reportId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle button appearance
                    this.classList.toggle('active');
                    
                    // Update icon
                    const icon = this.querySelector('i');
                    if (icon) {
                        icon.className = isFavorite ? 'far fa-star' : 'fas fa-star';
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