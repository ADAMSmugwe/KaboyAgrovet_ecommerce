// Admin Dashboard Charts & Stats

document.addEventListener('DOMContentLoaded', async () => {
    // --- Fetch and Display Stats ---
    async function fetchStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const stats = await response.json();

            document.getElementById('totalSales').textContent = `KSh ${Number(stats.total_sales).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('lowStockCount').textContent = stats.low_stock_count;
            document.getElementById('totalInventoryValue').textContent = `KSh ${Number(stats.total_inventory_value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('todaysOrders').textContent = stats.todays_online_orders;
            document.getElementById('todaysOfflineSales').textContent = stats.todays_offline_sales;
            document.getElementById('totalOfflineSales').textContent = `KSh ${Number(stats.total_offline_sales).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

            // Optional: Display low stock items list
            const lowStockItemsDiv = document.getElementById('lowStockItemsList');
            if (lowStockItemsDiv && stats.low_stock_items.length > 0) {
                lowStockItemsDiv.innerHTML = '<h4>Low Stock:</h4>' + stats.low_stock_items.map(item =>
                    `<p>${item.name} (${item.variant}): ${item.stock}</p>`
                ).join('');
            }
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
        }
    }

    // --- Render Sales Trends Chart ---
    async function renderSalesTrendChart() {
        try {
            const response = await fetch('/api/dashboard/sales-trends');
            const data = await response.json();

            const ctx = document.getElementById('salesTrendChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Total Sales (KSh)',
                        data: data.data,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true
                        },
                        title: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering sales trend chart:', error);
        }
    }

    // --- Render Stock Levels Chart ---
    async function renderStockLevelsChart() {
        try {
            const response = await fetch('/api/dashboard/stock-levels');
            const data = await response.json();

            const ctx = document.getElementById('stockLevelsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Stock Level',
                        data: data.data,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering stock levels chart:', error);
        }
    }

    // --- Initial Calls ---
    fetchStats();
    renderSalesTrendChart();
    renderStockLevelsChart();
});
