// Utility functions and shared behaviors
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};

const showAlert = (message, type = 'info') => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    document.querySelector('.messages-container').appendChild(alertDiv);
    
    setTimeout(() => alertDiv.remove(), 3000);
};

// ... other shared utilities ... 