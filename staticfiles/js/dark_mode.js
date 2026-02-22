document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    
    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('crm_leads_dark_mode');
    if (savedTheme === 'true') {
        html.classList.add('dark-mode');
    }

    // Theme toggle functionality
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            const isDarkMode = html.classList.toggle('dark-mode');
            localStorage.setItem('crm_leads_dark_mode', isDarkMode);
            
            // Optional: Send theme preference to server
            fetch('/update-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ theme: isDarkMode ? 'dark' : 'light' })
            });
        });
    }

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
