document.addEventListener('DOMContentLoaded', function () {
    // Monthly Expenses Chart
    const monthlyCtx = document.getElementById('monthlyExpensesChart').getContext('2d');
    new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: [{% for expense in monthly_expenses %}'{{ expense.month|date:"M Y" }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Monthly Expenses',
                data: [{% for expense in monthly_expenses %}{{ expense.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                borderColor: '#2563eb',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Weekly Expenses Chart
    const weeklyCtx = document.getElementById('weeklyExpensesChart').getContext('2d');
    new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: [{% for week in weekly_expenses %}'Week {{ week.week_number }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Weekly Expenses',
                data: [{% for week in weekly_expenses %}{{ week.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                backgroundColor: '#34d399',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Expenses by Category Chart
    const categoryCtx = document.getElementById('categoryExpensesChart').getContext('2d');
    new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: [{% for expense in category_expenses %}'{{ expense.category__name }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                data: [{% for expense in category_expenses %}{{ expense.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                backgroundColor: [
                    '#2563eb',
                    '#7c3aed',
                    '#db2777',
                    '#dc2626',
                    '#d97706',
                    '#059669',
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // Expenses by Volume Chart
    const volumeCtx = document.getElementById('volumeExpensesChart').getContext('2d');
    new Chart(volumeCtx, {
        type: 'bar',
        data: {
            labels: [{% for volume in volume_expenses %}'{{ volume.category }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Expenses by Volume',
                data: [{% for volume in volume_expenses %}{{ volume.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                backgroundColor: '#fbbf24',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Yearly Expense Overview Chart
    const yearlyCtx = document.getElementById('yearlyExpensesChart').getContext('2d');
    new Chart(yearlyCtx, {
        type: 'line',
        data: {
            labels: [{% for year in yearly_expenses %}'{{ year.year }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Yearly Expenses',
                data: [{% for year in yearly_expenses %}{{ year.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                borderColor: '#ff6347',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Expense Distribution by Payment Method Chart
    const paymentMethodCtx = document.getElementById('paymentMethodChart').getContext('2d');
    new Chart(paymentMethodCtx, {
        type: 'pie',
        data: {
            labels: [{% for method in payment_method_expenses %}'{{ method.payment_method }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                data: [{% for method in payment_method_expenses %}{{ method.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                backgroundColor: [
                    '#4f46e5',
                    '#fbbf24',
                    '#ef4444',
                    '#34d399',
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Top 5 Expense Categories Chart
    const topCategoriesCtx = document.getElementById('topCategoriesChart').getContext('2d');
    new Chart(topCategoriesCtx, {
        type: 'bar',
        data: {
            labels: [{% for category in top_categories %}'{{ category.name }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Top 5 Expense Categories',
                data: [{% for category in top_categories %}{{ category.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                backgroundColor: '#2563eb',
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Monthly Average Expenses Chart
    const averageExpensesCtx = document.getElementById('averageExpensesChart').getContext('2d');
    new Chart(averageExpensesCtx, {
        type: 'line',
        data: {
            labels: [{% for month in average_expenses %}'{{ month.month|date:"M Y" }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Average Monthly Expenses',
                data: [{% for month in average_expenses %}{{ month.average }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                borderColor: '#34d399',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Cumulative Expenses Over Time Chart
    const cumulativeExpensesCtx = document.getElementById('cumulativeExpensesChart').getContext('2d');
    new Chart(cumulativeExpensesCtx, {
        type: 'line',
        data: {
            labels: [{% for date in cumulative_expenses %}'{{ date.date|date:"M d, Y" }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Cumulative Expenses',
                data: [{% for date in cumulative_expenses %}{{ date.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                borderColor: '#fbbf24',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Budget vs. Actual Expenses Chart
    const budgetVsActualCtx = document.getElementById('budgetVsActualChart').getContext('2d');
    new Chart(budgetVsActualCtx, {
        type: 'bar',
        data: {
            labels: ['Budget', 'Actual'],
            datasets: [{
                label: 'Expenses',
                data: [{{ budget_amount }}, {{ actual_amount }}],
                backgroundColor: ['#4f46e5', '#34d399'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Recurring vs. One-Time Expenses Chart
    const recurringVsOneTimeCtx = document.getElementById('recurringVsOneTimeChart').getContext('2d');
    new Chart(recurringVsOneTimeCtx, {
        type: 'bar',
        data: {
            labels: ['Recurring', 'One-Time'],
            datasets: [{
                label: 'Expenses',
                data: [{{ recurring_expenses_total }}, {{ one_time_expenses_total }}],
                backgroundColor: ['#2563eb', '#fbbf24'],
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    // Expense Heatmap Chart
    const expenseHeatmapCtx = document.getElementById('expenseHeatmapChart').getContext('2d');
    // Implement heatmap logic here (requires additional library or custom implementation)

    // Savings Over Time Chart
    const savingsCtx = document.getElementById('savingsChart').getContext('2d');
    new Chart(savingsCtx, {
        type: 'line',
        data: {
            labels: [{% for month in savings_data %}'{{ month.date|date:"M Y" }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: 'Savings Over Time',
                data: [{% for month in savings_data %}{{ month.savings }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                borderColor: '#34d399',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}); 