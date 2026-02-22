document.addEventListener('DOMContentLoaded', function() {
    /**
     * UTILITIES
     */
    
    // Format currency values
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: 'KES'
        }).format(value);
    };

    // Safe JSON parse with improved handling
    const safeJSONParse = (data, defaultValue = []) => {
        if (!data || data === '[]' || data === '' || data === 'null') return defaultValue;
        
        try {
            // If it's already an array or object, return it
            if (typeof data === 'object') return data;
            
            // Try to parse it
            const parsed = JSON.parse(data);
            
            // Ensure we return the default if parsing returns null or undefined
            return parsed || defaultValue;
        } catch (e) {
            console.error('Error parsing JSON:', e, 'Raw data:', data);
            
            // Special handling for string that looks like an array but isn't valid JSON
            if (typeof data === 'string' && data.startsWith('[') && data.endsWith(']')) {
                try {
                    // Try to clean it up and parse again
                    const cleanedData = data.replace(/'/g, '"');
                    return JSON.parse(cleanedData);
                } catch (innerError) {
                    console.error('Error parsing cleaned JSON:', innerError);
                }
            }
            
            return defaultValue;
        }
    };

    // Utility function to safely get a data attribute and parse it if needed
    const getDataAttribute = (element, attr, defaultValue = null, parse = false) => {
        // Try to get the attribute using getAttribute first (handles hyphenated names)
        let value = element.getAttribute(`data-${attr}`);
        
        // If not found, try using dataset (camelCase version)
        if (value === null) {
            // Convert hyphenated name to camelCase
            const camelCaseAttr = attr.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
            value = element.dataset[camelCaseAttr];
        }
        
        // If still not found or empty, return default
        if (value === null || value === '') return defaultValue;
        
        // Parse the value if requested
        if (parse) {
            if (parse === 'json') {
                return safeJSONParse(value, defaultValue);
            } else if (parse === 'float') {
                return parseFloat(value) || defaultValue;
            } else if (parse === 'int') {
                return parseInt(value, 10) || defaultValue;
            }
        }
        
        return value;
    };

    // Log current chart data for debugging
    const logChartData = (chartName, data) => {
        console.log(`${chartName} Chart Data:`, data);
    };

    // Common chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    padding: 15,
                    font: {
                        size: 12
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += formatCurrency(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };

    // Show diagnostic overlay if no data
    const showNoDataOverlay = (canvas, message = 'No data available for this chart') => {
        const container = canvas.parentElement;
        container.style.position = 'relative';
        
        // Clear any existing diagnostics
        const existingDiagnostics = container.querySelectorAll('.diagnostic-overlay');
        existingDiagnostics.forEach(el => el.remove());
        
        // Create the diagnostic overlay
        const overlay = document.createElement('div');
        overlay.className = 'diagnostic-overlay';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
        overlay.style.color = '#ef4444';
        overlay.style.fontWeight = 'bold';
        overlay.style.zIndex = '10';
        overlay.textContent = message;
        
        container.appendChild(overlay);
        console.warn(message, canvas.id);
    };

    /**
     * CHART INITIALIZATION
     */
    
    // Store chart instances to prevent conflicts
    const chartInstances = {};
    
    // Debug function to check all available data attributes on a canvas element
    const debugCanvasAttributes = (canvas) => {
        console.log('==========================================');
        console.log(`All data attributes for ${canvas.id}:`);
        
        // Get all dataset attributes
        const allAttributes = {};
        for (const key in canvas.dataset) {
            allAttributes[key] = canvas.dataset[key];
            console.log(`${key}: ${canvas.dataset[key]}`);
        }
        
        // Special check for hyphenated attributes
        const checkAttributes = ['quotes-amount', 'invoices-amount', 'monthly-revenue', 'monthly-expenditure'];
        for (const attr of checkAttributes) {
            const value = canvas.getAttribute(`data-${attr}`);
            if (value) {
                console.log(`data-${attr}: ${value} (directly from getAttribute)`);
            }
        }
        
        console.log('==========================================');
        return allAttributes;
    };

    // Helper to safely initialize a chart
    const initChart = (canvasId, type, data, options) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas not found: ${canvasId}`);
            return null;
        }
        
        // Destroy existing chart if any
        if (chartInstances[canvasId]) {
            chartInstances[canvasId].destroy();
            delete chartInstances[canvasId];
        }
        
        // Log raw data from canvas for debugging
        console.log(`Raw data for ${canvasId}:`, {
            allDatasets: canvas.dataset,
            specificFields: {
                quotes: canvas.dataset.quotes,
                invoices: canvas.dataset.invoices,
                quotesAmount: canvas.dataset.quotesAmount,
                invoicesAmount: canvas.dataset.invoicesAmount,
                revenue: canvas.dataset.revenue,
                expenditure: canvas.dataset.expenditure,
                monthlyRevenue: canvas.dataset.monthlyRevenue,
                monthlyExpenditure: canvas.dataset.monthlyExpenditure,
                months: canvas.dataset.months,
                purchases: canvas.dataset.purchases,
                sales: canvas.dataset.sales,
                expenses: canvas.dataset.expenses
            }
        });
        
        // Check for empty data
        if (!data.datasets || data.datasets.length === 0 || 
            !data.labels || data.labels.length === 0) {
            showNoDataOverlay(canvas, 'Chart data is missing labels or datasets');
            return null;
        }
        
        // Check if all data values are zero or null/undefined
        const allEmpty = data.datasets.every(ds => 
            !ds.data || ds.data.length === 0 || ds.data.every(val => val === 0 || val === null || val === undefined)
        );
        
        if (allEmpty) {
            showNoDataOverlay(canvas, 'All data values are zero or missing');
            return null;
        }
        
        // Log chart data for debugging
        logChartData(canvasId, data);
        
        // Create and store the chart
        const ctx = canvas.getContext('2d');
        chartInstances[canvasId] = new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });
        
        return chartInstances[canvasId];
    };

    /**
     * 2. REVENUE VS EXPENDITURE CHART
     */
    const setupRevenueVsExpenditureChart = () => {
        const canvas = document.getElementById('revenueVsExpenditureChart');
        if (!canvas) return;
        
        // Debug all attributes
        const attributes = debugCanvasAttributes(canvas);
        
        // Get data using our utility function
        let months = getDataAttribute(canvas, 'months', [], 'json');
        let monthlyRevenue = getDataAttribute(canvas, 'monthly-revenue', [], 'json');
        let monthlyExpenditure = getDataAttribute(canvas, 'monthly-expenditure', [], 'json');
        
        console.log('Revenue vs Expenditure data:', {
            months,
            monthlyRevenue,
            monthlyExpenditure
        });
        
        // If we don't have proper monthly data, use the single values
        if (!months.length || !monthlyRevenue.length || !monthlyExpenditure.length) {
            console.warn('Using fallback single values for Revenue vs Expenditure chart');
            
            // Create single value chart with revenue and expenditure totals
            const revenue = getDataAttribute(canvas, 'revenue', 0, 'float');
            const expenditure = getDataAttribute(canvas, 'expenditure', 0, 'float');
            
            console.log('Using single values:', { revenue, expenditure });
            
            const chartData = {
                labels: ['Revenue vs Expenditure'],
                datasets: [
                    {
                        label: 'Revenue (Paid Invoices)',
                        data: [revenue],
                        backgroundColor: 'rgba(16, 185, 129, 0.5)',
                        borderColor: 'rgb(16, 185, 129)',
                        borderWidth: 1
                    },
                    {
                        label: 'Expenditure (Expenses + Purchases)',
                        data: [expenditure],
                        backgroundColor: 'rgba(239, 68, 68, 0.5)',
                        borderColor: 'rgb(239, 68, 68)',
                        borderWidth: 1
                    }
                ]
            };
            
            initChart('revenueVsExpenditureChart', 'bar', chartData, commonOptions);
            return;
        }
        
        const chartData = {
            labels: months,
            datasets: [
                {
                    label: 'Revenue (Paid Invoices)',
                    data: monthlyRevenue,
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Expenditure (Expenses + Purchases)',
                    data: monthlyExpenditure,
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        };
        
        initChart('revenueVsExpenditureChart', 'line', chartData, commonOptions);
    };
    
    /**
     * 3. PURCHASES VS SALES CHART
     */
    const setupPurchasesVsSalesChart = () => {
        const canvas = document.getElementById('purchasesVsSalesChart');
        if (!canvas) return;
        
        // Debug all attributes
        const attributes = debugCanvasAttributes(canvas);
        
        // Extract data using our utility function
        const months = getDataAttribute(canvas, 'months', [], 'json');
        const purchases = getDataAttribute(canvas, 'purchases', [], 'json');
        const sales = getDataAttribute(canvas, 'sales', [], 'json');
        
        console.log('Purchases vs Sales data:', { months, purchases, sales });
        
        if (!months.length) {
            showNoDataOverlay(canvas, 'No month data available for Purchases vs Sales chart');
            return;
        }
        
        // If either purchases or sales data is missing, add zeros
        const purchasesData = purchases.length ? purchases : Array(months.length).fill(0);
        const salesData = sales.length ? sales : Array(months.length).fill(0);
        
        // Only proceed if we have at least some data
        if (purchasesData.every(val => val === 0) && salesData.every(val => val === 0)) {
            showNoDataOverlay(canvas, 'No purchase or sales data available');
            return;
        }
        
        const chartData = {
            labels: months,
            datasets: [
                {
                    label: 'Purchases',
                    data: purchasesData,
                    backgroundColor: 'rgba(239, 68, 68, 0.5)',
                    borderColor: 'rgb(239, 68, 68)',
                    borderWidth: 1
                },
                {
                    label: 'Sales',
                    data: salesData,
                    backgroundColor: 'rgba(16, 185, 129, 0.5)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 1
                }
            ]
        };
        
        initChart('purchasesVsSalesChart', 'bar', chartData, commonOptions);
    };
    
    /**
     * 4. MONTHLY TRENDS CHART
     */
    const setupMonthlyTrendsChart = () => {
        const canvas = document.getElementById('monthlyTrendsChart');
        if (!canvas) return;
        
        // Debug all attributes
        const attributes = debugCanvasAttributes(canvas);
        
        // Extract data using our utility function
        const months = getDataAttribute(canvas, 'months', [], 'json');
        const revenue = getDataAttribute(canvas, 'revenue', [], 'json');
        const expenses = getDataAttribute(canvas, 'expenses', [], 'json');
        
        console.log('Monthly Trends data:', { months, revenue, expenses });
        
        if (!months.length) {
            showNoDataOverlay(canvas, 'No month data available for Monthly Trends chart');
            return;
        }
        
        // If either revenue or expenses data is missing, add zeros
        const revenueData = revenue.length ? revenue : Array(months.length).fill(0);
        const expensesData = expenses.length ? expenses : Array(months.length).fill(0);
        
        // Only proceed if we have at least some data
        if (revenueData.every(val => val === 0) && expensesData.every(val => val === 0)) {
            showNoDataOverlay(canvas, 'No revenue or expense data available');
            return;
        }
        
        const chartData = {
            labels: months,
            datasets: [
                {
                    label: 'Revenue',
                    data: revenueData,
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Expenses',
                    data: expensesData,
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: false,
                    tension: 0.4
                }
            ]
        };
        
        initChart('monthlyTrendsChart', 'line', chartData, commonOptions);
    };
    
    /**
     * TIME PERIOD SELECTOR
     */
    const setupTimePeriodSelector = () => {
        const selector = document.getElementById('timePeriod');
        if (!selector) return;
        
        selector.addEventListener('change', function() {
            const url = new URL(window.location.href);
            url.searchParams.set('period', this.value);
            window.location.href = url.toString();
        });
    };
    
    /**
     * INITIALIZE ALL CHARTS
     */
    const initializeAllCharts = () => {
        console.log('Initializing dashboard charts');
        
        // Disable any existing charts to prevent conflicts
        if (window.Chart) {
            Chart.helpers.each(Chart.instances, function(instance) {
                instance.destroy();
            });
        }
        
        // Remove setupQuotesVsInvoicesChart() since it's handled by charts.js
        setupRevenueVsExpenditureChart();
        setupPurchasesVsSalesChart();
        setupMonthlyTrendsChart();
        setupTimePeriodSelector();
    };
    
    // Start chart initialization with a small delay to ensure DOM is fully loaded
    setTimeout(initializeAllCharts, 100);
});