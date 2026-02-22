document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.expense-form');
    const fileInput = document.querySelector('input[type="file"]');
    
    // File upload preview
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const filePreview = document.querySelector('.selected-file');
            if (file) {
                filePreview.innerHTML = `
                    <i class="fas fa-file"></i>
                    <span>${file.name}</span>
                `;
                filePreview.style.display = 'flex';
            }
        });
    }
    
    // Form validation
    if (form) {
        form.addEventListener('submit', function(e) {
            // Add your form validation logic here
        });
    }
}); 