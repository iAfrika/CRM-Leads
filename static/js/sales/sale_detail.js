document.addEventListener('DOMContentLoaded', function() {
    // Format numbers with thousand separators
    function formatNumber(number, decimals = 2) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }

    // Format currency with thousand separators
    function formatCurrency(number) {
        return '$' + formatNumber(number);
    }

    // Format all numeric values
    document.querySelectorAll('.numeric-value').forEach(element => {
        if (element.textContent.includes('%')) {
            // Handle percentage values
            const value = parseFloat(element.textContent);
            if (!isNaN(value)) {
                element.textContent = formatNumber(value, 0) + '%';
            }
        } else {
            // Handle regular numbers
            const value = parseFloat(element.textContent);
            if (!isNaN(value)) {
                element.textContent = formatNumber(value);
            }
        }
    });

    // Format all currency values
    document.querySelectorAll('.currency-value').forEach(element => {
        // Remove existing currency symbol and formatting
        const rawValue = element.textContent.replace(/[$,]/g, '');
        const value = parseFloat(rawValue);
        if (!isNaN(value)) {
            element.textContent = formatCurrency(value);
        }
    });
}); 