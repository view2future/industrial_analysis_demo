// Dashboard JavaScript functionality
class IndustrialDashboard {
    constructor() {
        this.data = window.industrialData;
        this.charts = {};
        this.animationDuration = 2000;
    }

    // Initialize the dashboard
    init() {
        this.updateKPIs();
        this.renderCharts();
        this.populateTable();
        this.setupEventListeners();
    }

    // Update Key Performance Indicators with animation
    updateKPIs() {
        const kpis = this.data.kpis;
        
        // Animate numbers counting up
        this.animateNumber('total-production', 0, kpis.totalProduction, 2000, (num) => {
            return new Intl.NumberFormat().format(num);
        });
        
        this.animateNumber('active-facilities', 0, kpis.activeFacilities, 2000);
        
        this.animateNumber('employment-rate', 0, kpis.employmentRate, 2000, (num) => {
            return num.toFixed(1) + '%';
        });
        
        this.animateNumber('energy-efficiency', 0, kpis.energyEfficiency, 2000, (num) => {
            return num.toFixed(1) + '%';
        });
    }

    // Animate number counting
    animateNumber(elementId, start, end, duration, formatter = null) {
        const element = document.getElementById(elementId);
        const range = end - start;
        const startTime = Date.now();
        
        const updateNumber = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easedProgress = this.easeOutCubic(progress);
            const current = start + (range * easedProgress);
            
            const displayValue = formatter ? formatter(current) : Math.round(current);
            element.textContent = displayValue;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        updateNumber();
    }

    // Easing function
    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    // Render all charts
    renderCharts() {
        this.renderProductionChart();
        this.renderGrowthChart();
    }

    // Render production by region chart (Doughnut chart)
    renderProductionChart() {
        const ctx = document.getElementById('productionChart').getContext('2d');
        const data = this.data.regionalProduction;
        
        this.charts.production = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.colors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = new Intl.NumberFormat().format(context.parsed);
                                const percentage = ((context.parsed / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
                                return `${context.label}: ${value} units (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 2000
                }
            }
        });
    }

    // Render growth trends chart (Line chart)
    renderGrowthChart() {
        const ctx = document.getElementById('growthChart').getContext('2d');
        const data = this.data.growthTrends;
        
        this.charts.growth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets.map(dataset => ({
                    ...dataset,
                    tension: 0.4,
                    pointBackgroundColor: dataset.borderColor,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y}% growth`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Growth Rate (%)'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutCubic'
                }
            }
        });
    }

    // Populate the regional data table
    populateTable() {
        const tableBody = document.getElementById('tableBody');
        const data = this.data.regionalDetails;
        
        // Clear existing content
        tableBody.innerHTML = '';
        
        data.forEach((region, index) => {
            const row = document.createElement('tr');
            row.style.opacity = '0';
            row.style.transform = 'translateY(20px)';
            
            row.innerHTML = `
                <td><strong>${region.region}</strong></td>
                <td>${region.production}</td>
                <td>${region.facilities}</td>
                <td>${region.employment}</td>
                <td><span class="metric-change positive">${region.growthRate}</span></td>
            `;
            
            tableBody.appendChild(row);
            
            // Animate row appearance
            setTimeout(() => {
                row.style.transition = 'all 0.5s ease';
                row.style.opacity = '1';
                row.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    // Setup event listeners
    setupEventListeners() {
        // Add click handlers for metric cards to show additional info
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.handleMetricCardClick(e.currentTarget);
            });
        });

        // Add resize listener for chart responsiveness
        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => {
                if (chart) chart.resize();
            });
        });

        // Add refresh functionality
        this.setupRefreshButton();
    }

    // Handle metric card clicks
    handleMetricCardClick(card) {
        // Add a subtle animation effect
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 150);

        // You could add modal or additional info display here
        console.log('Metric card clicked:', card.querySelector('.metric-label').textContent);
    }

    // Setup refresh functionality
    setupRefreshButton() {
        // Add a refresh button to the header (if it doesn't exist)
        const header = document.querySelector('.header .container');
        if (!document.getElementById('refreshButton')) {
            const refreshButton = document.createElement('button');
            refreshButton.id = 'refreshButton';
            refreshButton.innerHTML = '🔄 Refresh Data';
            refreshButton.className = 'refresh-btn';
            refreshButton.style.cssText = `
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 15px;
                transition: all 0.3s ease;
            `;
            
            refreshButton.addEventListener('mouseover', () => {
                refreshButton.style.background = 'rgba(255, 255, 255, 0.3)';
                refreshButton.style.borderColor = 'rgba(255, 255, 255, 0.5)';
            });
            
            refreshButton.addEventListener('mouseout', () => {
                refreshButton.style.background = 'rgba(255, 255, 255, 0.2)';
                refreshButton.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            });
            
            refreshButton.addEventListener('click', () => {
                this.refreshDashboard();
            });
            
            header.appendChild(refreshButton);
        }
    }

    // Refresh dashboard data
    refreshDashboard() {
        const button = document.getElementById('refreshButton');
        const originalText = button.innerHTML;
        
        button.innerHTML = '⏳ Refreshing...';
        button.disabled = true;
        
        // Simulate data refresh
        setTimeout(() => {
            // Add small random variations to the data for demo purposes
            this.simulateDataUpdate();
            
            // Update displays
            this.updateKPIs();
            this.populateTable();
            
            // Update charts
            Object.values(this.charts).forEach(chart => {
                if (chart) chart.update('active');
            });
            
            button.innerHTML = originalText;
            button.disabled = false;
        }, 1500);
    }

    // Simulate data updates (for demo purposes)
    simulateDataUpdate() {
        const kpis = this.data.kpis;
        
        // Add small random variations
        kpis.totalProduction += Math.floor((Math.random() - 0.5) * 10000);
        kpis.activeFacilities += Math.floor((Math.random() - 0.5) * 2);
        kpis.employmentRate += (Math.random() - 0.5) * 0.5;
        kpis.energyEfficiency += (Math.random() - 0.5) * 0.3;
        
        // Keep values within reasonable bounds
        kpis.employmentRate = Math.max(80, Math.min(95, kpis.employmentRate));
        kpis.energyEfficiency = Math.max(85, Math.min(98, kpis.energyEfficiency));
    }

    // Utility function to format large numbers
    formatLargeNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure all resources are loaded
    setTimeout(() => {
        const dashboard = new IndustrialDashboard();
        dashboard.init();
        
        // Make dashboard instance available globally for debugging
        window.dashboard = dashboard;
        
        console.log('Regional Industrial Analysis Dashboard initialized successfully!');
    }, 100);
});

// Handle potential errors gracefully
window.addEventListener('error', function(e) {
    console.error('Dashboard error:', e.error);
    
    // Show user-friendly error message
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fed7d7;
        color: #e53e3e;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #e53e3e;
        max-width: 300px;
        z-index: 1000;
    `;
    errorDiv.innerHTML = `
        <strong>Dashboard Error</strong><br>
        ${e.message || 'An error occurred while loading the dashboard'}
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove error message after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
});