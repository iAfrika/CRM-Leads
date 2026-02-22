/**
 * Banking App JavaScript
 * This file contains all the interactive functionality for the banking app.
 */

document.addEventListener('DOMContentLoaded', function() {
    // PIN Input Formatting
    const pinInputs = document.querySelectorAll('.pin-input');
    if (pinInputs.length > 0) {
        pinInputs.forEach(input => {
            // Only allow numbers
            input.addEventListener('keypress', function(e) {
                if (e.key < '0' || e.key > '9') {
                    e.preventDefault();
                }
            });
            
            // Limit to 4 digits
            input.addEventListener('input', function() {
                if (this.value.length > 4) {
                    this.value = this.value.slice(0, 4);
                }
            });
        });
    }
    
    // Amount Input Validation
    const amountInputs = document.querySelectorAll('.amount-input');
    if (amountInputs.length > 0) {
        amountInputs.forEach(input => {
            // Ensure positive values
            input.addEventListener('change', function() {
                if (parseFloat(this.value) <= 0) {
                    this.setCustomValidity('Amount must be greater than zero');
                } else {
                    this.setCustomValidity('');
                }
            });
        });
    }
    
    // Account Number Input Validation
    const accountNumberInputs = document.querySelectorAll('.account-number-input');
    if (accountNumberInputs.length > 0) {
        accountNumberInputs.forEach(input => {
            // Only allow numbers
            input.addEventListener('keypress', function(e) {
                if (e.key < '0' || e.key > '9') {
                    e.preventDefault();
                }
            });
        });
    }
    
    // PIN Confirmation Check
    const changePinForm = document.getElementById('change-pin-form');
    if (changePinForm) {
        changePinForm.addEventListener('submit', function(e) {
            const newPin = document.getElementById('new_pin').value;
            const confirmPin = document.getElementById('confirm_pin').value;
            
            if (newPin !== confirmPin) {
                e.preventDefault();
                alert('New PIN and confirmation do not match');
            }
        });
    }
    
    // Transaction Filter
    const transactionFilter = document.getElementById('transaction-filter');
    if (transactionFilter) {
        transactionFilter.addEventListener('change', function() {
            const filterValue = this.value.toLowerCase();
            const transactionItems = document.querySelectorAll('.transaction-item');
            
            transactionItems.forEach(item => {
                const transactionType = item.getAttribute('data-type').toLowerCase();
                
                if (filterValue === 'all' || transactionType === filterValue) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // Balance Chart
    const balanceChartCanvas = document.getElementById('balance-chart');
    if (balanceChartCanvas) {
        // Sample data - in a real app, this would come from the backend
        const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const data = {
            labels: labels,
            datasets: [{
                label: 'Account Balance',
                data: [1200, 1900, 1700, 2100, 2300, 2500],
                backgroundColor: 'rgba(0, 123, 255, 0.2)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 2,
                tension: 0.4
            }]
        };
        
        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Balance: $' + context.raw.toLocaleString();
                            }
                        }
                    }
                }
            }
        };
        
        new Chart(balanceChartCanvas, config);
    }
}); 