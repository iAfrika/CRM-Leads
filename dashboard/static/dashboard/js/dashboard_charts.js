document.addEventListener('DOMContentLoaded', function() {
    console.group('Dashboard Charts Initialization');
    console.log('DOM fully loaded and parsed');
    
    try {
        // Ensure Chart.js is loaded
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js is not loaded');
        }
        console.log('Chart.js version:', Chart.version);

        // Verify chart data exists
        if (!window.chartData) {
            throw new Error('No chart data found in window object');
        }
        console.log('Chart data object:', window.chartData);

        // Fallback data with minimal structure
        const fallbackData = {
            labels: ['No Data'],
            datasets: [{
                label: 'No Data Available',
                data: [0],
                backgroundColor: 'rgba(200,200,200,0.5)'
            }]
        };

        // Pie/Doughnut shared options with comprehensive styling and animations
        const pieOptions = {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                tooltip: {
                    callbacks: {
                        // Custom tooltip label to show individual segment labels
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value}`;
                        }
                    }
                },
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        // Custom legend labels with specific text for each segment
                        generateLabels: function(chart) {
                            const originalLabels = Chart.defaults.plugins.legend.labels.generateLabels(chart);
                            return [
                                {
                                    ...originalLabels[0],
                                    text: 'Quotes',
                                    fillStyle: 'rgba(54, 162, 235, 0.7)',
                                    pointStyle: 'circle',
                                    borderWidth: 0,
                                    borderColor: 'rgba(0,0,0,0)'
                                },
                                {
                                    ...originalLabels[1],
                                    text: 'Invoices',
                                    fillStyle: 'rgba(255, 99, 132, 0.7)',
                                    pointStyle: 'circle',
                                    borderWidth: 0,
                                    borderColor: 'rgba(0,0,0,0)'
                                }
                            ];
                        },
                        boxWidth: 20,
                        boxHeight: 10,
                        usePointStyle: true,
                        borderWidth: 0,
                        borderColor: 'rgba(0,0,0,0)'
                    }
                },
                title: {
                    display: false
                }
            },
            elements: {
                arc: {
                    borderWidth: 0,  // Remove border between segments
                    hoverOffset: 30  // Increased hover offset to move segments further
                }
            },
            layout: {
                padding: 10
            },
            hover: {
                mode: 'nearest',
                intersect: true,
                animationDuration: 200  // Very quick hover response
            },
            animation: {
                duration: 1000,  // Longer initial load animation
                delay: 100,  // Slight delay to make loading smoother
                easing: 'easeOutQuad',  // Smooth, natural easing
                animateRotate: true,  // Rotate segments on initial load
                animateScale: true  // Scale segments on initial load
            },
            // Smooth transitions for all chart interactions
            transitions: {
                show: {
                    animations: {
                        x: {
                            from: 0,
                            to: 1,
                            type: 'number',
                            duration: 800,
                            delay: 200,
                            easing: 'easeOutQuad'
                        },
                        y: {
                            from: 0,
                            to: 1,
                            type: 'number',
                            duration: 800,
                            delay: 200,
                            easing: 'easeOutQuad'
                        },
                        opacity: {
                            from: 0,
                            to: 1,
                            type: 'number',
                            duration: 800,
                            delay: 200,
                            easing: 'easeOutQuad'
                        }
                    }
                },
                hide: {
                    animations: {
                        x: {
                            from: 1,
                            to: 0,
                            type: 'number',
                            duration: 500,
                            easing: 'easeOutQuad'
                        },
                        y: {
                            from: 1,
                            to: 0,
                            type: 'number',
                            duration: 500,
                            easing: 'easeOutQuad'
                        },
                        opacity: {
                            from: 1,
                            to: 0,
                            type: 'number',
                            duration: 500,
                            easing: 'easeOutQuad'
                        }
                    }
                }
            },
            onHover: (event, chartElement) => {
                event.native.target.style.cursor = chartElement[0] 
                    ? 'pointer' 
                    : 'default';
            }
        };

        // Safely extract and parse chart data
        const quotesInvoicesData = {
            labels: ['Quotes', 'Invoices'],
            datasets: [{
                label: 'Quotes vs Invoices',
                data: [
                    window.chartData.quotes_count || 0, 
                    window.chartData.invoices_count || 0
                ],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',   // Blue for Quotes
                    'rgba(255, 99, 132, 0.7)'    // Red for Invoices
                ],
                hoverBackgroundColor: [
                    'rgba(54, 162, 235, 0.9)',
                    'rgba(255, 99, 132, 0.9)'
                ],
                borderWidth: 1,
                cutout: '70%'  // Increased hole size
            }]
        };

        // Safely find the toggle button and chart canvas
        const quotesInvoicesToggle = document.querySelector('#chartDataToggle');
        const quotesInvoicesChart = document.querySelector('#quotesInvoicesChart');
        
        // Validate essential DOM elements
        if (!quotesInvoicesToggle || !quotesInvoicesChart) {
            console.warn('Dashboard Charts: Critical elements missing', {
                toggleButton: !!quotesInvoicesToggle,
                chartCanvas: !!quotesInvoicesChart
            });
            console.groupEnd();
            return;
        }

        // Destroy existing chart if it exists
        if (window.quotesInvoicesChartInstance) {
            window.quotesInvoicesChartInstance.destroy();
        }

        // Recreate the chart
        window.quotesInvoicesChartInstance = new Chart(quotesInvoicesChart, {
            type: 'doughnut',
            data: quotesInvoicesData,
            options: pieOptions  // Use the comprehensive pie chart options
        });

        // Find labels using a more robust method
        const toggleContainer = quotesInvoicesToggle.closest('.chart-toggle-switch-small');
        const quotesInvoicesCountLabel = toggleContainer.querySelector('.chart-toggle-count');
        const quotesInvoicesValueLabel = toggleContainer.querySelector('.chart-toggle-value');

        // Function to update chart data
        function updateQuotesInvoicesChart(dataType) {
            try {
                let chartData, chartLabel;
                
                console.log(`Updating chart to ${dataType} view`);
                
                if (dataType === 'count') {
                    chartData = [
                        window.chartData.quotes_count || 0, 
                        window.chartData.invoices_count || 0
                    ];
                    chartLabel = 'Quotes vs Invoices (Count)';
                } else {
                    chartData = [
                        window.chartData.quotes_total_value || 0, 
                        window.chartData.invoices_total_value || 0
                    ];
                    chartLabel = 'Quotes vs Invoices (Total Value)';
                }

                // Update chart data and labels
                window.quotesInvoicesChartInstance.data.datasets[0].data = chartData;
                window.quotesInvoicesChartInstance.data.datasets[0].label = chartLabel;
                window.quotesInvoicesChartInstance.update();
            } catch (error) {
                console.error('Dashboard Charts: Error updating chart', error);
            }
        }

        // Toggle event listener for Quotes vs Invoices
        quotesInvoicesToggle.addEventListener('change', function() {
            const dataType = this.checked ? 'value' : 'count';
            
            // Update label styles
            quotesInvoicesCountLabel.classList.toggle('active', !this.checked);
            quotesInvoicesValueLabel.classList.toggle('active', this.checked);

            // Update chart data
            updateQuotesInvoicesChart(dataType);
        });

        console.log('Dashboard Charts: Initialization complete');
        console.groupEnd();
    } catch (error) {
        console.error('Critical error in chart initialization:', error);
    }

    // Global variable to track current monthly view
    let currentMonthlyViewIndex = 0;

    // Revenue vs Expenses Chart Configuration
    const revenueExpendituresChart = document.querySelector('#revenueExpendituresChart');
    const revenueExpendituresTimeframeLabels = document.querySelectorAll('.revenue-expenditures-timeframe-label');

    // Validate essential DOM elements
    if (!revenueExpendituresChart) {
        console.warn('Revenue vs Expenditures Chart: Chart canvas not found');
        return;
    }

    // Destroy existing chart if it exists
    if (window.revenueExpendituresChartInstance) {
        window.revenueExpendituresChartInstance.destroy();
    }

    async function fetchMonthlyRevenueExpenses() {
        try {
            const response = await fetch('/dashboard/monthly-revenue-expenses/');
            if (!response.ok) {
                throw new Error('Failed to fetch monthly revenue and expenses');
            }
            const data = await response.json();
            
            // Debug logging
            console.log('Revenue vs Expenses Data:', data);

            return {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: data.revenue,
                        backgroundColor: 'rgba(46, 204, 113, 0.6)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 1,
                        tension: 0.4,  // Add soft curve to the line
                        fill: false,
                        type: 'line'  // Change to line type
                    },
                    {
                        label: 'Expenses',
                        data: data.expenses,
                        backgroundColor: 'rgba(255, 0, 0, 0.6)',
                        borderColor: 'rgba(255, 0, 0, 1)',
                        borderWidth: 1,
                        tension: 0.4,  // Add soft curve to the line
                        fill: false,
                        type: 'line'  // Change to line type
                    }
                ]
            };
        } catch (error) {
            console.error('Error fetching monthly revenue and expenses:', error);
            return {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Revenue',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(46, 204, 113, 0.6)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 1,
                        tension: 0.4,  // Add soft curve to the line
                        fill: false,
                        type: 'line'  // Change to line type
                    },
                    {
                        label: 'Expenses',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(255, 0, 0, 0.6)',
                        borderColor: 'rgba(255, 0, 0, 1)',
                        borderWidth: 1,
                        tension: 0.4,  // Add soft curve to the line
                        fill: false,
                        type: 'line'  // Change to line type
                    }
                ]
            };
        }
    }

    function formatNumber(value) {
        // Convert to number in case it's a string
        const num = Number(value);
        
        // Handle special cases
        if (num === 0) return '0';
        if (isNaN(num)) return '';

        // Absolute value for formatting
        const absNum = Math.abs(num);

        // Formatting for different ranges
        if (absNum < 1000) {
            // Less than 1,000: show as is
            return num.toLocaleString('en-US', {maximumFractionDigits: 0});
        } else if (absNum < 10000) {
            // 1,000 to 9,999: show with one decimal place and K
            return (num / 1000).toLocaleString('en-US', {maximumFractionDigits: 1}) + 'K';
        } else if (absNum < 1000000) {
            // 10,000 to 999,999: show without decimal
            return Math.round(num / 1000).toLocaleString('en-US', {maximumFractionDigits: 0}) + 'K';
        } else {
            // 1,000,000 and above: show with one decimal place and M
            return (num / 1000000).toLocaleString('en-US', {maximumFractionDigits: 1}) + 'M';
        }
    }

    async function updateRevenueExpendituresChart() {
        try {
            // Fetch live data
            const chartData = await fetchMonthlyRevenueExpenses();
            
            // Chart configuration
            const chartConfig = {
                type: 'bar',
                data: {
                    labels: chartData.labels,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: chartData.datasets[0].data,
                            backgroundColor: 'rgba(46, 204, 113, 0.6)',
                            borderColor: 'rgba(46, 204, 113, 1)',
                            borderWidth: 1,
                            borderRadius: 5,
                            barThickness: 15
                        },
                        {
                            label: 'Expenses',
                            data: chartData.datasets[1].data,
                            backgroundColor: 'rgba(255, 0, 0, 0.6)',
                            borderColor: 'rgba(255, 0, 0, 1)',
                            borderWidth: 1,
                            borderRadius: 5,
                            barThickness: 15
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: {
                            top: 0,
                            bottom: 0,
                            left: 0,
                            right: 0
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                boxWidth: 10,
                                boxHeight: 10
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Months'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Amount (KES)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                }
                            }
                        }
                    }
                }
            };

            // Destroy existing chart if it exists
            if (window.revenueExpendituresChartInstance) {
                window.revenueExpendituresChartInstance.destroy();
            }

            // Create new chart
            const ctx = document.getElementById('revenueExpendituresChart').getContext('2d');
            window.revenueExpendituresChartInstance = new Chart(ctx, chartConfig);

        } catch (error) {
            console.error('Error updating Revenue vs Expenses chart:', error);
        }
    }

    // Initial chart load
    updateRevenueExpendituresChart();

    // Timeframe toggle event listeners
    if (revenueExpendituresTimeframeLabels) {
        revenueExpendituresTimeframeLabels.forEach(label => {
            label.addEventListener('click', function() {
                const timeframe = this.dataset.timeframe;
                
                // Update active label
                revenueExpendituresTimeframeLabels.forEach(l => 
                    l.classList.toggle('active', l === this)
                );

                // Update chart
                updateRevenueExpendituresChart();
            });
        });
    }

    async function fetchMonthlyPurchasesSales(timeframe = 'monthly') {
        try {
            const response = await fetch('/dashboard/monthly-purchases-sales/');
            if (!response.ok) {
                throw new Error('Failed to fetch monthly purchases and sales');
            }
            const data = await response.json();
            
            // Prepare chart data based on timeframe
            let chartData;
            switch(timeframe) {
                case 'monthly':
                    chartData = {
                        labels: data.labels,
                        datasets: [
                            {
                                label: 'Sales',
                                data: data.sales,
                                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1
                            },
                            {
                                label: 'Purchases',
                                data: data.purchases,
                                backgroundColor: 'rgba(255, 206, 86, 0.6)',
                                borderColor: 'rgba(255, 206, 86, 1)',
                                borderWidth: 1
                            }
                        ]
                    };
                    break;
                default:
                    chartData = {
                        labels: data.labels,
                        datasets: [
                            {
                                label: 'Sales',
                                data: data.sales,
                                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1
                            },
                            {
                                label: 'Purchases',
                                data: data.purchases,
                                backgroundColor: 'rgba(255, 206, 86, 0.6)',
                                borderColor: 'rgba(255, 206, 86, 1)',
                                borderWidth: 1
                            }
                        ]
                    };
            }

            return chartData;
        } catch (error) {
            console.error('Error fetching monthly purchases and sales:', error);
            return {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Sales',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Purchases',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(255, 206, 86, 0.6)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    }
                ]
            };
        }
    }

    async function updatePurchasesSalesChart(timeframe = 'monthly') {
        let labels, salesData, purchasesData;

        if (timeframe === 'monthly') {
            // Fetch live data
            const monthlyData = await fetchMonthlyPurchasesSales();
            labels = monthlyData.labels;  // Full 12 months
            salesData = monthlyData.datasets[0].data;
            purchasesData = monthlyData.datasets[1].data;
        } else {
            // Use existing logic for other timeframes
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            salesData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
            purchasesData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        }

        // Get current month and year
        const currentDate = new Date();
        const currentMonth = currentDate.getMonth();

        // Prepare chart configuration
        const chartConfig = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Sales',
                        data: salesData,
                        backgroundColor: labels.map((label, index) => 
                            index === currentMonth ? 'rgba(54, 162, 235, 1)' : 'rgba(54, 162, 235, 0.5)'
                        ),
                        borderWidth: 1.5,
                        barThickness: 15,
                        maxBarThickness: 20,
                        borderRadius: 5
                    },
                    {
                        label: 'Purchases',
                        data: purchasesData,
                        backgroundColor: labels.map((label, index) => 
                            index === currentMonth ? 'rgba(255, 206, 86, 1)' : 'rgba(255, 206, 86, 0.5)'
                        ),
                        borderWidth: 0,
                        barThickness: 15,
                        maxBarThickness: 20,
                        borderRadius: 5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 5,
                        right: 5
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Purchases vs Sales',
                        font: {
                            size: 12
                        }
                    },
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 10
                            },
                            usePointStyle: true,
                            pointStyle: 'circle',
                            boxWidth: 10,
                            boxHeight: 10
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 9
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 9
                            },
                            callback: function(value) {
                                return formatNumber(value);
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    intersect: false
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        };

        // Create or update chart with configuration
        if (!window.purchasesSalesChartInstance) {
            const ctx = document.getElementById('purchasesSalesChart').getContext('2d');
            window.purchasesSalesChartInstance = new Chart(ctx, chartConfig);
        } else {
            window.purchasesSalesChartInstance.data = chartConfig.data;
            window.purchasesSalesChartInstance.options = chartConfig.options;
            window.purchasesSalesChartInstance.update();
        }
    }

    // Add timeframe toggle for Purchases vs Sales chart
    const purchasesSalesTimeframeLabels = document.querySelectorAll('.purchases-sales-timeframe');
    if (purchasesSalesTimeframeLabels) {
        purchasesSalesTimeframeLabels.forEach(label => {
            label.addEventListener('click', function() {
                const timeframe = this.getAttribute('data-timeframe');
                
                // Toggle active class
                purchasesSalesTimeframeLabels.forEach(l => 
                    l.classList.toggle('active', l === this)
                );

                // Update chart
                updatePurchasesSalesChart(timeframe);
            });
        });
    }

    // Initial chart load
    updatePurchasesSalesChart();

    async function fetchMonthlyFinancialTrends() {
        try {
            const response = await fetch('/dashboard/monthly-financial-trends/');
            if (!response.ok) {
                throw new Error('Failed to fetch monthly financial trends');
            }
            const data = await response.json();
            
            // Debugging: Log the entire financial data
            console.group('Monthly Financial Trends Debug');
            console.log('Full Data:', data);
            console.log('Labels:', data.labels);
            console.log('Revenue:', data.financial_data.revenue);
            console.log('Expenses:', data.financial_data.expenses);
            console.log('Purchases:', data.financial_data.purchases);
            console.log('Quotes:', data.financial_data.quotes);
            console.log('Net Profit:', data.financial_data.net_profit);
            console.groupEnd();

            return {
                'daily': {
                    labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    revenue: [0, 0, 0, 0, 0, 0, 0],
                    expenses: [0, 0, 0, 0, 0, 0, 0],
                    purchases: [0, 0, 0, 0, 0, 0, 0],
                    quotes: [0, 0, 0, 0, 0, 0, 0],
                    net_profit: [0, 0, 0, 0, 0, 0, 0]
                },
                'weekly': {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    revenue: [0, 0, 0, 0],
                    expenses: [0, 0, 0, 0],
                    purchases: [0, 0, 0, 0],
                    quotes: [0, 0, 0, 0],
                    net_profit: [0, 0, 0, 0]
                },
                'monthly': {
                    labels: data.labels,
                    revenue: data.financial_data.revenue,
                    expenses: data.financial_data.expenses,
                    purchases: data.financial_data.purchases,
                    quotes: data.financial_data.quotes,
                    net_profit: data.financial_data.net_profit,
                    gross_profit: data.financial_data.gross_profit
                }
            };
        } catch (error) {
            console.error('Error fetching monthly financial trends:', error);
            return {
                'monthly': {
                    labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
                    revenue: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    expenses: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    purchases: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    quotes: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    net_profit: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    gross_profit: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                }
            };
        }
    }

    async function updateFinancialTrendsChart(timeframe = 'monthly') {
        try {
            console.log('Starting updateFinancialTrendsChart');
            let labels, revenueData, expensesData, purchasesData, quotesData, netProfitData, grossProfitData;

            if (timeframe === 'monthly') {
                // Fetch live data
                const monthlyData = await fetchMonthlyFinancialTrends();
                console.log('Fetched Monthly Financial Trends Data:', monthlyData);
                labels = monthlyData.monthly.labels;
                revenueData = monthlyData.monthly.revenue;
                expensesData = monthlyData.monthly.expenses;
                purchasesData = monthlyData.monthly.purchases;
                quotesData = monthlyData.monthly.quotes;
                netProfitData = monthlyData.monthly.net_profit;
                grossProfitData = monthlyData.monthly.gross_profit;

                console.log('Revenue Data:', revenueData);
                console.log('Expenses Data:', expensesData);
            } else {
                // Use placeholder data for other timeframes
                labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                revenueData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                expensesData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                purchasesData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                quotesData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                netProfitData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                grossProfitData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
            }

            // Verify canvas element exists
            const ctx = document.getElementById('monthlyTrendsChart');
            if (!ctx) {
                console.error('Canvas element #monthlyTrendsChart not found!');
                return;
            }
            const chartContext = ctx.getContext('2d');

            // Prepare chart configuration
            const chartConfig = {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: revenueData,
                            backgroundColor: 'rgba(46, 204, 113, 0.2)',
                            borderColor: 'rgba(46, 204, 113, 1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: 'rgba(46, 204, 113, 1)',
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Expenses',
                            data: expensesData,
                            backgroundColor: 'rgba(255, 0, 0, 0.2)',
                            borderColor: 'rgba(255, 0, 0, 1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: 'rgba(255, 0, 0, 1)',
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Purchases',
                            data: purchasesData,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Quotes',
                            data: quotesData,
                            backgroundColor: 'rgba(255, 206, 86, 0.2)',
                            borderColor: 'rgba(255, 206, 86, 1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                            pointHoverRadius: 6
                        },
                        {
                            label: 'Gross Profit',
                            data: grossProfitData,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: 'rgba(153, 102, 255, 1)',
                            pointHoverRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'nearest',
                        intersect: false
                    },
                    elements: {
                        line: {
                            borderWidth: 0.5
                        }
                    },
                    plugins: {
                        title: {
                            display: false,
                            text: 'Monthly Financial Trends',
                            font: {
                                size: 14
                            }
                        },
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                pointStyle: 'circle',
                                boxWidth: 10,
                                boxHeight: 10
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'rgba(255, 255, 255, 0.8)',
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            borderWidth: 1,
                            cornerRadius: 4,
                            padding: 10,
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.parsed.y !== null) {
                                        label += new Intl.NumberFormat('en-KE', { 
                                            style: 'currency', 
                                            currency: 'KES' 
                                        }).format(context.parsed.y);
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Month'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Amount (KES)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                }
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            };

            // Create or update chart with configuration
            if (!window.financialTrendsChartInstance) {
                console.log('Creating new chart instance');
                window.financialTrendsChartInstance = new Chart(chartContext, chartConfig);
            } else {
                console.log('Updating existing chart instance');
                window.financialTrendsChartInstance.data = chartConfig.data;
                window.financialTrendsChartInstance.options = chartConfig.options;
                window.financialTrendsChartInstance.update();
            }
        } catch (error) {
            console.error('Error in updateFinancialTrendsChart:', error);
        }
    }

    // Initial chart load
    updateFinancialTrendsChart();

    async function fetchMonthlyPurchasesSales() {
        try {
            const response = await fetch('/dashboard/monthly-purchases-sales/');
            if (!response.ok) {
                throw new Error('Failed to fetch monthly purchases and sales');
            }
            const data = await response.json();
            
            // Debug logging
            console.log('Purchases vs Sales Data:', data);

            return {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Sales',
                        data: data.sales,
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(46, 204, 113, 1)',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Purchases',
                        data: data.purchases,
                        backgroundColor: 'rgba(255, 0, 0, 0.2)',
                        borderColor: 'rgba(255, 0, 0, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(255, 0, 0, 1)',
                        pointHoverRadius: 6
                    }
                ]
            };
        } catch (error) {
            console.error('Error fetching monthly purchases and sales:', error);
            return {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Sales',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(46, 204, 113, 1)',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Purchases',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(255, 0, 0, 0.2)',
                        borderColor: 'rgba(255, 0, 0, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(255, 0, 0, 1)',
                        pointHoverRadius: 6
                    }
                ]
            };
        }
    }

    // Render Purchases vs Sales Chart
    async function renderPurchasesSalesChart() {
        const ctx = document.getElementById('purchasesSalesChart').getContext('2d');
        
        // Destroy existing chart instance if it exists
        if (window.purchasesSalesChartInstance) {
            window.purchasesSalesChartInstance.destroy();
        }

        const chartData = await fetchMonthlyPurchasesSales();

        window.purchasesSalesChartInstance = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            boxWidth: 10,
                            boxHeight: 10
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Months'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount (KES)'
                        },
                        ticks: {
                            callback: function(value) {
                                return formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
    }

    // Call the render function when the page loads
    renderPurchasesSalesChart();

    async function fetchMonthlyFinancialTrends() {
        try {
            const response = await fetch('/dashboard/monthly-financial-trends/');
            if (!response.ok) {
                throw new Error('Failed to fetch monthly financial trends');
            }
            const data = await response.json();
            
            // Debug logging
            console.log('Monthly Financial Trends Data:', data);

            return {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: data.revenue,
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(46, 204, 113, 1)',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Expenses',
                        data: data.expenses,
                        backgroundColor: 'rgba(255, 0, 0, 0.2)',
                        borderColor: 'rgba(255, 0, 0, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(255, 0, 0, 1)',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Purchases',
                        data: data.purchases,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Quotes',
                        data: data.quotes,
                        backgroundColor: 'rgba(255, 206, 86, 0.2)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(255, 206, 86, 1)',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Gross Profit',
                        data: data.gross_profit,
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(153, 102, 255, 1)',
                        pointHoverRadius: 6
                    }
                ]
            };
        } catch (error) {
            console.error('Error fetching monthly financial trends:', error);
            return {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Revenue',
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(46, 204, 113, 1)',
                        pointHoverRadius: 6
                    },
                    // ... other datasets with zero data
                ]
            };
        }
    }

    // Render Monthly Financial Trends Chart
    async function renderFinancialTrendsChart() {
        const ctx = document.getElementById('financialTrendsChart').getContext('2d');
        
        // Destroy existing chart instance if it exists
        if (window.financialTrendsChartInstance) {
            window.financialTrendsChartInstance.destroy();
        }

        const chartData = await fetchMonthlyFinancialTrends();

        window.financialTrendsChartInstance = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 0,
                        bottom: 0,
                        left: 0,
                        right: 0
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            boxWidth: 10,
                            boxHeight: 10
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Months'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Amount (KES)'
                        },
                        ticks: {
                            callback: function(value) {
                                return formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
    }

    // Call the render function when the page loads
    renderFinancialTrendsChart();
});