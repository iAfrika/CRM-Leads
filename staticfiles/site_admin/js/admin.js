/**
 * Site Admin JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const adminLayout = document.querySelector('.admin-layout');
    
    if (sidebarToggle && adminLayout) {
        sidebarToggle.addEventListener('click', function() {
            adminLayout.classList.toggle('sidebar-collapsed');
            
            // Store the sidebar state in localStorage
            const isSidebarCollapsed = adminLayout.classList.contains('sidebar-collapsed');
            localStorage.setItem('site_admin_sidebar_collapsed', isSidebarCollapsed);
        });
        
        // Restore sidebar state from localStorage
        const isSidebarCollapsed = localStorage.getItem('site_admin_sidebar_collapsed') === 'true';
        if (isSidebarCollapsed) {
            adminLayout.classList.add('sidebar-collapsed');
        }
    }
    
    // Table row hover effects
    const dataTableRows = document.querySelectorAll('.data-table tbody tr');
    dataTableRows.forEach(row => {
        row.addEventListener('mouseover', function() {
            this.style.backgroundColor = 'rgba(44, 62, 80, 0.1)';
        });
        
        row.addEventListener('mouseout', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Custom file input styling
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const fileLabel = document.createElement('label');
        fileLabel.classList.add('custom-file-label');
        fileLabel.textContent = 'Choose file';
        
        const fileWrapper = document.createElement('div');
        fileWrapper.classList.add('custom-file');
        
        // Insert the wrapper
        input.parentNode.insertBefore(fileWrapper, input);
        fileWrapper.appendChild(input);
        fileWrapper.appendChild(fileLabel);
        
        // Update label text when file is selected
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Choose file';
            }
        });
    });
    
    // Confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation
    const adminForms = document.querySelectorAll('.site-admin-form');
    adminForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    const fieldParent = field.closest('.form-field');
                    
                    if (fieldParent) {
                        fieldParent.classList.add('has-error');
                        
                        // Create error message if it doesn't exist
                        if (!fieldParent.querySelector('.error-message')) {
                            const errorMsg = document.createElement('div');
                            errorMsg.classList.add('error-message');
                            errorMsg.textContent = 'This field is required.';
                            fieldParent.appendChild(errorMsg);
                        }
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.has-error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
        
        // Clear error on input
        const formInputs = form.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            input.addEventListener('input', function() {
                const fieldParent = this.closest('.form-field');
                if (fieldParent && fieldParent.classList.contains('has-error')) {
                    fieldParent.classList.remove('has-error');
                    
                    const errorMsg = fieldParent.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
        });
    });
    
    // Mobile sidebar toggle
    const mobileToggle = document.querySelector('.mobile-sidebar-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            document.body.classList.toggle('mobile-sidebar-open');
        });
    }
    
    // Initialize any tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseover', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            
            if (tooltipText) {
                const tooltipEl = document.createElement('div');
                tooltipEl.classList.add('tooltip');
                tooltipEl.textContent = tooltipText;
                
                document.body.appendChild(tooltipEl);
                
                const rect = this.getBoundingClientRect();
                tooltipEl.style.top = (rect.top - tooltipEl.offsetHeight - 10) + 'px';
                tooltipEl.style.left = (rect.left + (rect.width / 2) - (tooltipEl.offsetWidth / 2)) + 'px';
                
                this.addEventListener('mouseout', function() {
                    tooltipEl.remove();
                }, { once: true });
            }
        });
    });
    
    // Dismissible alerts
    const alertCloseButtons = document.querySelectorAll('.alert .close');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
    
    // Enhanced search functionality
    const searchForms = document.querySelectorAll('.search-form');
    searchForms.forEach(form => {
        const searchInput = form.querySelector('.search-input');
        const clearButton = form.querySelector('.search-clear');
        
        if (searchInput && clearButton) {
            // Show clear button only when there's text
            searchInput.addEventListener('input', function() {
                if (this.value.trim()) {
                    clearButton.style.display = 'block';
                } else {
                    clearButton.style.display = 'none';
                }
            });
            
            // Initialize on page load
            if (searchInput.value.trim()) {
                clearButton.style.display = 'block';
            } else {
                clearButton.style.display = 'none';
            }
            
            // Clear search
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                this.style.display = 'none';
                form.submit();
            });
        }
    });
    
    // Dark mode toggle
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
            localStorage.setItem('site_admin_dark_mode', isDark);
            
            // Log for debugging
            console.log('Dark mode toggled:', isDark);
        };
        
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const isDarkMode = !document.documentElement.classList.contains('dark-mode');
            toggleDarkMode(isDarkMode);
        });
        
        // Apply dark mode based on saved preference or system preference
        const savedDarkMode = localStorage.getItem('site_admin_dark_mode');
        if (savedDarkMode !== null) {
            toggleDarkMode(savedDarkMode === 'true');
        } else {
            // Check system preference if no saved preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            toggleDarkMode(prefersDark);
        }
        
        // Listen for system preference changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (localStorage.getItem('site_admin_dark_mode') === null) {
                toggleDarkMode(e.matches);
            }
        });
    }
    
    // User dropdown menu
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
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea.auto-resize');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Initialize on page load
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    });
    
    // Filter panel toggle
    const filterToggleBtn = document.querySelector('.filter-toggle-btn');
    const filterPanel = document.querySelector('.filter-panel');
    
    if (filterToggleBtn && filterPanel) {
        filterToggleBtn.addEventListener('click', function() {
            filterPanel.classList.toggle('show');
            
            // Update button text
            const isVisible = filterPanel.classList.contains('show');
            this.querySelector('.filter-toggle-text').textContent = isVisible ? 'Hide Filters' : 'Show Filters';
            
            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-chevron-up', isVisible);
                icon.classList.toggle('fa-chevron-down', !isVisible);
            }
        });
    }
    
    // Filter navigation toggle (for mobile)
    const filterToggleBtnNav = document.querySelector('.filter-toggle-nav');
    const filterPanelNav = document.querySelector('.filters-nav');
    
    if (filterToggleBtnNav && filterPanelNav) {
        filterToggleBtnNav.addEventListener('click', function() {
            filterPanelNav.classList.toggle('show');
            
            // Save state in localStorage
            const isVisible = filterPanelNav.classList.contains('show');
            localStorage.setItem('site_admin_filters_visible', isVisible);
            
            // Update button text
            this.querySelector('.filter-toggle-text').textContent = isVisible ? 'Hide' : 'Filters';
            
            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-chevron-up', isVisible);
                icon.classList.toggle('fa-chevron-down', !isVisible);
            }
        });
        
        // Restore state from localStorage
        const filtersVisible = localStorage.getItem('site_admin_filters_visible') === 'true';
        if (filtersVisible) {
            filterPanelNav.classList.add('show');
            filterToggleBtnNav.querySelector('.filter-toggle-text').textContent = 'Hide';
            const icon = filterToggleBtnNav.querySelector('i');
            if (icon) {
                icon.classList.add('fa-chevron-up');
                icon.classList.remove('fa-chevron-down');
            }
        }
    }
    
    // Clear button for search input
    const toggleClearButton = function() {
        const searchInput = document.querySelector('.filter-search-input');
        const clearButton = document.querySelector('.filter-search-clear');
        
        if (searchInput && clearButton) {
            if (searchInput.value.trim()) {
                clearButton.style.display = 'block';
            } else {
                clearButton.style.display = 'none';
            }
        }
    };
    
    const searchInput = document.querySelector('.filter-search-input');
    const clearButton = document.querySelector('.filter-search-clear');
    
    if (searchInput && clearButton) {
        // Initial state
        toggleClearButton();
        
        // Update on input
        searchInput.addEventListener('input', toggleClearButton);
        
        // Clear search
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            toggleClearButton();
            const searchForm = searchInput.closest('form');
            if (searchForm) {
                searchForm.submit();
            }
        });
    }
});
