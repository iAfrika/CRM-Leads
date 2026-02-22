document.addEventListener('DOMContentLoaded', function() {
    const pinDisplay = document.getElementById('pin-display');
    const keypadButtons = document.querySelectorAll('.keypad-btn');
    const togglePassword = document.querySelector('.toggle-password');
    const form = document.querySelector('.pin-form');
    
    function updatePin(value) {
        if (pinDisplay.value.length < 4) {
            pinDisplay.value += value;
        }
        if (pinDisplay.value.length === 4) {
            form.submit();
        }
    }

    function clearPin() {
        pinDisplay.value = '';
    }

    // Handle keypad button clicks
    keypadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (this.classList.contains('clear-btn')) {
                clearPin();
            } else if (!this.classList.contains('enter-btn')) {
                updatePin(this.dataset.value);
            }
        });
    });

    // Prevent the input from accepting direct keyboard input
    pinDisplay.addEventListener('input', function(e) {
        e.preventDefault();
        pinDisplay.value = pinDisplay.value.slice(0, -1); // Remove the last character
    });

    // Handle keyboard input globally
    document.addEventListener('keydown', function(e) {
        if (e.key >= '0' && e.key <= '9') {
            e.preventDefault(); // Prevent default to avoid double input
            updatePin(e.key);
        } else if (e.key === 'Backspace') {
            e.preventDefault();
            pinDisplay.value = pinDisplay.value.slice(0, -1);
        } else if (e.key === 'Enter' && pinDisplay.value.length === 4) {
            e.preventDefault();
            form.submit();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            clearPin();
        }
    });

    // Toggle password visibility
    togglePassword.addEventListener('click', function(e) {
        e.preventDefault();
        const type = pinDisplay.getAttribute('type') === 'password' ? 'text' : 'password';
        pinDisplay.setAttribute('type', type);
        
        // Update icon
        const path = this.querySelector('path');
        if (type === 'password') {
            path.setAttribute('d', 'M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24');
        } else {
            path.setAttribute('d', 'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z');
        }
    });

    // Auto-focus the PIN input
    pinDisplay.focus();

    // Clear messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-10px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 