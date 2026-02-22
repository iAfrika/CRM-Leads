document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('clientSearchInput');
    const clientTable = document.getElementById('clientTable');
    const tableRows = clientTable.querySelectorAll('tbody tr');

    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();

        tableRows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            const isVisible = rowText.includes(searchTerm);
            row.style.display = isVisible ? '' : 'none';
        });

        // Update client count dynamically
        const visibleRows = Array.from(tableRows).filter(row => row.style.display !== 'none');
        const clientCountElement = document.querySelector('.client-count');
        clientCountElement.textContent = `${visibleRows.length} clients`;
    });
});
