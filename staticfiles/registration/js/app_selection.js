/**
 * app_selection.js
 * JavaScript functionality for the app selection page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variables for tracking selected apps and total price
    const selectedApps = new Map();
    let totalPrice = 0;
    
    // DOM elements
    const appCards = document.querySelectorAll('.app-card');
    const appToggles = document.querySelectorAll('.app-toggle input[type="checkbox"]');
    const summaryApps = document.querySelector('.summary-apps');
    const summaryTotal = document.querySelector('.summary-total');
    const summaryForm = document.getElementById('app-selection-form');
    const selectedAppsInput = document.getElementById('selected-apps-input');
    
    // Initialize app cards with animations
    appCards.forEach((card, index) => {
        // Set animation delay based on index
        card.style.animationDelay = `${0.1 * (index + 1)}s`;
        
        // Add click event for card selection
        card.addEventListener('click', function(e) {
            // Don't toggle if clicking on the toggle switch directly
            if (e.target.closest('.app-toggle')) {
                return;
            }
            
            // Find the toggle checkbox for this card
            const toggle = this.querySelector('input[type="checkbox"]');
            if (toggle) {
                // Toggle the checkbox
                toggle.checked = !toggle.checked;
                
                // Trigger change event
                const event = new Event('change');
                toggle.dispatchEvent(event);
            }
        });
    });
    
    // Add event listeners to toggle switches
    appToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const appCard = this.closest('.app-card');
            const appId = appCard.dataset.appId;
            const appName = appCard.querySelector('.app-header h3').textContent;
            const appPrice = parseFloat(appCard.querySelector('.app-price').dataset.price || 0);
            
            if (this.checked) {
                // Select the app
                appCard.classList.add('selected');
                
                // Add to selected apps
                selectedApps.set(appId, {
                    name: appName,
                    price: appPrice
                });
            } else {
                // Deselect the app
                appCard.classList.remove('selected');
                
                // Remove from selected apps
                selectedApps.delete(appId);
            }
            
            // Update the summary
            updateSummary();
        });
        
        // Trigger change event on page load if the checkbox is checked by default
        if (toggle.checked) {
            const event = new Event('change');
            toggle.dispatchEvent(event);
        }
    });
    
    /**
     * Update the summary section with selected apps and total price
     */
    function updateSummary() {
        // Clear current summary
        if (summaryApps) {
            summaryApps.innerHTML = '';
        }
        
        // Reset total price
        totalPrice = 0;
        
        // Add each selected app to the summary
        selectedApps.forEach((app, id) => {
            // Add to total price
            totalPrice += app.price;
            
            // Create summary item
            if (summaryApps) {
                const item = document.createElement('div');
                item.className = 'summary-app-item';
                item.innerHTML = `
                    <span class="summary-app-name">${app.name}</span>
                    <span class="summary-app-price">KES ${app.price.toLocaleString()}</span>
                `;
                summaryApps.appendChild(item);
            }
        });
        
        // Update total price display
        if (summaryTotal) {
            summaryTotal.textContent = `KES ${totalPrice.toLocaleString()}`;
        }
        
        // Update hidden input with selected apps
        if (selectedAppsInput) {
            const selectedAppIds = Array.from(selectedApps.keys());
            selectedAppsInput.value = JSON.stringify(selectedAppIds);
        }
        
        // Update continue button state
        const continueBtn = document.querySelector('.btn-continue');
        if (continueBtn) {
            if (selectedApps.size === 0) {
                continueBtn.disabled = true;
                continueBtn.classList.add('disabled');
            } else {
                continueBtn.disabled = false;
                continueBtn.classList.remove('disabled');
            }
        }
    }
    
    // Handle form submission
    if (summaryForm) {
        summaryForm.addEventListener('submit', function(e) {
            // Prevent submission if no apps selected
            if (selectedApps.size === 0) {
                e.preventDefault();
                alert('Please select at least one app to continue.');
            }
        });
    }
    
    // Initialize apps from URL parameters (if any)
    const urlParams = new URLSearchParams(window.location.search);
    const preselectedApps = urlParams.get('apps');
    
    if (preselectedApps) {
        try {
            const appIds = preselectedApps.split(',');
            
            appIds.forEach(id => {
                const appCard = document.querySelector(`.app-card[data-app-id="${id}"]`);
                if (appCard) {
                    const toggle = appCard.querySelector('input[type="checkbox"]');
                    if (toggle && !toggle.checked) {
                        toggle.checked = true;
                        
                        // Trigger change event
                        const event = new Event('change');
                        toggle.dispatchEvent(event);
                    }
                }
            });
        } catch (error) {
            console.error('Error parsing preselected apps:', error);
        }
    }
}); 