/**
 * Navigation JavaScript - Handles sidebar toggle and responsive behavior
 */
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
        });
    }
    
    // Handle responsive design
    function checkWidth() {
        if (window.innerWidth < 768) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        } else {
            sidebar.classList.remove('collapsed');
            content.classList.remove('expanded');
        }
    }
    
    // Initial check
    checkWidth();
    
    // Listen for window resize
    window.addEventListener('resize', checkWidth);

    // Dropdown functionality for profile menu
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            dropdownMenu.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    }

    // Banking link styling
    const bankingLink = document.querySelector('.banking-link');
    if (bankingLink) {
        bankingLink.style.display = 'flex';
    }
}); 