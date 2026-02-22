document.addEventListener('DOMContentLoaded', function() {
    // Register Chart.js plugins
    Chart.register(ChartDataLabels);
    
    // Get data from the hidden div
    const reportData = document.querySelector('.report-data');
    if (!reportData) return;
    
    // Parse JSON data
    const categories = JSON.parse(reportData.dataset.categories || '[]');
    const categoryAmounts = JSON.parse(reportData.dataset.categoryAmounts || '[]');
    const months = JSON.parse(reportData.dataset.months || '[]');
    const monthlyAmounts = JSON.parse(reportData.dataset.monthlyAmounts || '[]');
    const paymentMethods = JSON.parse(reportData.dataset.paymentMethods || '[]');
    const paymentMethodAmounts = JSON.parse(reportData.dataset.paymentMethodAmounts || '[]');
    const statuses = JSON.parse(reportData.dataset.statuses || '[]');
    const statusAmounts = JSON.parse(reportData.dataset.statusAmounts || '[]');
    
    // Calculate growth rate
    const previousTotal = parseFloat(reportData.dataset.previousTotal || '0');
    const currentTotal = parseFloat(reportData.dataset.currentTotal || '0');
    let growthRate = 0;
    
    if (previousTotal > 0) {
        growthRate = ((currentTotal - previousTotal) / previousTotal) * 100;
    }
    
    const growthRateElement = document.getElementById('growth-rate');
    if (growthRateElement) {
        const formattedGrowthRate = growthRate.toFixed(1) + '%';
        growthRateElement.textContent = formattedGrowthRate;
        
        if (growthRate > 0) {
            growthRateElement.classList.add('positive-growth');
            growthRateElement.innerHTML = `<i class="fas fa-arrow-up"></i> ${formattedGrowthRate}`;
        } else if (growthRate < 0) {
            growthRateElement.classList.add('negative-growth');
            growthRateElement.innerHTML = `<i class="fas fa-arrow-down"></i> ${formattedGrowthRate}`;
        } else {
            growthRateElement.innerHTML = `${formattedGrowthRate}`;
        }
    }
    
    // Generate random colors for charts
    function generateColors(count) {
        const colors = [
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 99, 132, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(255, 159, 64, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 205, 86, 0.7)',
            'rgba(201, 203, 207, 0.7)',
            'rgba(255, 99, 71, 0.7)',
            'rgba(46, 204, 113, 0.7)',
            'rgba(142, 68, 173, 0.7)'
        ];
        
        // If we need more colors than in our predefined list, generate them
        if (count > colors.length) {
            for (let i = colors.length; i < count; i++) {
                const r = Math.floor(Math.random() * 255);
                const g = Math.floor(Math.random() * 255);
                const b = Math.floor(Math.random() * 255);
                colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
            }
        }
        
        return colors.slice(0, count);
    }
    
    // Format currency
    function formatCurrency(value) {
        return 'KES ' + value.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    // Create Category Chart (Pie Chart)
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx && categories.length > 0) {
        const categoryColors = generateColors(categories.length);
        
        new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: categories,
                datasets: [{
                    data: categoryAmounts,
                    backgroundColor: categoryColors,
                    borderColor: categoryColors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 15,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    },
                    datalabels: {
                        formatter: (value, ctx) => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return percentage > 5 ? `${percentage}%` : '';
                        },
                        color: '#fff',
                        font: {
                            weight: 'bold',
                            size: 12
                        }
                    }
                }
            }
        });
    }
    
    // Create Trend Chart (Line Chart)
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx && months.length > 0) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Purchase Amount',
                    data: monthlyAmounts,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.raw);
                            }
                        }
                    },
                    datalabels: {
                        align: 'top',
                        anchor: 'end',
                        formatter: value => formatCurrency(value),
                        font: {
                            weight: 'bold',
                            size: 10
                        },
                        color: 'rgba(54, 162, 235, 1)'
                    }
                }
            }
        });
    }
    
    // Create Payment Method Chart (Doughnut Chart)
    const paymentMethodCtx = document.getElementById('paymentMethodChart');
    if (paymentMethodCtx && paymentMethods.length > 0) {
        const paymentMethodColors = generateColors(paymentMethods.length);
        
        new Chart(paymentMethodCtx, {
            type: 'doughnut',
            data: {
                labels: paymentMethods,
                datasets: [{
                    data: paymentMethodAmounts,
                    backgroundColor: paymentMethodColors,
                    borderColor: paymentMethodColors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 15,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    },
                    datalabels: {
                        formatter: (value, ctx) => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return percentage > 5 ? `${percentage}%` : '';
                        },
                        color: '#fff',
                        font: {
                            weight: 'bold',
                            size: 12
                        }
                    }
                }
            }
        });
    }
    
    // Create Status Chart (Bar Chart)
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx && statuses.length > 0) {
        const statusColors = {
            'PENDING': 'rgba(255, 193, 7, 0.7)',
            'PROCESSING': 'rgba(23, 162, 184, 0.7)',
            'COMPLETED': 'rgba(40, 167, 69, 0.7)',
            'CANCELLED': 'rgba(220, 53, 69, 0.7)'
        };
        
        const colors = statuses.map(status => statusColors[status] || 'rgba(108, 117, 125, 0.7)');
        
        new Chart(statusCtx, {
            type: 'bar',
            data: {
                labels: statuses,
                datasets: [{
                    label: 'Amount by Status',
                    data: statusAmounts,
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.7', '1')),
                    borderWidth: 1,
                    borderRadius: 5,
                    maxBarThickness: 50
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.raw);
                            }
                        }
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        formatter: value => formatCurrency(value),
                        font: {
                            weight: 'bold'
                        },
                        color: function(context) {
                            return context.dataset.borderColor[context.dataIndex];
                        }
                    }
                }
            }
        });
    }
    
    // Create Timeline Chart (Scatter Chart)
    const timelineCtx = document.getElementById('timelineChart');
    if (timelineCtx && months.length > 0) {
        // Create a dataset that combines months and amounts
        const timelineData = months.map((month, index) => {
            return {
                x: index,
                y: monthlyAmounts[index]
            };
        });
        
        new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Purchase Timeline',
                    data: monthlyAmounts,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        },
                        title: {
                            display: true,
                            text: 'Purchase Amount',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time Period',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${formatCurrency(context.raw)}`;
                            }
                        }
                    },
                    datalabels: {
                        display: false
                    }
                }
            }
        });
    }
}); 