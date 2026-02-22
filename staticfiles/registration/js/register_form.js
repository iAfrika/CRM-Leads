/**
 * register_form.js
 * JavaScript functionality for the registration forms
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variables to track the current step
    let currentStep = 0;
    const form = document.querySelector('.registration-form');
    const steps = document.querySelectorAll('.form-step');
    const stepIndicators = document.querySelectorAll('.steps .step');
    
    console.log('DOM loaded', { 
        formFound: !!form, 
        stepsFound: steps.length, 
        indicatorsFound: stepIndicators.length 
    });
    
    // Initialize the form if it exists
    if (form && steps.length > 0) {
        initForm();
    }
    
    /**
     * Initialize the registration form
     */
    function initForm() {
        // Show the first step
        showStep(0);
        
        // Add event listeners to the next buttons
        const nextButtons = document.querySelectorAll('.btn-next');
        console.log('Next buttons found:', nextButtons.length);
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                console.log('Next button clicked, current step:', currentStep);
                if (validateStep(currentStep)) {
                    console.log('Step validated, moving to next step');
                    nextStep();
                } else {
                    console.log('Step validation failed');
                }
            });
        });
        
        // Add event listeners to the previous buttons
        const prevButtons = document.querySelectorAll('.btn-prev');
        prevButtons.forEach(button => {
            button.addEventListener('click', prevStep);
        });
        
        // Add event listeners to the form inputs for real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearError(this);
            });
            
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
        
        // Add event listener for form submission
        form.addEventListener('submit', function(e) {
            if (!validateAllSteps()) {
                e.preventDefault();
            }
        });
        
        // Initialize password toggle buttons
        initPasswordToggles();
        
        // Initialize plan selection
        initPlanSelection();
    }
    
    /**
     * Show a specific step in the form
     * @param {number} stepIndex The index of the step to show
     */
    function showStep(stepIndex) {
        console.log('Showing step:', stepIndex);
        // Hide all steps
        steps.forEach(step => step.style.display = 'none');
        
        // Show the current step
        steps[stepIndex].style.display = 'block';
        
        // Update step indicators
        updateStepIndicators(stepIndex);
        
        // Update current step
        currentStep = stepIndex;
        
        // Scroll to top of form
        form.scrollIntoView({ behavior: 'smooth' });
    }
    
    /**
     * Update the step indicators to reflect the current step
     * @param {number} stepIndex The index of the current step
     */
    function updateStepIndicators(stepIndex) {
        stepIndicators.forEach((indicator, index) => {
            // Remove all classes first
            indicator.classList.remove('active', 'completed');
            
            // Add appropriate class based on step index
            if (index < stepIndex) {
                indicator.classList.add('completed');
            } else if (index === stepIndex) {
                indicator.classList.add('active');
            }
        });
    }
    
    /**
     * Move to the next step in the form
     */
    function nextStep() {
        console.log('nextStep called, current step:', currentStep, 'total steps:', steps.length);
        if (currentStep < steps.length - 1) {
            showStep(currentStep + 1);
        }
    }
    
    /**
     * Move to the previous step in the form
     */
    function prevStep() {
        if (currentStep > 0) {
            showStep(currentStep - 1);
        }
    }
    
    /**
     * Validate a single field
     * @param {HTMLElement} field The field to validate
     * @returns {boolean} Whether the field is valid
     */
    function validateField(field) {
        // Skip validation for non-required empty fields
        if (!field.hasAttribute('required') && !field.value.trim()) {
            return true;
        }
        
        // Check for required fields
        if (field.hasAttribute('required') && !field.value.trim()) {
            showError(field, 'This field is required');
            return false;
        }
        
        // Validate email fields
        if (field.type === 'email' && field.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                showError(field, 'Please enter a valid email address');
                return false;
            }
        }
        
        // Validate password fields
        if (field.id === 'admin_password' && field.value.trim()) {
            if (field.value.length < 8) {
                showError(field, 'Password must be at least 8 characters');
                return false;
            }
        }
        
        // Validate password confirmation
        if (field.id === 'admin_password_confirm' && field.value.trim()) {
            const passwordField = document.getElementById('admin_password');
            if (passwordField && field.value !== passwordField.value) {
                showError(field, 'Passwords do not match');
                return false;
            }
        }
        
        // Clear any errors
        clearError(field);
        return true;
    }
    
    /**
     * Validate all fields in a step
     * @param {number} stepIndex The index of the step to validate
     * @returns {boolean} Whether the step is valid
     */
    function validateStep(stepIndex) {
        const stepFields = steps[stepIndex].querySelectorAll('input, select, textarea');
        console.log('Validating step', stepIndex, 'with', stepFields.length, 'fields');
        let isValid = true;
        
        // Validate each field in the step
        stepFields.forEach(field => {
            if (!validateField(field)) {
                console.log('Field validation failed:', field.id);
                isValid = false;
            }
        });
        
        console.log('Step validation result:', isValid);
        return isValid;
    }
    
    /**
     * Validate all steps in the form
     * @returns {boolean} Whether the whole form is valid
     */
    function validateAllSteps() {
        let isValid = true;
        
        // Validate each step
        for (let i = 0; i < steps.length; i++) {
            if (!validateStep(i)) {
                isValid = false;
                
                // Show the first invalid step
                if (i !== currentStep) {
                    showStep(i);
                }
                
                break;
            }
        }
        
        return isValid;
    }
    
    /**
     * Show an error message for a field
     * @param {HTMLElement} field The field with the error
     * @param {string} message The error message
     */
    function showError(field, message) {
        // Add error class to field
        field.classList.add('error');
        
        // Create or update error message
        let errorEl = field.nextElementSibling;
        if (!errorEl || !errorEl.classList.contains('form-error')) {
            errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            field.parentNode.insertBefore(errorEl, field.nextSibling);
        }
        
        errorEl.textContent = message;
        errorEl.classList.add('visible');
    }
    
    /**
     * Clear the error message for a field
     * @param {HTMLElement} field The field to clear the error for
     */
    function clearError(field) {
        // Remove error class from field
        field.classList.remove('error');
        
        // Remove error message
        const errorEl = field.nextElementSibling;
        if (errorEl && errorEl.classList.contains('form-error')) {
            errorEl.classList.remove('visible');
        }
    }
    
    /**
     * Initialize password toggle buttons
     */
    function initPasswordToggles() {
        const toggleButtons = document.querySelectorAll('.password-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const passwordField = this.parentNode.querySelector('input');
                
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                } else {
                    passwordField.type = 'password';
                    this.innerHTML = '<i class="fas fa-eye"></i>';
                }
            });
        });
    }
    
    /**
     * Initialize plan selection functionality
     */
    function initPlanSelection() {
        const planCards = document.querySelectorAll('.plan-card[data-plan]');
        const planInput = document.getElementById('selected_plan');
        
        if (planCards.length > 0 && planInput) {
            // Initially select the plan from the hidden input
            planCards.forEach(card => {
                if (card.dataset.plan === planInput.value) {
                    card.classList.add('selected');
                }
                
                // Add click event listener
                card.addEventListener('click', function() {
                    // Remove selected class from all cards
                    planCards.forEach(c => c.classList.remove('selected'));
                    
                    // Add selected class to clicked card
                    this.classList.add('selected');
                    
                    // Update the hidden input value
                    planInput.value = this.dataset.plan;
                });
            });
        }
    }
    
    // Initialize from URL parameters if present
    const urlParams = new URLSearchParams(window.location.search);
    const planParam = urlParams.get('plan');
    
    if (planParam && document.getElementById('selected_plan')) {
        document.getElementById('selected_plan').value = planParam;
        
        // Select the corresponding card
        const planCard = document.querySelector(`.plan-card[data-plan="${planParam}"]`);
        if (planCard) {
            // Remove selected class from all cards
            document.querySelectorAll('.plan-card[data-plan]').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Add selected class to the matching card
            planCard.classList.add('selected');
        }
    }
}); 