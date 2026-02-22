/**
 * home.js
 * JavaScript functionality for the registration home page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Animate the hero section
    animateHero();
    
    // Animate the feature cards
    animateFeatureCards();
    
    // Initialize the steps section
    initStepsSection();
    
    // Initialize testimonials carousel
    initTestimonialsCarousel();
    
    /**
     * Animate the hero section with a fade-in effect
     */
    function animateHero() {
        const heroTitle = document.querySelector('.hero-title');
        const heroSubtitle = document.querySelector('.hero-subtitle');
        
        if (heroTitle) {
            heroTitle.style.opacity = '0';
            heroTitle.style.transform = 'translateY(20px)';
            heroTitle.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            
            setTimeout(() => {
                heroTitle.style.opacity = '1';
                heroTitle.style.transform = 'translateY(0)';
            }, 100);
        }
        
        if (heroSubtitle) {
            heroSubtitle.style.opacity = '0';
            heroSubtitle.style.transform = 'translateY(20px)';
            heroSubtitle.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            
            setTimeout(() => {
                heroSubtitle.style.opacity = '1';
                heroSubtitle.style.transform = 'translateY(0)';
            }, 300);
        }
    }
    
    /**
     * Animate the feature cards with a staggered fade-in effect
     */
    function animateFeatureCards() {
        const featureCards = document.querySelectorAll('.feature-card');
        
        featureCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 500 + (index * 100));
            
            // Add hover effect
            card.addEventListener('mouseenter', function() {
                const icon = this.querySelector('.feature-icon');
                if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(5deg)';
                    icon.style.transition = 'transform 0.3s ease';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                const icon = this.querySelector('.feature-icon');
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0)';
                }
            });
        });
    }
    
    /**
     * Initialize the steps section with interactive features
     */
    function initStepsSection() {
        const steps = document.querySelectorAll('.step');
        
        steps.forEach((step, index) => {
            // Add click event to each step
            step.addEventListener('click', function() {
                // Update the step circle to reflect a completed state
                if (!this.classList.contains('completed')) {
                    for (let i = 0; i < steps.length; i++) {
                        if (i < index) {
                            steps[i].classList.add('completed');
                        } else {
                            steps[i].classList.remove('completed');
                        }
                    }
                    
                    this.classList.add('active');
                    
                    // Remove active class from other steps
                    steps.forEach((s, i) => {
                        if (i !== index) {
                            s.classList.remove('active');
                        }
                    });
                }
            });
        });
    }
    
    /**
     * Initialize a simple testimonials carousel
     */
    function initTestimonialsCarousel() {
        const testimonials = document.querySelectorAll('.testimonial-card');
        if (testimonials.length <= 1) return;
        
        let currentIndex = 0;
        const interval = 5000; // Change testimonial every 5 seconds
        
        // Initially hide all but the first testimonial
        testimonials.forEach((testimonial, index) => {
            if (index > 0) {
                testimonial.style.display = 'none';
            }
        });
        
        // Function to show the next testimonial
        function showNextTestimonial() {
            // Hide current testimonial
            testimonials[currentIndex].style.display = 'none';
            
            // Update index
            currentIndex = (currentIndex + 1) % testimonials.length;
            
            // Show next testimonial
            testimonials[currentIndex].style.display = 'block';
            testimonials[currentIndex].style.opacity = '0';
            testimonials[currentIndex].style.transform = 'translateY(10px)';
            
            // Animate in
            setTimeout(() => {
                testimonials[currentIndex].style.opacity = '1';
                testimonials[currentIndex].style.transform = 'translateY(0)';
                testimonials[currentIndex].style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            }, 50);
        }
        
        // Set interval for automatic carousel
        setInterval(showNextTestimonial, interval);
        
        // Add manual navigation (optional)
        const testimonialsContainer = testimonials[0].parentNode;
        if (testimonialsContainer) {
            // Create navigation dots
            const dotsContainer = document.createElement('div');
            dotsContainer.className = 'testimonial-dots';
            dotsContainer.style.display = 'flex';
            dotsContainer.style.justifyContent = 'center';
            dotsContainer.style.gap = '0.5rem';
            dotsContainer.style.marginTop = '1rem';
            
            for (let i = 0; i < testimonials.length; i++) {
                const dot = document.createElement('button');
                dot.className = 'testimonial-dot';
                dot.style.width = '10px';
                dot.style.height = '10px';
                dot.style.borderRadius = '50%';
                dot.style.border = 'none';
                dot.style.backgroundColor = i === 0 ? 'var(--primary-color)' : '#e5e7eb';
                dot.style.cursor = 'pointer';
                dot.style.transition = 'background-color 0.3s ease';
                
                dot.addEventListener('click', function() {
                    // Hide current testimonial
                    testimonials[currentIndex].style.display = 'none';
                    
                    // Update index
                    currentIndex = i;
                    
                    // Show selected testimonial
                    testimonials[currentIndex].style.display = 'block';
                    testimonials[currentIndex].style.opacity = '0';
                    testimonials[currentIndex].style.transform = 'translateY(10px)';
                    
                    // Animate in
                    setTimeout(() => {
                        testimonials[currentIndex].style.opacity = '1';
                        testimonials[currentIndex].style.transform = 'translateY(0)';
                    }, 50);
                    
                    // Update dots
                    dotsContainer.querySelectorAll('.testimonial-dot').forEach((d, idx) => {
                        d.style.backgroundColor = idx === i ? 'var(--primary-color)' : '#e5e7eb';
                    });
                });
                
                dotsContainer.appendChild(dot);
            }
            
            testimonialsContainer.appendChild(dotsContainer);
        }
    }
}); 