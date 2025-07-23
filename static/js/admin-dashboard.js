let salesTrendChart = null;
let stockLevelsChart = null;

function createSalesTrendChart(labels, data) {
    const ctx = document.getElementById('salesTrendChart').getContext('2d');
    if (salesTrendChart) {
        salesTrendChart.destroy();
    }
    salesTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Sales (KSh)',
                data: data,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'KSh ' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createStockLevelsChart(labels, data) {
    const ctx = document.getElementById('stockLevelsChart').getContext('2d');
    if (stockLevelsChart) {
        stockLevelsChart.destroy();
    }
    stockLevelsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Current Stock Level',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createLowStockDropdown(lowStockItems) {
    const dropdown = document.createElement('div');
    dropdown.className = 'low-stock-dropdown';
    dropdown.style.display = 'none';
    
    const table = document.createElement('table');
    table.className = 'low-stock-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Variant</th>
                <th>Stock Level</th>
                <th>Price</th>
                <th>Expiry Date</th>
            </tr>
        </thead>
        <tbody>
            ${lowStockItems.map(item => `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.category}</td>
                    <td>${item.variant}</td>
                    <td>${item.stock}</td>
                    <td>KSh ${item.selling_price}</td>
                    <td>${item.expiry_date || 'N/A'}</td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    dropdown.appendChild(table);
    return dropdown;
}

function updateCharts() {
    // Fetch and update sales trend
    fetch('/api/dashboard/sales-trends')
        .then(response => response.json())
        .then(data => {
            createSalesTrendChart(data.labels, data.data);
        })
        .catch(error => console.error('Error fetching sales trends:', error));

    // Fetch and update stock levels
    fetch('/api/dashboard/stock-levels')
        .then(response => response.json())
        .then(data => {
            createStockLevelsChart(data.labels, data.data);
        })
        .catch(error => console.error('Error fetching stock levels:', error));
}

function updateDashboard() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            // Update online orders stats
            const onlineOrdersElement = document.getElementById('online-orders-count');
            if (onlineOrdersElement) {
                onlineOrdersElement.textContent = `${data.total_online_orders} orders (${data.todays_online_orders} today)`;
            }

            // Update offline sales stats
            const offlineSalesElement = document.getElementById('offline-sales-count');
            const offlineItemsElement = document.getElementById('offline-items-count');
            if (offlineSalesElement) {
                offlineSalesElement.textContent = `${data.total_offline_transactions} transactions (${data.todays_offline_sales} today)`;
            }
            if (offlineItemsElement) {
                offlineItemsElement.textContent = `${data.offline_sales_items_count} items sold`;
            }

            // Update low stock alert
            const lowStockCount = document.getElementById('low-stock-count');
            if (lowStockCount) {
                lowStockCount.textContent = data.low_stock_count;
            }

            // Set up low stock dropdown
            const lowStockAlert = document.getElementById('low-stock-alert');
            if (lowStockAlert) {
                const existingDropdown = document.querySelector('.low-stock-dropdown');
                if (existingDropdown) {
                    existingDropdown.remove();
                }
                
                const dropdown = createLowStockDropdown(data.low_stock_items);
                lowStockAlert.parentNode.appendChild(dropdown);
                
                lowStockAlert.onclick = function(e) {
                    e.preventDefault();
                    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
                };
            }
        })
        .catch(error => console.error('Error updating dashboard:', error));
}

// Initialize dashboard and charts
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    updateCharts();
    // Refresh data every 5 minutes
    setInterval(() => {
        updateDashboard();
        updateCharts();
    }, 300000);
});
