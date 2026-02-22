/**
 * Registration App JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Variables to store the current step and total steps
    let currentStep = 0;
    const steps = document.querySelectorAll('.form-step');
    const stepIndicators = document.querySelectorAll('.step');
    
    // Initialize the multi-step form
    if (steps.length > 0) {
        initMultiStepForm();
    }
    
    // Add password toggle functionality
    initPasswordToggles();
    
    // Initialize plan selection
    initPlanSelection();
    
    // Initialize form validation
    initFormValidation();
    
    /**
     * Initialize multi-step form functionality
     */
    function initMultiStepForm() {
        // Show the first step
        steps[0].classList.add('active');
        stepIndicators[0].classList.add('active');
        
        // Add event listeners to next buttons
        const nextButtons = document.querySelectorAll('.btn-next');
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                if (validateStep(currentStep)) {
                    goToNextStep();
                }
            });
        });
        
        // Add event listeners to previous buttons
        const prevButtons = document.querySelectorAll('.btn-prev');
        prevButtons.forEach(button => {
            button.addEventListener('click', goToPrevStep);
        });
    }
    
    /**
     * Go to the next form step
     */
    function goToNextStep() {
        // Mark current step as completed
        if (stepIndicators[currentStep]) {
            stepIndicators[currentStep].classList.remove('active');
            stepIndicators[currentStep].classList.add('completed');
        }
        
        // Hide current step
        steps[currentStep].classList.remove('active');
        
        // Increment current step
        currentStep++;
        
        // Show next step
        if (currentStep < steps.length) {
            steps[currentStep].classList.add('active');
            if (stepIndicators[currentStep]) {
                stepIndicators[currentStep].classList.add('active');
            }
            
            // Scroll to top of the form
            const form = document.querySelector('.registration-form');
            if (form) {
                form.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
    
    /**
     * Go to the previous form step
     */
    function goToPrevStep() {
        // Hide current step
        steps[currentStep].classList.remove('active');
        
        // Update step indicator
        if (stepIndicators[currentStep]) {
            stepIndicators[currentStep].classList.remove('active');
        }
        
        // Decrement current step
        currentStep--;
        
        // Show previous step
        steps[currentStep].classList.add('active');
        
        // Update step indicator
        if (stepIndicators[currentStep]) {
            stepIndicators[currentStep].classList.remove('completed');
            stepIndicators[currentStep].classList.add('active');
        }
        
        // Scroll to top of the form
        const form = document.querySelector('.registration-form');
        if (form) {
            form.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    /**
     * Validate the current form step
     * @param {number} stepIndex The index of the step to validate
     * @returns {boolean} Whether the step is valid
     */
    function validateStep(stepIndex) {
        const currentStepEl = steps[stepIndex];
        const requiredFields = currentStepEl.querySelectorAll('[required]');
        let isValid = true;
        
        // Check all required fields
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                showError(field, 'This field is required');
            } else {
                clearError(field);
            }
        });
        
        // Validate email fields
        const emailFields = currentStepEl.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value.trim() && !isValidEmail(field.value)) {
                isValid = false;
                showError(field, 'Please enter a valid email address');
            }
        });
        
        // Validate password fields
        const passwordField = currentStepEl.querySelector('#admin_password');
        const confirmPasswordField = currentStepEl.querySelector('#admin_password_confirm');
        
        if (passwordField && confirmPasswordField && 
            passwordField.value && confirmPasswordField.value) {
            
            if (passwordField.value !== confirmPasswordField.value) {
                isValid = false;
                showError(confirmPasswordField, 'Passwords do not match');
            } else if (passwordField.value.length < 8) {
                isValid = false;
                showError(passwordField, 'Password must be at least 8 characters');
            }
        }
        
        return isValid;
    }
    
    /**
     * Show error message for a form field
     * @param {HTMLElement} field The form field
     * @param {string} message The error message
     */
    function showError(field, message) {
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
     * Clear error message for a form field
     * @param {HTMLElement} field The form field
     */
    function clearError(field) {
        field.classList.remove('error');
        
        // Remove error message
        const errorEl = field.nextElementSibling;
        if (errorEl && errorEl.classList.contains('form-error')) {
            errorEl.classList.remove('visible');
        }
    }
    
    /**
     * Validate email format
     * @param {string} email The email to validate
     * @returns {boolean} Whether the email is valid
     */
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
    
    /**
     * Initialize password toggle functionality
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
        // For the plan cards on the registration page
        const planCards = document.querySelectorAll('.plan-card[data-plan]');
        const planInput = document.getElementById('selected_plan');
        
        if (planCards.length > 0 && planInput) {
            // Set the initial selected plan
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
        
        // For plan selection outside registration (e.g., subscription page)
        const planSelectBtns = document.querySelectorAll('.plan-select-btn');
        
        planSelectBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                const plan = this.dataset.plan;
                if (plan) {
                    window.location.href = `/registration/register-company/?plan=${plan}`;
                }
            });
        });
    }
    
    /**
     * Initialize form validation
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('form.registration-form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Validate all steps before submitting
                let isValid = true;
                
                for (let i = 0; i < steps.length; i++) {
                    if (!validateStep(i)) {
                        isValid = false;
                        
                        // Show the invalid step
                        steps.forEach(step => step.classList.remove('active'));
                        steps[i].classList.add('active');
                        
                        // Update step indicators
                        stepIndicators.forEach((indicator, index) => {
                            indicator.classList.remove('active', 'completed');
                            if (index < i) {
                                indicator.classList.add('completed');
                            } else if (index === i) {
                                indicator.classList.add('active');
                            }
                        });
                        
                        // Update current step
                        currentStep = i;
                        
                        break;
                    }
                }
                
                if (!isValid) {
                    e.preventDefault();
                    
                    // Scroll to the top of the form
                    form.scrollIntoView({ behavior: 'smooth' });
                }
            });
            
            // Add input event listeners for real-time validation
            const inputFields = form.querySelectorAll('input, select, textarea');
            
            inputFields.forEach(field => {
                field.addEventListener('input', function() {
                    if (this.value.trim()) {
                        clearError(this);
                    }
                });
                
                field.addEventListener('blur', function() {
                    if (this.hasAttribute('required') && !this.value.trim()) {
                        showError(this, 'This field is required');
                    } else if (this.type === 'email' && this.value.trim() && !isValidEmail(this.value)) {
                        showError(this, 'Please enter a valid email address');
                    } else {
                        clearError(this);
                    }
                });
            });
        });
    }
    
    // Add animation to feature cards on the home page
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0) {
        featureCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + (index * 100));
        });
    }
    
    // Add animation to plan cards
    const pricingCards = document.querySelectorAll('.plan-card:not([data-plan])');
    if (pricingCards.length > 0) {
        pricingCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + (index * 150));
        });
    }
}); 