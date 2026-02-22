// reports/static/reports/js/reports.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all chart containers
    initializeCharts();
    
    // Handle time range changes
    const timeRangeSelects = document.querySelectorAll('#time_range, #modal_time_range');
    timeRangeSelects.forEach(select => {
        select.addEventListener('change', function() {
            const customDateContainer = this.id === 'time_range' 
                ? document.getElementById('custom-date-container')
                : document.getElementById('modal-custom-date-container');
                
            if (customDateContainer) {
                customDateContainer.style.display = this.value === 'CUSTOM' ? 'flex' : 'none';
            }
        });
        
        // Trigger change event to set initial state
        select.dispatchEvent(new Event('change'));
    });
    
    // Initialize date pickers
    const datePickers = document.querySelectorAll('.date-picker');
    if (datePickers.length && typeof $.fn.datepicker !== 'undefined') {
        $(datePickers).datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }
    
    // Handle favorite toggles
    const favoriteToggles = document.querySelectorAll('.favorite-toggle');
    favoriteToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const configId = this.dataset.configId;
            toggleFavorite(configId, this);
        });
    });
});

/**
 * Initialize all chart containers on the page
 */
function initializeCharts() {
    const chartContainers = document.querySelectorAll('.chart-container');
    
    chartContainers.forEach(container => {
        const canvas = container.querySelector('canvas');
        if (!canvas) return;
        
        const chartType = container.dataset.chartType || 'bar';
        const reportType = container.dataset.reportType || '';
        
        // Get chart data from the server
        fetchChartData(container.id, reportType, chartType.toLowerCase())
            .then(data => {
                if (data) {
                    createChart(canvas, data, chartType.toLowerCase());
                }
            });
    });
}

/**
 * Fetch chart data from the server
 * @param {string} chartId - The ID of the chart container
 * @param {string} reportType - The type of report (BANKING, SALES, etc.)
 * @param {string} chartType - The type of chart (bar, line, pie, etc.)
 * @returns {Promise} - A promise that resolves with the chart data
 */
function fetchChartData(chartId, reportType, chartType) {
    // Get query parameters from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const configId = urlParams.get('config_id');
    
    // Build the API URL
    let apiUrl = `/reports/api/chart-data/?chart_id=${chartId}&report_type=${reportType}&chart_type=${chartType}`;
    
    if (configId) {
        apiUrl += `&config_id=${configId}`;
    }
    
    // Add any filter parameters
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const formData = new FormData(filterForm);
        for (const [key, value] of formData.entries()) {
            if (value) {
                apiUrl += `&${key}=${encodeURIComponent(value)}`;
            }
        }
    }
    
    // Fetch the data
    return fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            return data;
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            return null;
        });
}

/**
 * Create a chart using Chart.js
 * @param {HTMLCanvasElement} canvas - The canvas element to draw the chart on
 * @param {Object} data - The chart data
 * @param {string} chartType - The type of chart (bar, line, pie, etc.)
 */
function createChart(canvas, data, chartType) {
    // Default options for all charts
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        }
    };
    
    // Specific options based on chart type
    let chartOptions = { ...defaultOptions };
    
    if (chartType === 'bar') {
        chartOptions = {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };
    } else if (chartType === 'line' || chartType === 'area') {
        chartOptions = {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };
        
        // For area charts, set the fill option
        if (chartType === 'area') {
            if (data.datasets) {
                data.datasets.forEach(dataset => {
                    dataset.fill = true;
                });
            }
            chartType = 'line'; // Area charts are line charts with fill
        }
    }
    
    // Create the chart
    new Chart(canvas, {
        type: chartType,
        data: data,
        options: chartOptions
    });
}

/**
 * Toggle a report as favorite
 * @param {number} configId - The ID of the report configuration
 * @param {HTMLElement} element - The favorite toggle element
 */
function toggleFavorite(configId, element) {
    fetch(`/reports/api/toggle-favorite/${configId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            element.classList.toggle('active');
            
            // Update icon
            const icon = element.querySelector('i') || element;
            if (data.is_favorite) {
                icon.classList.remove('far');
                icon.classList.add('fas');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        }
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
    });
}

/**
 * Save a report configuration
 * @param {number|null} configId - The ID of the existing report configuration, or null for a new one
 */
function saveReport(configId) {
    // Get the current filter values
    const filterForm = document.getElementById('filter-form');
    if (!filterForm) return;
    
    const formData = new FormData(filterForm);
    const reportData = {};
    
    for (const [key, value] of formData.entries()) {
        reportData[key] = value;
    }
    
    // Add the report type from the current page
    const reportTypeElement = document.querySelector('.chart-container');
    if (reportTypeElement) {
        reportData.report_type = reportTypeElement.dataset.reportType;
    }
    
    // Show the save report modal
    const modal = document.getElementById('save-report-modal');
    if (modal) {
        // Set the form action based on whether we're updating or creating
        const form = modal.querySelector('form');
        if (form) {
            form.action = configId 
                ? `/reports/update-report-config/${configId}/`
                : `/reports/create-report-config/`;
                
            // Set the hidden report data field
            const reportDataField = form.querySelector('#report_data');
            if (reportDataField) {
                reportDataField.value = JSON.stringify(reportData);
            }
            
            // If updating, pre-fill the form fields
            if (configId) {
                fetch(`/reports/api/report-config/${configId}/`)
                    .then(response => response.json())
                    .then(data => {
                        form.querySelector('#name').value = data.name || '';
                        form.querySelector('#description').value = data.description || '';
                    });
            }
        }
        
        // Show the modal
        $(modal).modal('show');
    }
}

/**
 * Export a chart as an image
 * @param {string} chartId - The ID of the chart container
 */
function exportChartAsImage(chartId) {
    const container = document.getElementById(chartId);
    if (!container) return;
    
    const canvas = container.querySelector('canvas');
    if (!canvas) return;
    
    // Create a link element
    const link = document.createElement('a');
    link.download = `${chartId}-${new Date().toISOString().split('T')[0]}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
}

/**
 * Export chart data as CSV
 * @param {string} chartId - The ID of the chart container
 */
function exportDataAsCSV(chartId) {
    const container = document.getElementById(chartId);
    if (!container) return;
    
    const reportType = container.dataset.reportType;
    const chartType = container.dataset.chartType;
    
    // Get query parameters from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const configId = urlParams.get('config_id');
    
    // Build the API URL
    let apiUrl = `/reports/api/export-csv/?chart_id=${chartId}&report_type=${reportType}&chart_type=${chartType}`;
    
    if (configId) {
        apiUrl += `&config_id=${configId}`;
    }
    
    // Add any filter parameters
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const formData = new FormData(filterForm);
        for (const [key, value] of formData.entries()) {
            if (value) {
                apiUrl += `&${key}=${encodeURIComponent(value)}`;
            }
        }
    }
    
    // Create a link and trigger the download
    const link = document.createElement('a');
    link.href = apiUrl;
    link.download = `${chartId}-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
}

/**
 * Get the CSRF token from cookies
 * @returns {string} - The CSRF token
 */
function getCsrfToken() {
    const name = 'csrftoken';
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