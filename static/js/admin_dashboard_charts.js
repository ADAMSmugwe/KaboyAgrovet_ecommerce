// Admin Dashboard Charts & Stats

// Global modal functions (accessible from HTML onclick)
window.showOfflineSalesModal = async function() {
    const modal = document.getElementById('offlineSalesModal');
    const salesList = document.getElementById('offlineSalesList');
    
    // Show loading message
    salesList.innerHTML = '<p style="text-align:center;color:var(--text-light);">Loading offline sales...</p>';
    modal.style.display = 'block';
    
    try {
        const response = await fetch('/api/dashboard/recent-offline-sales');
        const salesData = await response.json();
        
        if (salesData.length > 0) {
            const tableHTML = `
                <div style="overflow-x:auto;">
                    <table style="width:100%;border-collapse:collapse;margin-top:10px;">
                        <thead>
                            <tr style="background-color:var(--light-color);">
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Sale ID</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Customer</th>
                                <th style="padding:12px;text-align:right;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Total</th>
                                <th style="padding:12px;text-align:right;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Paid</th>
                                <th style="padding:12px;text-align:center;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Payment</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Date</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Items</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${salesData.map(sale => `
                                <tr style="border-bottom:1px solid #eee;">
                                    <td style="padding:10px;border:1px solid #ddd;font-weight:600;color:var(--primary-color);">#${sale.id}</td>
                                    <td style="padding:10px;border:1px solid #ddd;">${sale.customer_name}</td>
                                    <td style="padding:10px;border:1px solid #ddd;text-align:right;font-weight:600;color:var(--primary-color);">KSh ${Number(sale.total_cost).toLocaleString()}</td>
                                    <td style="padding:10px;border:1px solid #ddd;text-align:right;">KSh ${Number(sale.amount_paid).toLocaleString()}</td>
                                    <td style="padding:10px;border:1px solid #ddd;text-align:center;">
                                        <span style="background-color:var(--accent-color);color:white;padding:3px 8px;border-radius:10px;font-size:0.8rem;">
                                            ${sale.payment_mode}
                                        </span>
                                    </td>
                                    <td style="padding:10px;border:1px solid #ddd;font-size:0.9rem;">${sale.sale_date}</td>
                                    <td style="padding:10px;border:1px solid #ddd;">
                                        <ul style="margin:0;padding-left:15px;">
                                            ${sale.items.map(item => `
                                                <li style="font-size:0.9rem;margin-bottom:3px;">
                                                    ${item.quantity}x ${item.product_name} (${item.variant}) - KSh ${Number(item.price).toLocaleString()}
                                                </li>
                                            `).join('')}
                                        </ul>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div style="margin-top:15px;padding:10px;background-color:#e8f5e9;border:1px solid #c3e6cb;border-radius:5px;">
                    <p style="margin:0;color:var(--primary-color);font-size:0.9rem;">
                        <strong>💰 Summary:</strong> Showing the ${salesData.length} most recent offline sales transactions.
                    </p>
                </div>
            `;
            salesList.innerHTML = tableHTML;
        } else {
            salesList.innerHTML = `
                <div style="text-align:center;padding:40px;">
                    <span style="font-size:3rem;color:var(--accent-color);">🏪</span>
                    <h3 style="color:var(--primary-color);margin:15px 0 10px 0;">No Offline Sales Yet</h3>
                    <p style="color:var(--text-light);margin:0;">No offline sales have been recorded yet.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching offline sales:', error);
        salesList.innerHTML = `
            <div style="text-align:center;padding:40px;">
                <span style="font-size:3rem;color:#d32f2f;">⚠️</span>
                <h3 style="color:#d32f2f;margin:15px 0 10px 0;">Error Loading Data</h3>
                <p style="color:var(--text-light);margin:0;">Failed to load offline sales data. Please try again.</p>
            </div>
        `;
    }
};

window.showOnlineOrdersModal = async function() {
    const modal = document.getElementById('onlineOrdersModal');
    const ordersList = document.getElementById('onlineOrdersList');
    
    // Show loading message
    ordersList.innerHTML = '<p style="text-align:center;color:var(--text-light);">Loading online orders...</p>';
    modal.style.display = 'block';
    
    try {
        const response = await fetch('/api/dashboard/recent-online-orders');
        const ordersData = await response.json();
        
        if (ordersData.length > 0) {
            const tableHTML = `
                <div style="overflow-x:auto;">
                    <table style="width:100%;border-collapse:collapse;margin-top:10px;">
                        <thead>
                            <tr style="background-color:var(--light-color);">
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Order ID</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Customer</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Contact</th>
                                <th style="padding:12px;text-align:right;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Total</th>
                                <th style="padding:12px;text-align:center;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Status</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Date</th>
                                <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Items</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${ordersData.map(order => {
                                const statusColor = order.payment_status === 'Paid' ? '#e8f5e9' : order.payment_status === 'Pending' ? '#fffde7' : '#ffebee';
                                const statusTextColor = order.payment_status === 'Paid' ? 'var(--primary-color)' : order.payment_status === 'Pending' ? 'var(--accent-color)' : '#d32f2f';
                                return `
                                    <tr style="border-bottom:1px solid #eee;">
                                        <td style="padding:10px;border:1px solid #ddd;font-weight:600;color:var(--primary-color);">#${order.id}</td>
                                        <td style="padding:10px;border:1px solid #ddd;">${order.customer_name}</td>
                                        <td style="padding:10px;border:1px solid #ddd;font-size:0.9rem;">
                                            <div>${order.customer_email}</div>
                                            <div style="color:var(--text-light);">${order.customer_phone}</div>
                                        </td>
                                        <td style="padding:10px;border:1px solid #ddd;text-align:right;font-weight:600;color:var(--primary-color);">KSh ${Number(order.total_amount).toLocaleString()}</td>
                                        <td style="padding:10px;border:1px solid #ddd;text-align:center;">
                                            <span style="background-color:${statusColor};color:${statusTextColor};padding:3px 8px;border-radius:10px;font-size:0.8rem;font-weight:600;">
                                                ${order.payment_status}
                                            </span>
                                        </td>
                                        <td style="padding:10px;border:1px solid #ddd;font-size:0.9rem;">${order.ordered_at}</td>
                                        <td style="padding:10px;border:1px solid #ddd;">
                                            <ul style="margin:0;padding-left:15px;">
                                                ${order.items.map(item => `
                                                    <li style="font-size:0.9rem;margin-bottom:3px;">
                                                        ${item.quantity}x ${item.product_name} (${item.variant}) - KSh ${Number(item.price).toLocaleString()}
                                                    </li>
                                                `).join('')}
                                            </ul>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
                <div style="margin-top:15px;padding:10px;background-color:#e8f5e9;border:1px solid #c3e6cb;border-radius:5px;">
                    <p style="margin:0;color:var(--primary-color);font-size:0.9rem;">
                        <strong>🛒 Summary:</strong> Showing the ${ordersData.length} most recent online orders.
                    </p>
                </div>
            `;
            ordersList.innerHTML = tableHTML;
        } else {
            ordersList.innerHTML = `
                <div style="text-align:center;padding:40px;">
                    <span style="font-size:3rem;color:var(--primary-color);">🛒</span>
                    <h3 style="color:var(--primary-color);margin:15px 0 10px 0;">No Online Orders Yet</h3>
                    <p style="color:var(--text-light);margin:0;">No online orders have been placed yet.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching online orders:', error);
        ordersList.innerHTML = `
            <div style="text-align:center;padding:40px;">
                <span style="font-size:3rem;color:#d32f2f;">⚠️</span>
                <h3 style="color:#d32f2f;margin:15px 0 10px 0;">Error Loading Data</h3>
                <p style="color:var(--text-light);margin:0;">Failed to load online orders data. Please try again.</p>
            </div>
        `;
    }
};

// Load dashboard data when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadCharts();
});

// Load all dashboard data
function loadDashboardData() {
    loadRecentOnlineOrders();
    loadRecentOfflineSales();
    loadLowStockProducts();
    loadDashboardStats();
}

// Load recent online orders
function loadRecentOnlineOrders() {
    fetch('/api/dashboard/recent-online-orders')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recentOnlineOrders');
            if (data.recent_orders && data.recent_orders.length > 0) {
                let html = '<div style="display:flex;flex-direction:column;gap:0.5rem;">';
                data.recent_orders.forEach(order => {
                    const statusColor = order.payment_status === 'Paid' ? '#4caf50' : 
                                      order.payment_status === 'Pending' ? '#ff9800' : '#f44336';
                    html += `
                        <div style="border:1px solid #e0e0e0;border-radius:8px;padding:0.8rem;background:#fafafa;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                                <strong style="color:var(--primary-color);">${order.customer_name}</strong>
                                <span style="padding:0.2em 0.6em;border-radius:12px;background:${statusColor};color:white;font-size:0.8rem;font-weight:600;">
                                    ${order.payment_status}
                                </span>
                            </div>
                            <div style="font-size:0.9rem;color:var(--text-light);margin-bottom:0.3rem;">
                                📧 ${order.customer_email} | 📞 ${order.customer_phone}
                            </div>
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="font-weight:600;color:var(--primary-color);">KSh ${order.total_amount.toFixed(2)}</span>
                                <span style="font-size:0.8rem;color:var(--text-light);">${order.ordered_at}</span>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="text-align:center;color:var(--text-light);">No recent online orders</p>';
            }
        })
        .catch(error => {
            console.error('Error loading recent online orders:', error);
            document.getElementById('recentOnlineOrders').innerHTML = 
                '<p style="text-align:center;color:#f44336;">Error loading orders</p>';
        });
}

// Load recent offline sales
function loadRecentOfflineSales() {
    fetch('/api/dashboard/recent-offline-sales')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recentOfflineSales');
            if (data.recent_sales && data.recent_sales.length > 0) {
                let html = '<div style="display:flex;flex-direction:column;gap:0.5rem;">';
                data.recent_sales.forEach(sale => {
                    const paymentColor = sale.payment_mode === 'Cash' ? '#4caf50' : 
                                       sale.payment_mode === 'M-Pesa' ? '#2196f3' : '#ff9800';
                    html += `
                        <div style="border:1px solid #e0e0e0;border-radius:8px;padding:0.8rem;background:#fafafa;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                                <strong style="color:var(--accent-color);">${sale.customer_name}</strong>
                                <span style="padding:0.2em 0.6em;border-radius:12px;background:${paymentColor};color:white;font-size:0.8rem;font-weight:600;">
                                    ${sale.payment_mode}
                                </span>
                            </div>
                            <div style="font-size:0.9rem;color:var(--text-light);margin-bottom:0.3rem;">
                                💰 Paid: KSh ${sale.amount_paid.toFixed(2)} | 💸 Change: KSh ${sale.change_given.toFixed(2)}
                            </div>
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="font-weight:600;color:var(--accent-color);">KSh ${sale.total_cost.toFixed(2)}</span>
                                <span style="font-size:0.8rem;color:var(--text-light);">${sale.sale_date}</span>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="text-align:center;color:var(--text-light);">No recent offline sales</p>';
            }
        })
        .catch(error => {
            console.error('Error loading recent offline sales:', error);
            document.getElementById('recentOfflineSales').innerHTML = 
                '<p style="text-align:center;color:#f44336;">Error loading sales</p>';
        });
}

// Load low stock products
function loadLowStockProducts() {
    fetch('/api/dashboard/stock-levels')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('lowStockProducts');
            if (data.low_stock_items && data.low_stock_items.length > 0) {
                let html = '<div style="display:flex;flex-direction:column;gap:0.5rem;">';
                data.low_stock_items.forEach(item => {
                    const stockColor = item.stock_level === 0 ? '#f44336' : 
                                     item.stock_level < 5 ? '#ff9800' : '#ffc107';
                    html += `
                        <div style="border:1px solid #e0e0e0;border-radius:8px;padding:0.8rem;background:#fafafa;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                                <strong style="color:#d32f2f;">${item.product_name}</strong>
                                <span style="padding:0.2em 0.6em;border-radius:12px;background:${stockColor};color:white;font-size:0.8rem;font-weight:600;">
                                    ${item.stock_level} left
                                </span>
                            </div>
                            <div style="font-size:0.9rem;color:var(--text-light);margin-bottom:0.3rem;">
                                📦 ${item.variant_info} | 💰 KSh ${item.selling_price.toFixed(2)}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="text-align:center;color:var(--text-light);">All products have sufficient stock</p>';
            }
        })
        .catch(error => {
            console.error('Error loading low stock products:', error);
            document.getElementById('lowStockProducts').innerHTML = 
                '<p style="text-align:center;color:#f44336;">Error loading stock data</p>';
        });
}

// Load dashboard statistics
function loadDashboardStats() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            // Update statistics cards
            document.getElementById('online-orders-count').textContent = data.total_orders;
            document.getElementById('offline-sales-count').textContent = data.total_offline_sales;
            
            // Update offline items count
            const offlineItemsCount = document.getElementById('offline-items-count');
            if (offlineItemsCount) {
                offlineItemsCount.textContent = `${data.total_offline_sales} total sales`;
            }
        })
        .catch(error => {
            console.error('Error loading dashboard stats:', error);
        });
    
    // Get low stock count from stock-levels API
    fetch('/api/dashboard/stock-levels')
        .then(response => response.json())
        .then(data => {
            const lowStockCount = data.low_stock_items ? data.low_stock_items.length : 0;
            document.getElementById('low-stock-count').textContent = lowStockCount;
        })
        .catch(error => {
            console.error('Error loading stock levels:', error);
            document.getElementById('low-stock-count').textContent = '0';
        });
}

// Load charts
function loadCharts() {
    renderSalesTrendChart();
    renderStockLevelsChart();
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

// --- Modal Functions ---
function showLowStockModal() {
    const modal = document.getElementById('lowStockModal');
    const productsList = document.getElementById('lowStockProductsList');
    
    if (window.lowStockItems && window.lowStockItems.length > 0) {
        // Create a nice table to display low stock products
        const tableHTML = `
            <div style="overflow-x:auto;">
                <table style="width:100%;border-collapse:collapse;margin-top:10px;">
                    <thead>
                        <tr style="background-color:var(--light-color);">
                            <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Product</th>
                            <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Variant</th>
                            <th style="padding:12px;text-align:center;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Stock Level</th>
                            <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Category</th>
                            <th style="padding:12px;text-align:right;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Price</th>
                            <th style="padding:12px;text-align:left;border:1px solid #ddd;color:var(--primary-color);font-weight:600;">Expiry</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${window.lowStockItems.map(item => `
                            <tr style="border-bottom:1px solid #eee;">
                                <td style="padding:10px;border:1px solid #ddd;font-weight:500;">${item.name}</td>
                                <td style="padding:10px;border:1px solid #ddd;">${item.variant}</td>
                                <td style="padding:10px;border:1px solid #ddd;text-align:center;">
                                    <span style="background-color:#ffebee;color:#d32f2f;padding:4px 8px;border-radius:12px;font-weight:600;font-size:0.9rem;">
                                        ${item.stock}
                                    </span>
                                </td>
                                <td style="padding:10px;border:1px solid #ddd;">
                                    <span style="background-color:var(--secondary-color);color:white;padding:3px 8px;border-radius:10px;font-size:0.8rem;">
                                        ${item.category}
                                    </span>
                                </td>
                                <td style="padding:10px;border:1px solid #ddd;text-align:right;font-weight:600;color:var(--primary-color);">KSh ${Number(item.selling_price).toLocaleString()}</td>
                                <td style="padding:10px;border:1px solid #ddd;font-size:0.9rem;color:var(--text-light);">${item.expiry_date || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div style="margin-top:15px;padding:10px;background-color:#fff3cd;border:1px solid #ffeaa7;border-radius:5px;">
                <p style="margin:0;color:#856404;font-size:0.9rem;">
                    <strong>💡 Tip:</strong> Consider restocking these items soon to avoid running out of inventory.
                </p>
            </div>
        `;
        productsList.innerHTML = tableHTML;
    } else {
        productsList.innerHTML = `
            <div style="text-align:center;padding:40px;">
                <span style="font-size:3rem;color:var(--primary-color);">✅</span>
                <h3 style="color:var(--primary-color);margin:15px 0 10px 0;">Great News!</h3>
                <p style="color:var(--text-light);margin:0;">All products are well stocked. No low stock alerts at this time.</p>
            </div>
        `;
    }
    
    modal.style.display = 'block';
}

function hideLowStockModal() {
    const modal = document.getElementById('lowStockModal');
    modal.style.display = 'none';
}

// Modal hide functions (global functions are defined above)
function hideOfflineSalesModal() {
    const modal = document.getElementById('offlineSalesModal');
    modal.style.display = 'none';
}

function hideOnlineOrdersModal() {
    const modal = document.getElementById('onlineOrdersModal');
    modal.style.display = 'none';
}

// Set up modal close handlers
document.addEventListener('click', function(event) {
    // Handle Low Stock Modal
    const lowStockModal = document.getElementById('lowStockModal');
    const lowStockCloseBtn = lowStockModal.querySelector('.close');
    
    if (event.target === lowStockCloseBtn || event.target === lowStockModal) {
        hideLowStockModal();
    }
    
    // Handle Offline Sales Modal
    const offlineSalesModal = document.getElementById('offlineSalesModal');
    const offlineSalesCloseBtn = offlineSalesModal.querySelector('.close');
    
    if (event.target === offlineSalesCloseBtn || event.target === offlineSalesModal) {
        hideOfflineSalesModal();
    }
    
    // Handle Online Orders Modal
    const onlineOrdersModal = document.getElementById('onlineOrdersModal');
    const onlineOrdersCloseBtn = onlineOrdersModal.querySelector('.close');
    
    if (event.target === onlineOrdersCloseBtn || event.target === onlineOrdersModal) {
        hideOnlineOrdersModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        hideLowStockModal();
        hideOfflineSalesModal();
        hideOnlineOrdersModal();
    }
});
