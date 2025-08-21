// Admin Dashboard Charts and Analytics JavaScript

class AdminDashboard {
    constructor() {
        this.charts = {};
        this.data = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleNavigation(e.target.closest('.nav-link').dataset.section);
            });
        });

        // Refresh button
        const refreshBtn = document.querySelector('.btn-secondary');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }

        // Manual sale button
        const manualSaleBtn = document.querySelector('a[href="/admin/manual_sale"]');
        if (manualSaleBtn) {
            manualSaleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openManualSale();
            });
        }
    }

    async loadDashboardData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/dashboard-data');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.data = await response.json();
            this.updateDashboard();
            this.hideLoading();
            this.showNotification('Dashboard updated successfully!', 'success');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.hideLoading();
            this.showNotification(`Failed to load dashboard: ${error.message}`, 'error');
            this.loadSampleData(); // Fallback to sample data
        }
    }

    loadSampleData() {
        // Fallback sample data for demonstration
        this.data = {
            stats: {
                total_revenue: 125000,
                total_orders: 45,
                total_products: 28,
                total_customers: 32,
                revenue_change: 12.5,
                orders_change: 8.3,
                products_change: 5.2,
                customers_change: 15.7
            },
            revenue_trend: [
                { date: 'Mon', revenue: 15000 },
                { date: 'Tue', revenue: 18000 },
                { date: 'Wed', revenue: 22000 },
                { date: 'Thu', revenue: 19000 },
                { date: 'Fri', revenue: 25000 },
                { date: 'Sat', revenue: 30000 },
                { date: 'Sun', revenue: 28000 }
            ],
            top_products: [
                { name: 'NPK Fertilizer', sales: 15 },
                { name: 'DAP Fertilizer', sales: 12 },
                { name: 'Pesticide', sales: 8 },
                { name: 'Seeds Mix', sales: 6 },
                { name: 'Other', sales: 4 }
            ],
            recent_activities: [
                {
                    type: 'sale',
                    title: 'New Sale Recorded',
                    description: 'NPK Fertilizer 50kg - KSh 2,500',
                    timestamp: new Date(Date.now() - 300000)
                },
                {
                    type: 'order',
                    title: 'Online Order Received',
                    description: 'Order #123 from John Doe',
                    timestamp: new Date(Date.now() - 900000)
                },
                {
                    type: 'product',
                    title: 'Stock Updated',
                    description: 'Pesticide stock increased by 20 units',
                    timestamp: new Date(Date.now() - 1800000)
                },
                {
                    type: 'customer',
                    title: 'New Customer Registered',
                    description: 'Jane Smith - jane@email.com',
                    timestamp: new Date(Date.now() - 3600000)
                }
            ]
        };
        
        this.updateDashboard();
    }

    updateDashboard() {
        this.updateStats();
        this.updateCharts();
        this.updateActivity();
    }

    updateStats() {
        const stats = this.data.stats || {};
        
        // Update stat values
        this.updateStatElement('total-revenue', `KSh ${(stats.total_revenue || 0).toLocaleString()}`);
        this.updateStatElement('total-orders', (stats.total_orders || 0).toLocaleString());
        this.updateStatElement('total-products', (stats.total_products || 0).toLocaleString());
        this.updateStatElement('total-customers', (stats.total_customers || 0).toLocaleString());
        
        // Update change indicators
        this.updateChangeIndicator('revenue-change', stats.revenue_change);
        this.updateChangeIndicator('orders-change', stats.orders_change);
        this.updateChangeIndicator('products-change', stats.products_change);
        this.updateChangeIndicator('customers-change', stats.customers_change);
    }

    updateStatElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateChangeIndicator(id, change) {
        const element = document.getElementById(id);
        if (!element) return;
        
        if (change > 0) {
            element.textContent = `+${change.toFixed(1)}% from last month`;
            element.className = 'stat-change';
        } else if (change < 0) {
            element.textContent = `${change.toFixed(1)}% from last month`;
            element.className = 'stat-change negative';
        } else {
            element.textContent = 'No change from last month';
            element.className = 'stat-change';
        }
    }

    updateCharts() {
        this.updateRevenueChart();
        this.updateProductsChart();
    }

    updateRevenueChart() {
        const ctx = document.getElementById('revenue-chart');
        if (!ctx) return;
        
        const data = this.data.revenue_trend || [];
        
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }
        
        this.charts.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.date),
                datasets: [{
                    label: 'Revenue (KSh)',
                    data: data.map(item => item.revenue),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return 'KSh ' + value.toLocaleString();
                            },
                            color: '#666'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            color: '#666'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    updateProductsChart() {
        const ctx = document.getElementById('products-chart');
        if (!ctx) return;
        
        const data = this.data.top_products || [];
        
        if (this.charts.products) {
            this.charts.products.destroy();
        }
        
        this.charts.products = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.name),
                datasets: [{
                    data: data.map(item => item.sales),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c',
                        '#4facfe',
                        '#00f2fe',
                        '#43e97b',
                        '#38f9d7'
                    ],
                    borderWidth: 0,
                    hoverBorderWidth: 2,
                    hoverBorderColor: '#fff'
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
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} sales (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    updateActivity() {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;
        
        const activities = this.data.recent_activities || [];
        
        if (activities.length === 0) {
            activityList.innerHTML = `
                <li class="activity-item">
                    <div class="activity-content">
                        <h4>No recent activity</h4>
                        <p>Start making sales to see activity here</p>
                    </div>
                </li>
            `;
            return;
        }
        
        activityList.innerHTML = activities.map(activity => `
            <li class="activity-item">
                <div class="activity-icon" style="background: ${this.getActivityColor(activity.type)};">
                    <i class="fas ${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <h4>${activity.title}</h4>
                    <p>${activity.description}</p>
                </div>
                <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
            </li>
        `).join('');
    }

    getActivityColor(type) {
        const colors = {
            'sale': 'linear-gradient(135deg, #667eea, #764ba2)',
            'order': 'linear-gradient(135deg, #f093fb, #f5576c)',
            'product': 'linear-gradient(135deg, #4facfe, #00f2fe)',
            'customer': 'linear-gradient(135deg, #43e97b, #38f9d7)'
        };
        return colors[type] || colors.sale;
    }

    getActivityIcon(type) {
        const icons = {
            'sale': 'fa-dollar-sign',
            'order': 'fa-shopping-cart',
            'product': 'fa-box',
            'customer': 'fa-user'
        };
        return icons[type] || 'fa-info-circle';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
        if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
        return date.toLocaleDateString();
    }

    handleNavigation(section) {
        // Update active navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');
        
        // Handle section-specific logic
        switch(section) {
            case 'overview':
                this.showOverview();
                break;
            case 'products':
                this.showProducts();
                break;
            case 'orders':
                this.showOrders();
                break;
            case 'customers':
                this.showCustomers();
                break;
            case 'analytics':
                this.showAnalytics();
                break;
            case 'settings':
                this.showSettings();
                break;
        }
    }

    showOverview() {
        // Default view - already shown
    }

    showProducts() {
        // TODO: Implement products view
        this.showNotification('Products view coming soon!', 'success');
    }

    showOrders() {
        // TODO: Implement orders view
        this.showNotification('Orders view coming soon!', 'success');
    }

    showCustomers() {
        // TODO: Implement customers view
        this.showNotification('Customers view coming soon!', 'success');
    }

    showAnalytics() {
        // TODO: Implement analytics view
        this.showNotification('Analytics view coming soon!', 'success');
    }

    showSettings() {
        // TODO: Implement settings view
        this.showNotification('Settings view coming soon!', 'success');
    }

    openManualSale() {
        window.open('/admin/manual_sale', '_blank');
    }

    refreshDashboard() {
        this.loadDashboardData();
    }

    startAutoRefresh() {
        // Refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showLoading() {
        const elements = ['total-revenue', 'total-orders', 'total-products', 'total-customers'];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = '<span class="loading"></span>';
            }
        });
    }

    hideLoading() {
        // Loading is hidden when data is loaded
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        if (!notification) return;
        
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    destroy() {
        this.stopAutoRefresh();
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminDashboard = new AdminDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.adminDashboard) {
        window.adminDashboard.destroy();
    }
});
