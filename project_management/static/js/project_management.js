// Project Management JavaScript
(function() {
    console.error('PROJECT MANAGEMENT SCRIPT LOADED IMMEDIATELY');
    
    // Ensure jQuery and other dependencies are loaded
    function waitForDependencies(callback) {
        const checkInterval = setInterval(function() {
            if (window.jQuery && document.readyState === 'complete') {
                clearInterval(checkInterval);
                callback();
            }
        }, 100);
    }

    waitForDependencies(function() {
        console.error('ALL DEPENDENCIES LOADED');
        
        document.addEventListener('DOMContentLoaded', function() {
            console.error('DOM CONTENT LOADED');
            
            // Project Delete Functionality
            const deleteButtons = document.querySelectorAll('.delete-project');
            const deleteModal = document.getElementById('delete-project-modal');
            const deleteProjectNameSpan = document.getElementById('delete-project-name');
            const deleteProjectIdInput = document.getElementById('delete-project-id');
            const deleteProjectForm = document.getElementById('delete-project-form');
            const deleteConfirmationBtn = deleteProjectForm ? deleteProjectForm.querySelector('button[type="submit"]') : null;

            // Extensive Logging
            console.log('Delete Buttons Found:', deleteButtons.length);
            console.log('Delete Modal:', deleteModal ? 'Found' : 'Not Found');
            console.log('Delete Project Form:', deleteProjectForm ? 'Found' : 'Not Found');
            console.log('Delete Confirmation Button:', deleteConfirmationBtn ? 'Found' : 'Not Found');

            // Attach event listeners to delete buttons
            deleteButtons.forEach(button => {
                button.addEventListener('click', function(event) {
                    console.log('Delete Button Clicked', {
                        projectId: this.dataset.projectId,
                        projectName: this.dataset.projectName,
                        deleteUrl: this.dataset.deleteUrl
                    });

                    // Ensure modal elements exist before manipulating
                    if (deleteProjectNameSpan) {
                        deleteProjectNameSpan.textContent = this.dataset.projectName || 'Project';
                    }
                    if (deleteProjectIdInput) {
                        deleteProjectIdInput.value = this.dataset.projectId;
                    }
                    if (deleteProjectForm) {
                        deleteProjectForm.action = this.dataset.deleteUrl;
                    }
                });
            });

            // Handle form submission
            if (deleteProjectForm) {
                deleteProjectForm.addEventListener('submit', function(event) {
                    event.preventDefault();
                    console.log('Delete Form Submitted', {
                        action: this.action,
                        method: this.method
                    });

                    // Validate form action
                    if (!this.action) {
                        console.error('Delete URL is not set');
                        showNotification('error', 'Delete URL is not configured. Please try again.');
                        return;
                    }

                    // Disable submit button and show loading state
                    if (deleteConfirmationBtn) {
                        deleteConfirmationBtn.disabled = true;
                        deleteConfirmationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
                    }

                    // Perform AJAX submission
                    fetch(this.action, {
                        method: 'POST',
                        body: new FormData(this),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    })
                    .then(response => {
                        console.log('Response Status:', response.status);
                        
                        // Check for non-200 status codes
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        
                        return response.json();
                    })
                    .then(data => {
                        console.log('Delete Response:', data);

                        if (data.status === 'success') {
                            // Remove project card from DOM
                            const projectCard = document.querySelector(`.project-card[data-project-id="${data.id}"]`);
                            if (projectCard) {
                                projectCard.remove();

                                // Update project count
                                const projectCount = document.querySelector('.project-count');
                                if (projectCount) {
                                    const currentCount = parseInt(projectCount.textContent);
                                    projectCount.textContent = `${currentCount - 1} total projects`;
                                }

                                // Check if there are no more projects
                                const projectsGrid = document.querySelector('.projects-grid');
                                if (projectsGrid && !projectsGrid.children.length) {
                                    location.reload(); // Reload to show empty state
                                }
                            }

                            // Close modal
                            $('#delete-project-modal').modal('hide');

                            // Show success notification
                            showNotification('success', data.message || 'Project deleted successfully');
                        } else {
                            // Show error notification
                            showNotification('error', data.message || 'Failed to delete project');
                        }
                    })
                    .catch(error => {
                        console.error('Delete Error:', error);
                        showNotification('error', error.message || 'An unexpected error occurred while deleting the project.');
                    })
                    .finally(() => {
                        // Restore button state
                        if (deleteConfirmationBtn) {
                            deleteConfirmationBtn.disabled = false;
                            deleteConfirmationBtn.innerHTML = 'Delete Project';
                        }
                    });
                });
            } else {
                console.error('Delete project form not found');
            }

            // Notification function
            function showNotification(type, message) {
                const container = document.getElementById('notification-container');
                if (!container) {
                    console.error('Notification container not found');
                    alert(message);  // Fallback notification
                    return;
                }
                
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                
                const iconClass = type === 'success' ? 'fa-check-circle' :
                                  type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
                
                notification.innerHTML = `
                    <div class="notification-icon">
                        <i class="fas ${iconClass}"></i>
                    </div>
                    <div class="notification-content">
                        <h4 class="notification-title">${type.charAt(0).toUpperCase() + type.slice(1)}</h4>
                        <p class="notification-message">${message}</p>
                    </div>
                    <button class="notification-close">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                
                container.appendChild(notification);
                
                // Add active class to animate in
                setTimeout(() => {
                    notification.classList.add('active');
                }, 10);
                
                // Auto close after 3 seconds
                setTimeout(() => {
                    notification.classList.remove('active');
                    setTimeout(() => {
                        container.removeChild(notification);
                    }, 300);
                }, 3000);
                
                // Close button functionality
                notification.querySelector('.notification-close').addEventListener('click', function() {
                    notification.classList.remove('active');
                    setTimeout(() => {
                        container.removeChild(notification);
                    }, 300);
                });
            }

            // CSRF Cookie Helper
            function getCookie(name) {
                console.error('Getting Cookie:', name);
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
                console.error('Cookie Value:', cookieValue);
                return cookieValue;
            }

            // Initialize select2 for multi-select fields if Select2 is available
            if (typeof $.fn.select2 !== 'undefined') {
                console.error('Initializing Select2');
                $('.select2').select2({
                    theme: 'bootstrap4',
                    width: '100%'
                });
            }
            
            // Initialize datepickers if Flatpickr is available
            if (typeof flatpickr !== 'undefined') {
                console.error('Initializing Flatpickr');
                flatpickr('.datepicker', {
                    dateFormat: 'Y-m-d',
                    allowInput: true
                });
            }
            
            // Budget calculation in project form
            const budgetInput = document.getElementById('id_budget');
            const actualCostInput = document.getElementById('id_actual_cost');
            const budgetUtilizationElement = document.getElementById('budget-utilization');
            
            if (budgetInput && actualCostInput && budgetUtilizationElement) {
                console.error('Initializing Budget Calculation');
                const calculateBudgetUtilization = function() {
                    console.error('Calculating Budget Utilization');
                    const budget = parseFloat(budgetInput.value) || 0;
                    const actualCost = parseFloat(actualCostInput.value) || 0;
                    
                    if (budget > 0) {
                        const utilization = (actualCost / budget) * 100;
                        budgetUtilizationElement.textContent = utilization.toFixed(1) + '%';
                        
                        // Update progress bar if exists
                        const progressBar = document.getElementById('budget-progress');
                        if (progressBar) {
                            progressBar.style.width = Math.min(utilization, 100) + '%';
                            if (utilization > 100) {
                                progressBar.classList.add('bg-danger');
                                progressBar.classList.remove('bg-success');
                            } else {
                                progressBar.classList.add('bg-success');
                                progressBar.classList.remove('bg-danger');
                            }
                        }
                    } else {
                        budgetUtilizationElement.textContent = 'N/A';
                    }
                };
                
                budgetInput.addEventListener('input', calculateBudgetUtilization);
                actualCostInput.addEventListener('input', calculateBudgetUtilization);
                
                // Initial calculation
                calculateBudgetUtilization();
            }
            
            // Completion percentage validation
            const completionInput = document.getElementById('id_completion_percentage');
            if (completionInput) {
                console.error('Initializing Completion Percentage Validation');
                completionInput.addEventListener('input', function() {
                    console.error('Validating Completion Percentage');
                    let value = parseInt(this.value) || 0;
                    if (value < 0) value = 0;
                    if (value > 100) value = 100;
                    this.value = value;
                });
            }
            
            // Document/Note/Milestone deletion confirmation
            document.querySelectorAll('.delete-confirmation').forEach(function(element) {
                console.error('Initializing Deletion Confirmation');
                element.addEventListener('click', function(event) {
                    console.error('Confirming Deletion');
                    if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                        event.preventDefault();
                    }
                });
            });
            
            // Project financial charts initialization if Chart.js is available
            if (typeof Chart !== 'undefined') {
                console.error('Initializing Financial Charts');
                // Revenue vs Expenses Chart
                const revenueExpensesCanvas = document.getElementById('revenue-expenses-chart');
                if (revenueExpensesCanvas) {
                    const ctx = revenueExpensesCanvas.getContext('2d');
                    
                    // Get data from data attributes or API
                    const revenue = parseFloat(revenueExpensesCanvas.dataset.revenue) || 0;
                    const expenses = parseFloat(revenueExpensesCanvas.dataset.expenses) || 0;
                    
                    new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: ['Revenue', 'Expenses'],
                            datasets: [{
                                label: 'Amount',
                                data: [revenue, expenses],
                                backgroundColor: [
                                    'rgba(0, 123, 255, 0.7)',
                                    'rgba(220, 53, 69, 0.7)'
                                ],
                                borderColor: [
                                    'rgba(0, 123, 255, 1)',
                                    'rgba(220, 53, 69, 1)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
                
                // Transaction History Chart
                const transactionHistoryCanvas = document.getElementById('transaction-history-chart');
                if (transactionHistoryCanvas) {
                    const ctx = transactionHistoryCanvas.getContext('2d');
                    
                    // In a real application, this data would come from your API
                    // This is just placeholder data
                    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                    const deposits = [1000, 1500, 800, 1200, 1800, 1300];
                    const withdrawals = [500, 800, 1200, 600, 400, 900];
                    
                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [
                                {
                                    label: 'Revenue',
                                    data: deposits,
                                    borderColor: 'rgba(40, 167, 69, 1)',
                                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                    tension: 0.4,
                                    fill: true
                                },
                                {
                                    label: 'Expenses',
                                    data: withdrawals,
                                    borderColor: 'rgba(220, 53, 69, 1)',
                                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                                    tension: 0.4,
                                    fill: true
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                }
            }
        });
    });
})();