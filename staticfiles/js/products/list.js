/**
 * Set up delete confirmation for items
 * @param {string} deleteUrlName - The URL name for the delete view
 */
function setupDeleteConfirmation(deleteUrlName) {
    const deleteModal = document.getElementById('deleteModal');
    const deleteForm = document.getElementById('deleteForm');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const deleteButtons = document.querySelectorAll('.delete-item');
    
    if (!deleteModal || !deleteForm || !cancelDeleteBtn) {
        console.warn('Delete modal elements not found');
        return;
    }
    
    // Handle clicking delete buttons
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemId = this.dataset.id;
            const itemType = this.dataset.type || 'item';
            
            if (!itemId) {
                console.error('No item ID provided for deletion');
                return;
            }
            
            // Update the form action URL
            deleteForm.action = `/${itemType}s/${itemId}/delete/`;
            
            // If URL name provided, use Django's URL pattern instead
            if (deleteUrlName) {
                deleteForm.action = deleteUrlName.replace('0', itemId);
            }
            
            // Show the modal
            deleteModal.classList.add('show');
        });
    });
    
    // Handle cancel button
    cancelDeleteBtn.addEventListener('click', function() {
        deleteModal.classList.remove('show');
    });
    
    // Close modal when clicking outside
    deleteModal.addEventListener('click', function(e) {
        if (e.target === deleteModal) {
            deleteModal.classList.remove('show');
        }
    });
    
    // Close modal with escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && deleteModal.classList.contains('show')) {
            deleteModal.classList.remove('show');
        }
    });
    
    // Close button in header
    const closeBtn = deleteModal.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            deleteModal.classList.remove('show');
        });
    }
} 