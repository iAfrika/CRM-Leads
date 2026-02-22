// reports/static/reports/js/reports.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    const dateInputs = document.querySelectorAll('.date-picker');
    if (dateInputs.length > 0) {
        dateInputs.forEach(input => {
            // This assumes you're using a date picker library
            // You might need to adjust based on your actual implementation
            $(input).datepicker({
                format: 'yyyy-mm-dd',
                autoclose: true
            });
        });
    }

    // Initialize chart containers
    initializeCharts();

    // Set up event listeners for filter changes
    setupFilterListeners();

    // Set up favorite toggles
    setupFavoriteToggles();
});

// Function to initialize charts
function initializeCharts() {
    const chartContainers = document.querySelectorAll('.chart-container');
    
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

// Function to create a chart
function createChart(canvas, chartType, reportType) {
    // Get the 2D context of the canvas
    const ctx = canvas.getContext('2d');
    
    // Default options for all charts
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Loading data...'
            }
        }
    };
    
    // Create chart instance
    let chart;
    
    // Initialize with empty data
    const emptyData = {
        labels: [],
        datasets: [{
            label: 'Loading...',
            data: [],
            backgroundColor: 'rgba(200, 200, 200, 0.2)',
            borderColor: 'rgba(200, 200, 200, 1)',
            borderWidth: 1
        }]
    };
    
    // Create chart based on type
    if (chartType === 'pie' || chartType === 'doughnut') {
        chart = new Chart(ctx, {
            type: chartType,
            data: emptyData,
            options: {
                ...defaultOptions,
                cutout: chartType === 'doughnut' ? '50%' : 0
            }
        });
    } else if (chartType === 'line' || chartType === 'area') {
        // For area charts, we use line chart with fill
        chart = new Chart(ctx, {
            type: 'line',
            data: emptyData,
            options: {
                ...defaultOptions,
                elements: {
                    line: {
                        tension: 0.4
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // If it's an area chart, set fill to true
        if (chartType === 'area') {
            chart.data.datasets.forEach(dataset => {
                dataset.fill = true;
            });
            chart.update();
        }
    } else {
        // Default to bar chart
        chart = new Chart(ctx, {
            type: chartType,
            data: emptyData,
            options: {
                ...defaultOptions,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Store chart instance in the canvas element
    canvas.chart = chart;
    
    // Load data for the chart
    loadChartData(chart, reportType);
}

// Function to load chart data
function loadChartData(chart, reportType) {
    // Get filter values
    const filterForm = document.getElementById('filter-form');
    let filterData = {};
    
    if (filterForm) {
        const formData = new FormData(filterForm);
        formData.forEach((value, key) => {
            filterData[key] = value;
        });
    }
    
    // Determine API endpoint based on report type
    let endpoint = '';
    switch (reportType) {
        case 'BANKING':
            endpoint = '/reports/api/banking-chart-data/';
            break;
        case 'SALES':
            endpoint = '/reports/api/sales-chart-data/';
            break;
        case 'EXPENSES':
            endpoint = '/reports/api/expenses-chart-data/';
            break;
        case 'CLIENTS':
            endpoint = '/reports/api/clients-chart-data/';
            break;
        case 'PURCHASES':
            endpoint = '/reports/api/purchases-chart-data/';
            break;
        default:
            console.error('Unknown report type:', reportType);
            return;
    }
    
    // Add filter parameters to the URL
    const params = new URLSearchParams(filterData);
    endpoint += `?${params.toString()}`;
    
    // Fetch data from the API
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateChart(chart, data);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
            // Show error in chart
            chart.options.plugins.title.text = 'Error loading data';
            chart.update();
        });
}

// Function to update chart with new data
function updateChart(chart, data) {
    // Update chart title
    chart.options.plugins.title.text = data.title;
    
    // Clear existing datasets
    chart.data.labels = [];
    chart.data.datasets = [];
    
    // Update with new data
    chart.data.labels = data.data.labels;
    data.data.datasets.forEach(dataset => {
        chart.data.datasets.push(dataset);
    });
    
    // Update the chart
    chart.update();
}

// Function to set up filter listeners
function setupFilterListeners() {
    const filterForm = document.getElementById('filter-form');
    
    if (filterForm) {
        // Handle form submission
        filterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get all chart containers
            const chartContainers = document.querySelectorAll('.chart-container');
            
            // Reload data for each chart
            chartContainers.forEach(container => {
                const canvas = container.querySelector('canvas');
                const reportType = container.dataset.reportType;
                
                if (canvas && canvas.chart && reportType) {
                    loadChartData(canvas.chart, reportType);
                }
            });
        });
        
        // Handle time range change to show/hide custom date inputs
        const timeRangeSelect = document.getElementById('time_range');
        const customDateContainer = document.getElementById('custom-date-container');
        
        if (timeRangeSelect && customDateContainer) {
            timeRangeSelect.addEventListener('change', function() {
                if (this.value === 'CUSTOM') {
                    customDateContainer.style.display = 'block';
                } else {
                    customDateContainer.style.display = 'none';
                }
            });
            
            // Trigger change event to set initial state
            timeRangeSelect.dispatchEvent(new Event('change'));
        }
    }
}

// Function to set up favorite toggles
function setupFavoriteToggles() {
    const favoriteToggles = document.querySelectorAll('.favorite-toggle');
    
    favoriteToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const configId = this.dataset.configId;
            
            // Send AJAX request to toggle favorite status
            fetch(`/reports/toggle-favorite/${configId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Toggle active class
                    this.classList.toggle('active', data.is_favorite);
                }
            })
            .catch(error => {
                console.error('Error toggling favorite status:', error);
            });
        });
    });
}

// Function to get CSRF token
function getCsrfToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
}

// Function to save current report
function saveReport(configId) {
    // Get the chart data
    const chartContainers = document.querySelectorAll('.chart-container');
    let chartData = {};
    
    chartContainers.forEach(container => {
        const canvas = container.querySelector('canvas');
        if (canvas && canvas.chart) {
            const chartId = container.id;
            chartData[chartId] = {
                type: canvas.chart.config.type,
                data: canvas.chart.data,
                options: canvas.chart.options
            };
        }
    });
    
    // Show save report modal
    const modal = document.getElementById('save-report-modal');
    const reportDataInput = document.getElementById('report_data');
    
    if (modal && reportDataInput) {
        // Set report data in hidden input
        reportDataInput.value = JSON.stringify(chartData);
        
        // Set config ID in form action
        const form = modal.querySelector('form');
        if (form) {
            form.action = `/reports/save-report/${configId}/`;
        }
        
        // Show modal
        $(modal).modal('show');
    }
}

// Function to export chart as image
function exportChartAsImage(chartId) {
    const container = document.getElementById(chartId);
    if (!container) return;
    
    const canvas = container.querySelector('canvas');
    if (!canvas) return;
    
    // Create a temporary link
    const link = document.createElement('a');
    link.download = `chart-${Date.now()}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
}

// Function to export data as CSV
function exportDataAsCSV(chartId) {
    const container = document.getElementById(chartId);
    if (!container) return;
    
    const canvas = container.querySelector('canvas');
    if (!canvas || !canvas.chart) return;
    
    const chart = canvas.chart;
    const labels = chart.data.labels;
    const datasets = chart.data.datasets;
    
    // Create CSV content
    let csvContent = 'data:text/csv;charset=utf-8,';
    
    // Add header row
    let headerRow = ['Label'];
    datasets.forEach(dataset => {
        headerRow.push(dataset.label);
    });
    csvContent += headerRow.join(',') + '\r\n';
    
    // Add data rows
    labels.forEach((label, i) => {
        let row = [label];
        datasets.forEach(dataset => {
            row.push(dataset.data[i]);
        });
        csvContent += row.join(',') + '\r\n';
    });
    
    // Create a temporary link
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `chart-data-${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}