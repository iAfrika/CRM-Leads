document.addEventListener('DOMContentLoaded', function() {
    const addExpenseBtn = document.getElementById('addExpenseBtn');
    const cancelExpenseBtn = document.getElementById('cancelExpenseBtn');
    const expenseFormSection = document.getElementById('expenseFormSection');
    const expenseForm = document.getElementById('expenseForm');
    
    // Show/Hide form
    addExpenseBtn.addEventListener('click', () => {
        expenseFormSection.style.display = 'block';
        expenseForm.reset();
    });
    
    cancelExpenseBtn.addEventListener('click', () => {
        expenseFormSection.style.display = 'none';
    });
    
    // Form submission
    expenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(expenseForm);
        
        try {
            const response = await fetch('/documents/expenditure/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while saving the expense');
        }
    });
    
    // Filters
    const categoryFilter = document.getElementById('categoryFilter');
    const monthFilter = document.getElementById('monthFilter');
    const searchFilter = document.getElementById('searchFilter');
    
    function applyFilters() {
        const category = categoryFilter.value;
        const month = monthFilter.value;
        const search = searchFilter.value;
        
        window.location.href = `/documents/expenditure/?category=${category}&month=${month}&search=${search}`;
    }
    
    categoryFilter.addEventListener('change', applyFilters);
    monthFilter.addEventListener('change', applyFilters);
    searchFilter.addEventListener('input', debounce(applyFilters, 500));

    // Edit expense
    document.querySelectorAll('.edit-expense').forEach(button => {
        button.addEventListener('click', async (e) => {
            const id = e.currentTarget.dataset.id;
            const row = e.currentTarget.closest('tr');
            
            // Fill form with current values
            document.getElementById('title').value = row.cells[1].textContent;
            document.getElementById('category').value = row.cells[2].dataset.value;
            document.getElementById('amount').value = row.cells[3].textContent.replace('$', '');
            document.getElementById('date').value = row.cells[0].dataset.value;
            document.getElementById('description').value = row.cells[4].textContent;
            
            // Show form and update submit handler
            expenseFormSection.style.display = 'block';
            expenseForm.onsubmit = async (e) => {
                e.preventDefault();
                
                const formData = new FormData(expenseForm);
                
                try {
                    const response = await fetch(`/documents/expenditure/${id}/edit/`, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while updating the expense');
                }
            };
        });
    });

    // Delete expense
    document.querySelectorAll('.delete-expense').forEach(button => {
        button.addEventListener('click', async (e) => {
            if (!confirm('Are you sure you want to delete this expense?')) {
                return;
            }
            
            const id = e.currentTarget.dataset.id;
            
            try {
                const response = await fetch(`/documents/expenditure/${id}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while deleting the expense');
            }
        });
    });
});

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
} 