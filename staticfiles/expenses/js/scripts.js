document.addEventListener('DOMContentLoaded', function() {
    // Initialize date filters
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    
    if (dateFromInput && dateToInput) {
        // Set max date for date inputs to today
        const today = new Date().toISOString().split('T')[0];
        dateFromInput.max = today;
        dateToInput.max = today;
        
        // Ensure 'to' date is not before 'from' date
        dateFromInput.addEventListener('change', function() {
            dateToInput.min = this.value;
        });
        
        dateToInput.addEventListener('change', function() {
            dateFromInput.max = this.value;
        });
    }
    
    // Initialize delete confirmation
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this expense?')) {
                e.preventDefault();
            }
        });
    });
    
    // Format currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const amount = parseFloat(this.value);
                if (!isNaN(amount)) {
                    this.value = amount.toFixed(2);
                }
            }
        });
    });
    
    // Handle file input styling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            if (label && fileName) {
                label.textContent = fileName;
            }
        });
    });
    
    // Handle category filter changes
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            this.closest('form').submit();
        });
    }
}); 