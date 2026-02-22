document.addEventListener('DOMContentLoaded', function() {
    const avatar = document.getElementById('avatar');
    const preview = document.querySelector('.avatar-preview');
    const nameInput = document.getElementById('name');
    const pinInput = document.getElementById('pin');
    const pinConfirmInput = document.getElementById('pin_confirm');
    const form = document.querySelector('form');
    
    // Avatar preview
    avatar.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Avatar preview">`;
            }
            reader.readAsDataURL(this.files[0]);
        }
    });

    // Name validation
    const restrictedNames = ['admin', 'administrator', 'owner'];
    
    nameInput.addEventListener('input', function() {
        const name = this.value.toLowerCase();
        const errorDiv = document.getElementById('name-error');
        
        if (restrictedNames.includes(name)) {
            errorDiv.textContent = 'This profile name is not allowed';
            this.setCustomValidity('This profile name is not allowed');
        } else {
            errorDiv.textContent = '';
            this.setCustomValidity('');
        }
    });

    // PIN validation
    function isWeakPin(pin) {
        // Check for repeated digits (0000, 1111, etc.)
        if (/^(.)\1{3}$/.test(pin)) return true;
        
        // Check for sequential numbers (1234, 4321, etc.)
        const sequential = '01234567890';
        const reverseSequential = '09876543210';
        if (sequential.includes(pin) || reverseSequential.includes(pin)) return true;
        
        return false;
    }

    pinInput.addEventListener('input', function() {
        const pin = this.value;
        const errorDiv = document.getElementById('pin-error');
        
        if (pin.length === 4) {
            if (isWeakPin(pin)) {
                errorDiv.textContent = 'PIN cannot be sequential or repeated numbers';
                this.setCustomValidity('Please choose a stronger PIN');
            } else {
                errorDiv.textContent = '';
                this.setCustomValidity('');
            }
        }
    });

    // PIN confirmation
    pinConfirmInput.addEventListener('input', function() {
        const pin = pinInput.value;
        const confirmPin = this.value;
        const errorDiv = document.getElementById('pin-confirm-error');
        
        if (confirmPin.length === 4) {
            if (pin !== confirmPin) {
                errorDiv.textContent = 'PINs do not match';
                this.setCustomValidity('PINs must match');
            } else {
                errorDiv.textContent = '';
                this.setCustomValidity('');
            }
        }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        const pin = pinInput.value;
        const confirmPin = pinConfirmInput.value;
        
        if (pin !== confirmPin) {
            e.preventDefault();
            document.getElementById('pin-confirm-error').textContent = 'PINs do not match';
            return;
        }
        
        if (isWeakPin(pin)) {
            e.preventDefault();
            document.getElementById('pin-error').textContent = 'Please choose a stronger PIN';
            return;
        }
    });
}); 