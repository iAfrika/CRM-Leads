// Site Admin JavaScript

$(document).ready(function() {
    // Toggle sidebar collapse
    $('.sidebar-toggle').on('click', function() {
        $('.admin-layout').toggleClass('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', $('.admin-layout').hasClass('sidebar-collapsed'));
    });
    
    // Check if sidebar was collapsed in previous session
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        $('.admin-layout').addClass('sidebar-collapsed');
    }
    
    // Mobile sidebar toggle
    $('.mobile-sidebar-toggle').on('click', function() {
        $('.admin-layout').toggleClass('mobile-sidebar-open');
    });
    
    // Close alerts
    $(document).on('click', '.alert .close', function() {
        $(this).closest('.alert').remove();
    });
    
    // User dropdown toggle
    $('.user-dropdown-toggle').on('click', function(e) {
        e.stopPropagation();
        $('.user-dropdown-menu').toggleClass('show');
    });
    
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.user-dropdown').length) {
            $('.user-dropdown-menu').removeClass('show');
        }
    });
    
    // Dark mode toggle
    $('.dark-mode-toggle').on('click', function() {
        $('html').toggleClass('dark-mode');
        localStorage.setItem('darkMode', $('html').hasClass('dark-mode'));
        updateDarkModeIcon();
    });
    
    // Check if dark mode was enabled in previous session
    function initDarkMode() {
        if (localStorage.getItem('darkMode') === 'true') {
            $('html').addClass('dark-mode');
        } else if (localStorage.getItem('darkMode') === null) {
            // Check for system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                $('html').addClass('dark-mode');
                localStorage.setItem('darkMode', 'true');
            }
        }
        updateDarkModeIcon();
    }
    
    function updateDarkModeIcon() {
        if ($('html').hasClass('dark-mode')) {
            $('.dark-mode-toggle i').removeClass('fa-moon').addClass('fa-sun');
        } else {
            $('.dark-mode-toggle i').removeClass('fa-sun').addClass('fa-moon');
        }
    }
    
    // Initialize
    initDarkMode();
    
    // Listen for system preference changes
    if (window.matchMedia) {
        const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        colorSchemeQuery.addEventListener('change', (e) => {
            // Only apply if user hasn't manually set a preference
            if (localStorage.getItem('darkMode') === null) {
                if (e.matches) {
                    $('html').addClass('dark-mode');
                } else {
                    $('html').removeClass('dark-mode');
                }
                updateDarkModeIcon();
            }
        });
    }
    
    // Handle inline forms deletion
    $(document).on('click', '.delete-inline-item', function(e) {
        e.preventDefault();
        var $form = $(this).closest('.inline-form');
        $form.toggleClass('marked-for-deletion');
        var $deleteInput = $form.find('input[name$="-DELETE"]');
        $deleteInput.prop('checked', $form.hasClass('marked-for-deletion'));
        
        if ($form.hasClass('marked-for-deletion')) {
            $(this).html('<i class="fas fa-undo"></i>');
            $(this).attr('title', 'Restore');
        } else {
            $(this).html('<i class="fas fa-trash"></i>');
            $(this).attr('title', 'Delete');
        }
    });
}); 