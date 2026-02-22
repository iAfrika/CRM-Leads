/**
 * Reports Module JavaScript
 * Handles chart rendering and report functionality
 */

// Chart color palette
const chartColors = {
    primary: '#4e73df',
    success: '#1cc88a',
    info: '#36b9cc',
    warning: '#f6c23e',
    danger: '#e74a3b',
    secondary: '#858796',
    light: '#f8f9fc',
    dark: '#5a5c69',
    gray: '#6e707e',
    primaryLight: '#bac8f3',
    successLight: '#a3e9d2',
    infoLight: '#b3e3e8',
    warningLight: '#fbdea2',
    dangerLight: '#f5b8b1'
};

// Dashboard charts
function initDashboardCharts() {
    // Sales Performance Chart
    const salesCtx = document.getElementById('salesPerformanceChart');
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 19000, 3000, 5000, 2000, 3000, 20000, 25000, 23000, 25000, 28000, 30000],
                    backgroundColor: 'rgba(78, 115, 223, 0.05)',
                    borderColor: chartColors.primary,
                    pointBackgroundColor: chartColors.primary,
                    pointBorderColor: chartColors.primary,
                    pointHoverBackgroundColor: chartColors.primary,
                    pointHoverBorderColor: chartColors.primary,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#fff',
                        titleColor: '#5a5c69',
                        bodyColor: '#858796',
                        borderColor: '#dddfeb',
                        borderWidth: 1,
                        xPadding: 15,
                        yPadding: 15,
                        displayColors: false,
                        caretPadding: 10,
                        callbacks: {
                            label: function(context) {
                                return 'Revenue: $' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(0, 0, 0, 0.05)"
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Lead Sources Chart
    const leadSourcesCtx = document.getElementById('leadSourcesChart');
    if (leadSourcesCtx) {
        new Chart(leadSourcesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Website', 'Referral', 'Social Media', 'Email', 'Event', 'Other'],
                datasets: [{
                    data: [35, 25, 15, 10, 10, 5],
                    backgroundColor: [
                        chartColors.primary,
                        chartColors.success,
                        chartColors.info,
                        chartColors.warning,
                        chartColors.danger,
                        chartColors.secondary
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 10
                        }
                    },
                    tooltip: {
                        backgroundColor: '#fff',
                        titleColor: '#5a5c69',
                        bodyColor: '#858796',
                        borderColor: '#dddfeb',
                        borderWidth: 1,
                        xPadding: 15,
                        yPadding: 15,
                        displayColors: false,
                        caretPadding: 10,
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
}

// Project Reports Charts
function initProjectReportsCharts() {
    // Project Status Chart
    const projectStatusCtx = document.getElementById('projectStatusChart');
    if (projectStatusCtx) {
        const projectStatus = projectStatusCtx.dataset.projectStatus ? JSON.parse(projectStatusCtx.dataset.projectStatus) : null;
        
        if (projectStatus) {
            new Chart(projectStatusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Active', 'Completed', 'On Hold', 'Cancelled'],
                    datasets: [{
                        data: [
                            projectStatus.active || 0,
                            projectStatus.completed || 0,
                            projectStatus.on_hold || 0,
                            projectStatus.cancelled || 0
                        ],
                        backgroundColor: [
                            chartColors.primary,
                            chartColors.success,
                            chartColors.warning,
                            chartColors.danger
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12,
                                padding: 10
                            }
                        },
                        tooltip: {
                            backgroundColor: '#fff',
                            titleColor: '#5a5c69',
                            bodyColor: '#858796',
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 15,
                            yPadding: 15,
                            displayColors: false,
                            caretPadding: 10
                        }
                    }
                }
            });
        }
    }

    // Projects by Type Chart
    const projectTypeCtx = document.getElementById('projectTypeChart');
    if (projectTypeCtx) {
        const projectTypes = projectTypeCtx.dataset.projectTypes ? JSON.parse(projectTypeCtx.dataset.projectTypes) : null;
        
        if (projectTypes) {
            new Chart(projectTypeCtx, {
                type: 'bar',
                data: {
                    labels: projectTypes.labels || [],
                    datasets: [{
                        label: 'Projects',
                        data: projectTypes.data || [],
                        backgroundColor: chartColors.primary,
                        borderWidth: 0,
                        barThickness: 25,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#fff',
                            titleColor: '#5a5c69',
                            bodyColor: '#858796',
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 15,
                            yPadding: 15,
                            displayColors: false,
                            caretPadding: 10
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: "rgba(0, 0, 0, 0.05)"
                            },
                            ticks: {
                                precision: 0
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    }
}

// Report List Functionality
function initReportList() {
    // Filter reports by type
    const reportTypeFilter = document.getElementById('reportTypeFilter');
    const reportItems = document.querySelectorAll('.report-item');
    
    if (reportTypeFilter && reportItems.length > 0) {
        reportTypeFilter.addEventListener('change', function() {
            const selectedType = this.value;
            
            reportItems.forEach(item => {
                const itemType = item.dataset.reportType;
                
                if (selectedType === 'all' || selectedType === itemType) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Handle report favorite toggle
    const favoriteButtons = document.querySelectorAll('.toggle-favorite');
    
    if (favoriteButtons.length > 0) {
        favoriteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const reportId = this.dataset.reportId;
                const isFavorite = this.classList.contains('active');
                const icon = this.querySelector('i');
                
                // Toggle UI immediately for responsive feel
                this.classList.toggle('active');
                if (isFavorite) {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                } else {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                }
                
                // Send AJAX request to toggle favorite status
                fetch(`/reports/toggle-favorite/${reportId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        // Revert UI if request failed
                        this.classList.toggle('active');
                        if (isFavorite) {
                            icon.classList.remove('far');
                            icon.classList.add('fas');
                        } else {
                            icon.classList.remove('fas');
                            icon.classList.add('far');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Revert UI on error
                    this.classList.toggle('active');
                    if (isFavorite) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                });
            });
        });
    }
}

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initDashboardCharts();
    initProjectReportsCharts();
    initReportList();
}); 