document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from cookie
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

    // Handle project deletion
    document.querySelectorAll('form[action*="project_delete"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (confirm('Are you sure you want to delete this project?')) {
                const csrftoken = getCookie('csrftoken');
                
                fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams(new FormData(this))
                })
                .then(response => {
                    if (response.ok) {
                        // Remove the project card from the UI
                        const projectCard = this.closest('.project');
                        projectCard.remove();

                        // Check if there are any projects left
                        const projectGrid = document.querySelector('.project-grid');
                        if (!projectGrid.querySelector('.project')) {
                            // Show empty state message
                            const emptyState = document.createElement('div');
                            emptyState.className = 'empty-state';
                            emptyState.innerHTML = '<p>No projects found. Create your first project to get started!</p>';
                            projectGrid.appendChild(emptyState);
                        }
                    } else {
                        throw new Error('Failed to delete project');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed to delete the project. Please try again.');
                });
            }
        });
    });
});