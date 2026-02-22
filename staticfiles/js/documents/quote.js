document.addEventListener('DOMContentLoaded', function() {
    const quoteForm = document.getElementById('quote-form');
    const addItemBtn = document.getElementById('add-item');
    const quoteItems = document.getElementById('quote-items');
    
    // Add new item row
    addItemBtn.addEventListener('click', function() {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'quote-item';
        itemDiv.innerHTML = `
            <input type="text" name="items[][description]" placeholder="Description" required>
            <input type="number" name="items[][quantity]" placeholder="Quantity" required>
            <input type="number" name="items[][unit_price]" placeholder="Unit Price" required>
            <button type="button" class="remove-item">Remove</button>
        `;
        quoteItems.appendChild(itemDiv);
    });
    
    // Remove item row
    quoteItems.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            e.target.parentElement.remove();
        }
    });
    
    // Handle form submission
    quoteForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData(this);
            const response = await fetch('/documents/quote/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.open(data.pdf_url, '_blank');
            } else {
                throw new Error(data.error);
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create quote. Please try again.');
        }
    });
}); 