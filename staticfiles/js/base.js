// Common JavaScript functionality for the entire CRM Leads application

$(document).ready(function() {
    // ======= DARK MODE FUNCTIONALITY =======
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        const toggleDarkMode = function(isDark) {
            // Apply dark mode class to the html element
            document.documentElement.classList.toggle('dark-mode', isDark);
            
            // Update icon
            const icon = darkModeToggle.querySelector('i');
            if (icon) {
                if (isDark) {
                    icon.classList.remove('fa-moon');
                    icon.classList.add('fa-sun');
                } else {
                    icon.classList.remove('fa-sun');
                    icon.classList.add('fa-moon');
                }
            }
            
            // Store preference
            localStorage.setItem('crm_leads_dark_mode', isDark);
            
            // Log for debugging
            console.log('Dark mode toggled:', isDark);
            
            // Update Chart.js configurations if it exists
            updateChartsForDarkMode(isDark);
            
            // Dispatch custom event for other scripts that might need to know about theme changes
            document.dispatchEvent(new CustomEvent('themeChanged', { detail: { isDarkMode: isDark } }));
        };
        
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const isDarkMode = !document.documentElement.classList.contains('dark-mode');
            toggleDarkMode(isDarkMode);
        });
        
        // Apply dark mode based on saved preference or system preference
        const savedDarkMode = localStorage.getItem('crm_leads_dark_mode');
        if (savedDarkMode !== null) {
            toggleDarkMode(savedDarkMode === 'true');
        } else {
            // Check system preference if no saved preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            toggleDarkMode(prefersDark);
        }
        
        // Listen for system preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem('crm_leads_dark_mode') === null) {
                toggleDarkMode(e.matches);
            }
        });
    }
    
    // Function to update Chart.js theme if it exists
    function updateChartsForDarkMode(isDark) {
        if (window.Chart) {
            // Update Chart.js default configuration
            const chartColors = isDark ? {
                backgroundColor: 'rgba(54, 57, 63, 0.5)',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                gridColor: 'rgba(255, 255, 255, 0.1)',
                textColor: '#e9ecef'
            } : {
                backgroundColor: 'rgba(255, 255, 255, 0.5)',
                borderColor: 'rgba(0, 0, 0, 0.1)',
                gridColor: 'rgba(0, 0, 0, 0.1)',
                textColor: '#666'
            };
            
            Chart.defaults.global.defaultFontColor = chartColors.textColor;
            Chart.defaults.scale.gridLines.color = chartColors.gridColor;
            
            // Update all existing charts
            if (Chart.instances) {
                Object.values(Chart.instances).forEach(chart => {
                    chart.options.legend.labels.fontColor = chartColors.textColor;
                    chart.options.scales.xAxes.forEach(axis => {
                        axis.gridLines.color = chartColors.gridColor;
                        axis.ticks.fontColor = chartColors.textColor;
                    });
                    chart.options.scales.yAxes.forEach(axis => {
                        axis.gridLines.color = chartColors.gridColor;
                        axis.ticks.fontColor = chartColors.textColor;
                    });
                    chart.update();
                });
            }
        }
        
        // Update DataTables theme if it exists
        if ($.fn.dataTable) {
            $('.dataTable').each(function() {
                $(this).DataTable().draw();
            });
        }
    }
    
    // ======= USER DROPDOWN FUNCTIONALITY =======
    const userDropdown = document.querySelector('.user-dropdown');
    const userDropdownToggle = document.querySelector('.user-dropdown-toggle');
    
    if (userDropdown && userDropdownToggle) {
        userDropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            userDropdown.classList.toggle('open');
            
            // Log for debugging
            console.log('User dropdown clicked', userDropdown.classList.contains('open'));
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target)) {
                userDropdown.classList.remove('open');
            }
        });
    }
    
    // ======= SIDEBAR FUNCTIONALITY =======
    // Sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.app-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebarToggle && sidebar && overlay) {
        // Load saved state
        const sidebarCollapsed = localStorage.getItem('crm_leads_sidebar_collapsed') === 'true';
        if (sidebarCollapsed) {
            document.body.classList.add('sidebar-collapsed');
        }
        
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            
            // Save state to localStorage
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('crm_leads_sidebar_collapsed', isCollapsed);
            
            console.log('Sidebar toggled, collapsed:', isCollapsed);
        });
        
        // Mobile sidebar toggle
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // ======= ORIGINAL FUNCTIONALITY =======
    // Sidebar toggle (jQuery version for backward compatibility)
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar').toggleClass('active');
    });

    // Close sidebar on mobile when clicking outside
    $(document).on('click', function(e) {
        if ($(window).width() <= 768) {
            if (!$(e.target).closest('#sidebar, #sidebarCollapse').length) {
                $('#sidebar').addClass('active');
            }
        }
    });

    // Auto-hide alerts after 5 seconds
    $('.alert').delay(5000).fadeOut(500);

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Handle delete confirmations
    $('.delete-confirm').on('click', function(e) {
        e.preventDefault();
        if (confirm('Are you sure you want to delete this item?')) {
            let form = $(this).closest('form');
            let url = form.attr('action');
            
            $.ajax({
                url: url,
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    }
                },
                error: function(xhr, errmsg, err) {
                    console.log(xhr.status + ": " + xhr.responseText);
                }
            });
        }
    });

    // Handle form submissions with AJAX
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        let form = $(this);
        let url = form.attr('action');
        
        $.ajax({
            url: url,
            type: 'POST',
            data: form.serialize(),
            success: function(response) {
                if (response.status === 'success') {
                    location.reload();
                } else {
                    // Handle validation errors
                    let errors = response.errors;
                    for (let field in errors) {
                        let input = form.find('[name=' + field + ']');
                        input.addClass('is-invalid');
                        input.next('.invalid-feedback').text(errors[field][0]);
                    }
                }
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    });

    // Clear form validation on input
    $('form input, form select, form textarea').on('input', function() {
        $(this).removeClass('is-invalid');
        $(this).next('.invalid-feedback').text('');
    });
});
