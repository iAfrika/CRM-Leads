document.addEventListener('DOMContentLoaded', function() {
    // Filter functionality
    const monthFilter = document.getElementById('monthFilter');
    const searchFilter = document.getElementById('searchFilter');

    function applyFilters() {
        const month = monthFilter.value;
        const search = searchFilter.value.toLowerCase();
        
        document.querySelectorAll('.invoice-table tbody tr').forEach(row => {
            const date = row.querySelector('td:nth-child(3)').textContent;
            const searchText = row.textContent.toLowerCase();
            
            const matchesMonth = !month || date.includes(month);
            const matchesSearch = !search || searchText.includes(search);
            
            row.style.display = matchesMonth && matchesSearch ? '' : 'none';
        });
    }

    monthFilter?.addEventListener('change', applyFilters);
    searchFilter?.addEventListener('input', debounce(applyFilters, 300));

    // Download functionality
    document.querySelectorAll('.download-invoice').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const invoiceId = this.dataset.id;
            
            try {
                const response = await fetch(`/documents/${invoiceId}/download/`, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    window.open(response.url, '_blank');
                } else {
                    throw new Error('Failed to download invoice');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to download invoice. Please try again.');
            }
        });
    });
});

// Utility function
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