/**
 * plans.js
 * JavaScript functionality for the subscription plans page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animate plan cards on page load
    const planCards = document.querySelectorAll('.plan-card');
    
    planCards.forEach((card, index) => {
        // Set initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        // Animate each card with a delay based on index
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 150));
        
        // Add click event for plan selection
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on the button directly
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            // Trigger the select button click
            const selectButton = this.querySelector('a.btn');
            if (selectButton) {
                selectButton.click();
            }
        });
    });
    
    // Animate features section
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach((card, index) => {
        // Set initial state
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        // Animate each card with a delay based on index
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 400 + (index * 100)); // Start after plan cards
    });
    
    // FAQ accordion functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        
        // Initially hide answers (if not already hidden in CSS)
        if (answer && !answer.style.display) {
            answer.style.display = 'none';
        }
        
        // Add click event to questions
        if (question) {
            question.addEventListener('click', function() {
                // Toggle answer visibility
                if (answer) {
                    const isVisible = answer.style.display !== 'none';
                    
                    // Hide all answers
                    document.querySelectorAll('.faq-answer').forEach(a => {
                        a.style.display = 'none';
                    });
                    
                    // Remove active class from all questions
                    document.querySelectorAll('.faq-question').forEach(q => {
                        q.classList.remove('active');
                    });
                    
                    // Show this answer if it was hidden
                    if (!isVisible) {
                        answer.style.display = 'block';
                        question.classList.add('active');
                        
                        // Smoothly reveal the answer
                        answer.style.maxHeight = '0';
                        answer.style.overflow = 'hidden';
                        answer.style.transition = 'max-height 0.3s ease';
                        
                        // Use setTimeout to allow the transition to take effect
                        setTimeout(() => {
                            answer.style.maxHeight = answer.scrollHeight + 'px';
                        }, 10);
                    }
                }
            });
        }
    });
    
    // Plan comparison toggle (if present)
    const comparisonToggle = document.getElementById('comparison-toggle');
    const monthlyPrices = document.querySelectorAll('.monthly-price');
    const annualPrices = document.querySelectorAll('.annual-price');
    
    if (comparisonToggle) {
        comparisonToggle.addEventListener('change', function() {
            if (this.checked) {
                // Show annual prices
                monthlyPrices.forEach(el => el.style.display = 'none');
                annualPrices.forEach(el => el.style.display = 'block');
            } else {
                // Show monthly prices
                monthlyPrices.forEach(el => el.style.display = 'block');
                annualPrices.forEach(el => el.style.display = 'none');
            }
        });
    }
    
    // Initialize comparison table tabs (if present)
    const comparisonTabs = document.querySelectorAll('.comparison-tab');
    const comparisonTables = document.querySelectorAll('.comparison-table');
    
    if (comparisonTabs.length > 0 && comparisonTables.length > 0) {
        // Initially show the first table and activate first tab
        comparisonTables[0].style.display = 'block';
        comparisonTabs[0].classList.add('active');
        
        // Add click events to tabs
        comparisonTabs.forEach((tab, index) => {
            tab.addEventListener('click', function() {
                // Hide all tables
                comparisonTables.forEach(table => {
                    table.style.display = 'none';
                });
                
                // Show selected table
                comparisonTables[index].style.display = 'block';
                
                // Update active tab
                comparisonTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
            });
        });
    }
}); 