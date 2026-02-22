document.addEventListener('DOMContentLoaded', function() {
    // Initialize datetime picker
    if (document.getElementById('id_next_follow_up')) {
        const picker = new tempusDominus.TempusDominus(document.getElementById('next_follow_up_picker'), {
            display: {
                icons: {
                    time: 'fas fa-clock',
                    date: 'fas fa-calendar',
                    up: 'fas fa-arrow-up',
                    down: 'fas fa-arrow-down',
                    previous: 'fas fa-chevron-left',
                    next: 'fas fa-chevron-right',
                    today: 'fas fa-calendar-check',
                    clear: 'fas fa-trash',
                    close: 'fas fa-times'
                },
                components: {
                    calendar: true,
                    date: true,
                    month: true,
                    year: true,
                    decades: true,
                    clock: true,
                    hours: true,
                    minutes: true,
                    seconds: false
                },
                buttons: {
                    today: true,
                    clear: true,
                    close: true
                }
            },
            localization: {
                format: 'yyyy-MM-dd HH:mm'
            }
        });
    }

    // Initialize form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Handle activity completion
    const activityCheckboxes = document.querySelectorAll('.activity-checkbox');
    activityCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const activityId = this.dataset.activityId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/leads/activity/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    activity_id: activityId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const activityItem = this.closest('.timeline-item');
                    if (this.checked) {
                        activityItem.classList.add('completed');
                    } else {
                        activityItem.classList.remove('completed');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Handle filter form submission
    const filterForm = document.getElementById('lead-filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const searchParams = new URLSearchParams(formData);
            window.location.href = `${window.location.pathname}?${searchParams.toString()}`;
        });
    }

    // Handle bulk actions
    const selectAllCheckbox = document.getElementById('select-all-leads');
    const bulkActionBtn = document.getElementById('bulk-action-btn');
    const leadCheckboxes = document.querySelectorAll('.lead-checkbox');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            leadCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActionButton();
        });
    }

    leadCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionButton);
    });

    function updateBulkActionButton() {
        const selectedCount = document.querySelectorAll('.lead-checkbox:checked').length;
        if (bulkActionBtn) {
            bulkActionBtn.textContent = `Bulk Actions (${selectedCount})`;
            bulkActionBtn.disabled = selectedCount === 0;
        }
    }

    // Handle bulk delete confirmation
    const bulkDeleteForm = document.getElementById('bulk-delete-form');
    if (bulkDeleteForm) {
        bulkDeleteForm.addEventListener('submit', function(e) {
            const selectedCount = document.querySelectorAll('.lead-checkbox:checked').length;
            if (!confirm(`Are you sure you want to delete ${selectedCount} leads? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    }

    // Initialize charts if elements exist
    const statusChartEl = document.getElementById('leadStatusChart');
    if (statusChartEl) {
        const ctx = statusChartEl.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: JSON.parse(statusChartEl.dataset.labels),
                datasets: [{
                    data: JSON.parse(statusChartEl.dataset.values),
                    backgroundColor: [
                        '#4e73df',  // New
                        '#1cc88a',  // Contacted
                        '#f6c23e',  // Qualified
                        '#e74a3b',  // Lost
                        '#36b9cc'   // Won
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    const sourceChartEl = document.getElementById('leadSourceChart');
    if (sourceChartEl) {
        const ctx = sourceChartEl.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: JSON.parse(sourceChartEl.dataset.labels),
                datasets: [{
                    label: 'Leads by Source',
                    data: JSON.parse(sourceChartEl.dataset.values),
                    backgroundColor: '#4e73df',
                    borderWidth: 1
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
});