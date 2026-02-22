document.addEventListener('DOMContentLoaded', function() {
    // Format date input to use date picker
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        // Set default date to today if it's a new form
        if (!dateInput.value) {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            dateInput.value = `${year}-${month}-${day}`;
        }
    }

    // Format amount input to handle currency
    const amountInput = document.querySelector('input[name="amount"]');
    if (amountInput) {
        amountInput.addEventListener('blur', function() {
            // Remove non-numeric characters except decimal point
            let value = this.value.replace(/[^\d.]/g, '');
            
            // Ensure only one decimal point
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            // Format to 2 decimal places
            if (value && !isNaN(parseFloat(value))) {
                this.value = parseFloat(value).toFixed(2);
            }
        });
    }

    // Add new category option
    const categorySelect = document.querySelector('select[name="category"]');
    if (categorySelect) {
        // Check if "Add New Category" option exists
        let addNewOption = Array.from(categorySelect.options).find(option => 
            option.text === '+ Add New Category');
        
        // If not, add it
        if (!addNewOption) {
            addNewOption = document.createElement('option');
            addNewOption.text = '+ Add New Category';
            addNewOption.value = 'new';
            categorySelect.appendChild(addNewOption);
        }
        
        // Handle selection of "Add New Category"
        categorySelect.addEventListener('change', function() {
            if (this.value === 'new') {
                // Reset selection to previous value
                this.value = this.dataset.previousValue || '';
                
                // Prompt for new category name
                const categoryName = prompt('Enter new category name:');
                if (categoryName) {
                    // Here you would typically make an AJAX call to create the category
                    // For now, we'll just add it to the dropdown
                    const newOption = document.createElement('option');
                    newOption.text = categoryName;
                    newOption.value = 'temp_' + Date.now(); // Temporary ID
                    newOption.selected = true;
                    
                    // Insert before the "Add New" option
                    categorySelect.insertBefore(newOption, addNewOption);
                    
                    // Set the new value as selected
                    this.value = newOption.value;
                }
            }
            
            // Store current value for next time
            this.dataset.previousValue = this.value;
        });
        
        // Initialize previous value
        categorySelect.dataset.previousValue = categorySelect.value;
    }
}); 