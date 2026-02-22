/**
 * Document Detail functionality
 * Handles invoice generation and document sharing
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeInvoiceGeneration();
    initializeDocumentSharing();
});

/**
 * Initialize invoice generation functionality
 */
function initializeInvoiceGeneration() {
    const generateInvoiceBtn = document.getElementById('generateInvoiceBtn');
    if (generateInvoiceBtn) {
        generateInvoiceBtn.addEventListener('click', async function() {
            try {
                const quoteId = this.dataset.quoteId;
                const csrfToken = getCSRFToken();
                
                const response = await fetch(`/documents/quote/${quoteId}/generate-invoice/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert('Error generating invoice: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to generate invoice. Please try again.');
            }
        });
    }
}

/**
 * Initialize document sharing functionality
 */
function initializeDocumentSharing() {
    const shareDocumentBtn = document.getElementById('shareDocumentBtn');
    const shareModal = document.getElementById('shareDocumentModal');
    const shareForm = document.getElementById('shareDocumentForm');
    
    if (shareDocumentBtn) {
        shareDocumentBtn.addEventListener('click', function() {
            console.log('Share button clicked');
            resetShareModal();
            
            // Set document ID
            document.getElementById('shareDocumentId').value = this.dataset.documentId;
            
            // Show modal
            showShareModal();
        });
    }
    
    // Handle share method selection
    const shareMethodButtons = document.querySelectorAll('.share-options button');
    shareMethodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const shareMethod = this.dataset.shareMethod;
            showShareForm(shareMethod);
        });
    });
    
    // Handle form submission
    if (shareForm) {
        shareForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitShareForm(this);
        });
    }
}

/**
 * Reset share modal to initial state
 */
function resetShareModal() {
    const shareForm = document.getElementById('shareDocumentForm');
    
    if (shareForm) {
        shareForm.style.display = 'none';
    }
    
    const shareOptions = document.querySelector('.share-options');
    if (shareOptions) {
        shareOptions.style.display = 'flex';
    }
    
    const telegramDetails = document.querySelector('.telegram-details');
    const emailDetails = document.querySelector('.email-details');
    
    if (telegramDetails) telegramDetails.style.display = 'none';
    if (emailDetails) emailDetails.style.display = 'none';
}

/**
 * Show share modal
 */
function showShareModal() {
    const shareModal = document.getElementById('shareDocumentModal');
    
    if (shareModal) {
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bootstrapModal = new bootstrap.Modal(shareModal);
            bootstrapModal.show();
        } else {
            shareModal.style.display = 'block';
            shareModal.classList.add('show');
        }
    }
}

/**
 * Show share form with specific method
 */
function showShareForm(shareMethod) {
    const shareForm = document.getElementById('shareDocumentForm');
    const shareOptions = document.querySelector('.share-options');
    
    // Hide share options
    if (shareOptions) {
        shareOptions.style.display = 'none';
    }
    
    // Show form
    if (shareForm) {
        shareForm.style.display = 'block';
        document.getElementById('shareMethod').value = shareMethod;
    }
    
    // Show specific details
    if (shareMethod === 'telegram') {
        const telegramDetails = document.querySelector('.telegram-details');
        if (telegramDetails) {
            telegramDetails.style.display = 'block';
        }
    } else if (shareMethod === 'email') {
        const emailDetails = document.querySelector('.email-details');
        if (emailDetails) {
            emailDetails.style.display = 'block';
        }
    }
}

/**
 * Submit share form
 */
async function submitShareForm(form) {
    try {
        const formData = new FormData(form);
        const csrfToken = getCSRFToken();
        
        const response = await fetch('/documents/share/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Document shared successfully!');
            hideShareModal();
        } else {
            alert('Failed to share document: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while sharing the document.');
    }
}

/**
 * Hide share modal
 */
function hideShareModal() {
    const shareModal = document.getElementById('shareDocumentModal');
    
    if (shareModal) {
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(shareModal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        } else {
            shareModal.style.display = 'none';
            shareModal.classList.remove('show');
        }
    }
}

/**
 * Get CSRF token from various sources
 */
function getCSRFToken() {
    // Try to get from meta tag first
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    
    // Try to get from form input
    const formToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (formToken) {
        return formToken.value;
    }
    
    // Try to get from cookie
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
}

// Make functions available globally if needed
window.showShareModal = showShareModal;
window.hideShareModal = hideShareModal;
