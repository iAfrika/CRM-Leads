document.addEventListener('DOMContentLoaded', function() {
    // Handle PDF generation
    document.querySelectorAll('.generate-pdf').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const quoteId = this.dataset.quoteId;
            
            try {
                const response = await fetch(`/documents/quote/${quoteId}/generate-pdf/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.open(data.pdf_url, '_blank');
                } else {
                    showError('Error generating PDF: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Failed to generate PDF. Please try again.');
            }
        });
    });

    // Handle invoice generation
    document.querySelectorAll('.generate-invoice').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const quoteId = this.dataset.quoteId;
            
            try {
                const response = await fetch(`/documents/quote/${quoteId}/generate-invoice/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showSuccess('Invoice generated successfully!');
                    // Optionally refresh the page or update the UI
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showError('Error generating invoice: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Failed to generate invoice. Please try again.');
            }
        });
    });

    // Handle sorting
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', function() {
            // Add sorting logic here if needed
        });
    });
}); 