<<<<<<< HEAD
// Create a namespace for charts
const DashboardCharts = {
    init() {
        this.initQuotesVsInvoicesChart();
        // Add other chart initializations here
    },

    initQuotesVsInvoicesChart() {
        try {
            const canvas = document.getElementById('quotesVsInvoicesChart');
            const overlay = document.getElementById('quotesVsInvoicesChartOverlay');
            if (!canvas) {
                console.error('Chart canvas element not found');
                return;
            }

            // Parse data from canvas attributes
            const quotes = parseInt(canvas.dataset.quotes) || 0;
            const invoices = parseInt(canvas.dataset.invoices) || 0;
            const quotesAmount = parseFloat(canvas.dataset.quotesAmount) || 0;
            const invoicesAmount = parseFloat(canvas.dataset.invoicesAmount) || 0;

            // Check if data is valid
            if (quotes === 0 && invoices === 0 && quotesAmount === 0 && invoicesAmount === 0) {
                console.warn('No data available for Quotes vs Invoices chart');
                overlay.style.display = 'flex'; // Show diagnostic overlay
                return;
            } else {
                overlay.style.display = 'none'; // Hide diagnostic overlay
            }

            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Quotes', 'Invoices'],
                    datasets: [
                        {
                            label: 'Count',
                            data: [quotes, invoices],
                            backgroundColor: ['#4f46e5', '#16a34a'],
                            order: 1
                        },
                        {
                            label: 'Amount (KES)',
                            data: [quotesAmount, invoicesAmount],
                            backgroundColor: ['#60a5fa', '#34d399'],
                            order: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (context.dataset.label === 'Amount (KES)') {
                                        return `KES ${context.raw.toLocaleString()}`;
                                    }
                                    return context.raw.toLocaleString();
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (this.chart.currentDatasetIndex === 1) {
                                        return 'KES ' + value.toLocaleString();
                                    }
                                    return value;
                                }
                            }
                        }
                    }
                }
            });

            // Handle metric changes
            const metricSelector = document.getElementById('quotesVsInvoicesMetric');
            if (metricSelector) {
                metricSelector.addEventListener('change', function(e) {
                    const metric = e.target.value;
                    chart.data.datasets.forEach((dataset, index) => {
                        if (metric === 'count') {
                            dataset.hidden = index === 1;
                        } else if (metric === 'amount') {
                            dataset.hidden = index === 0;
                        } else {
                            dataset.hidden = false;
                        }
                    });
                    chart.update();
                });

                // Set initial state
                metricSelector.dispatchEvent(new Event('change'));
            }
        } catch (error) {
            console.error('Error initializing Quotes vs Invoices chart:', error);
        }
    }
};

// Wait for dashboard.js to load first
window.addEventListener('load', function() {
    // Check if dashboard has initialized
    if (typeof Dashboard !== 'undefined') {
        // Initialize after dashboard
        setTimeout(() => DashboardCharts.init(), 0);
    } else {
        // Initialize independently
        DashboardCharts.init();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    try {
        const canvas = document.getElementById('quotesVsInvoicesChart');
        if (!canvas) {
            console.error('Chart canvas element not found');
            return;
        }

        console.log('Initializing Quotes vs Invoices chart...');
        console.log('Canvas data:', {
            quotes: canvas.dataset.quotes,
            invoices: canvas.dataset.invoices,
            quotesAmount: canvas.dataset.quotesAmount,
            invoicesAmount: canvas.dataset.invoicesAmount
        });

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Could not get canvas context');
            return;
        }

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Quotes', 'Invoices'],
                datasets: [{
                    data: [
                        parseInt(canvas.dataset.quotes) || 0,
                        parseInt(canvas.dataset.invoices) || 0
                    ],
                    backgroundColor: ['#4f46e5', '#16a34a'],
                    label: 'Count'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Handle metric changes
        const metricSelector = document.getElementById('quotesVsInvoicesMetric');
        if (metricSelector) {
            metricSelector.addEventListener('change', function(e) {
                const metric = e.target.value;
                let data, label;

                switch(metric) {
                    case 'amount':
                        data = [
                            parseFloat(canvas.dataset.quotesAmount) || 0,
                            parseFloat(canvas.dataset.invoicesAmount) || 0
                        ];
                        label = 'Amount (KES)';
                        break;
                    case 'average':
                        const quotesCount = parseInt(canvas.dataset.quotes) || 1;
                        const invoicesCount = parseInt(canvas.dataset.invoices) || 1;
                        const quotesAmount = parseFloat(canvas.dataset.quotesAmount) || 0;
                        const invoicesAmount = parseFloat(canvas.dataset.invoicesAmount) || 0;
                        
                        data = [
                            quotesAmount / quotesCount,
                            invoicesAmount / invoicesCount
                        ];
                        label = 'Average Value (KES)';
                        break;
                    default: // count
                        data = [
                            parseInt(canvas.dataset.quotes) || 0,
                            parseInt(canvas.dataset.invoices) || 0
                        ];
                        label = 'Count';
                }

                chart.data.datasets[0].data = data;
                chart.data.datasets[0].label = label;
                chart.update();
            });

            // Set initial state
            metricSelector.dispatchEvent(new Event('change'));
        }
    } catch (error) {
        console.error('Error initializing chart:', error);
    }
});
=======
// Create a namespace for charts
const DashboardCharts = {
    init() {
        this.initQuotesVsInvoicesChart();
        // Add other chart initializations here
    },

    initQuotesVsInvoicesChart() {
        try {
            const canvas = document.getElementById('quotesVsInvoicesChart');
            const overlay = document.getElementById('quotesVsInvoicesChartOverlay');
            if (!canvas) {
                console.error('Chart canvas element not found');
                return;
            }

            // Parse data from canvas attributes
            const quotes = parseInt(canvas.dataset.quotes) || 0;
            const invoices = parseInt(canvas.dataset.invoices) || 0;
            const quotesAmount = parseFloat(canvas.dataset.quotesAmount) || 0;
            const invoicesAmount = parseFloat(canvas.dataset.invoicesAmount) || 0;

            // Check if data is valid
            if (quotes === 0 && invoices === 0 && quotesAmount === 0 && invoicesAmount === 0) {
                console.warn('No data available for Quotes vs Invoices chart');
                overlay.style.display = 'flex'; // Show diagnostic overlay
                return;
            } else {
                overlay.style.display = 'none'; // Hide diagnostic overlay
            }

            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Quotes', 'Invoices'],
                    datasets: [
                        {
                            label: 'Count',
                            data: [quotes, invoices],
                            backgroundColor: ['#4f46e5', '#16a34a'],
                            order: 1
                        },
                        {
                            label: 'Amount (KES)',
                            data: [quotesAmount, invoicesAmount],
                            backgroundColor: ['#60a5fa', '#34d399'],
                            order: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (context.dataset.label === 'Amount (KES)') {
                                        return `KES ${context.raw.toLocaleString()}`;
                                    }
                                    return context.raw.toLocaleString();
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    if (this.chart.currentDatasetIndex === 1) {
                                        return 'KES ' + value.toLocaleString();
                                    }
                                    return value;
                                }
                            }
                        }
                    }
                }
            });

            // Handle metric changes
            const metricSelector = document.getElementById('quotesVsInvoicesMetric');
            if (metricSelector) {
                metricSelector.addEventListener('change', function(e) {
                    const metric = e.target.value;
                    chart.data.datasets.forEach((dataset, index) => {
                        if (metric === 'count') {
                            dataset.hidden = index === 1;
                        } else if (metric === 'amount') {
                            dataset.hidden = index === 0;
                        } else {
                            dataset.hidden = false;
                        }
                    });
                    chart.update();
                });

                // Set initial state
                metricSelector.dispatchEvent(new Event('change'));
            }
        } catch (error) {
            console.error('Error initializing Quotes vs Invoices chart:', error);
        }
    }
};

// Wait for dashboard.js to load first
window.addEventListener('load', function() {
    // Check if dashboard has initialized
    if (typeof Dashboard !== 'undefined') {
        // Initialize after dashboard
        setTimeout(() => DashboardCharts.init(), 0);
    } else {
        // Initialize independently
        DashboardCharts.init();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    try {
        const canvas = document.getElementById('quotesVsInvoicesChart');
        if (!canvas) {
            console.error('Chart canvas element not found');
            return;
        }

        console.log('Initializing Quotes vs Invoices chart...');
        console.log('Canvas data:', {
            quotes: canvas.dataset.quotes,
            invoices: canvas.dataset.invoices,
            quotesAmount: canvas.dataset.quotesAmount,
            invoicesAmount: canvas.dataset.invoicesAmount
        });

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Could not get canvas context');
            return;
        }

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Quotes', 'Invoices'],
                datasets: [{
                    data: [
                        parseInt(canvas.dataset.quotes) || 0,
                        parseInt(canvas.dataset.invoices) || 0
                    ],
                    backgroundColor: ['#4f46e5', '#16a34a'],
                    label: 'Count'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Handle metric changes
        const metricSelector = document.getElementById('quotesVsInvoicesMetric');
        if (metricSelector) {
            metricSelector.addEventListener('change', function(e) {
                const metric = e.target.value;
                let data, label;

                switch(metric) {
                    case 'amount':
                        data = [
                            parseFloat(canvas.dataset.quotesAmount) || 0,
                            parseFloat(canvas.dataset.invoicesAmount) || 0
                        ];
                        label = 'Amount (KES)';
                        break;
                    case 'average':
                        const quotesCount = parseInt(canvas.dataset.quotes) || 1;
                        const invoicesCount = parseInt(canvas.dataset.invoices) || 1;
                        const quotesAmount = parseFloat(canvas.dataset.quotesAmount) || 0;
                        const invoicesAmount = parseFloat(canvas.dataset.invoicesAmount) || 0;
                        
                        data = [
                            quotesAmount / quotesCount,
                            invoicesAmount / invoicesCount
                        ];
                        label = 'Average Value (KES)';
                        break;
                    default: // count
                        data = [
                            parseInt(canvas.dataset.quotes) || 0,
                            parseInt(canvas.dataset.invoices) || 0
                        ];
                        label = 'Count';
                }

                chart.data.datasets[0].data = data;
                chart.data.datasets[0].label = label;
                chart.update();
            });

            // Set initial state
            metricSelector.dispatchEvent(new Event('change'));
        }
    } catch (error) {
        console.error('Error initializing chart:', error);
    }
});
>>>>>>> d781b6071826b1e9eeb8bf33453b359a2cce4225
