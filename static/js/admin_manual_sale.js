// Admin Manual Sale Page JS

// Sale items state
let saleItems = [];

// Utility: Format currency
function formatCurrency(amount) {
    return "KSh " + (parseFloat(amount) || 0).toFixed(2);
}

// Search product variants (AJAX placeholder)
document.getElementById('productVariantSearch').addEventListener('input', function () {
    const query = this.value.trim();
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    if (query.length < 2) return;
    // TODO: Replace with actual AJAX call to backend API
    fetch(`/api/products?search=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(products => {
            products.forEach(product => {
                product.variants.forEach(variant => {
                    const item = document.createElement('a');
                    item.className = 'list-group-item list-group-item-action';
                    item.href = '#';
                    item.textContent = `${product.name} (${variant.quantity_value}${variant.quantity_unit}) - KSh ${variant.selling_price} | Stock: ${variant.stock_level}`;
                    item.dataset.variantId = variant.id;
                    item.dataset.variantName = product.name + " (" + variant.quantity_value + variant.quantity_unit + ")";
                    item.dataset.unitPrice = variant.selling_price;
                    item.dataset.stockLevel = variant.stock_level;
                    item.onclick = function (e) {
                        e.preventDefault();
                        document.getElementById('productVariantSearch').value = item.dataset.variantName;
                        document.getElementById('productVariantSearch').dataset.variantId = item.dataset.variantId;
                        document.getElementById('productVariantSearch').dataset.unitPrice = item.dataset.unitPrice;
                        document.getElementById('productVariantSearch').dataset.stockLevel = item.dataset.stockLevel;
                        resultsDiv.innerHTML = '';
                    };
                    resultsDiv.appendChild(item);
                });
            });
        });
});

// Add item to sale
document.getElementById('addToSaleBtn').onclick = function () {
    const variantId = document.getElementById('productVariantSearch').dataset.variantId;
    const variantName = document.getElementById('productVariantSearch').value;
    const unitPrice = parseFloat(document.getElementById('productVariantSearch').dataset.unitPrice || 0);
    const stockLevel = parseInt(document.getElementById('productVariantSearch').dataset.stockLevel || 0);
    const quantity = parseInt(document.getElementById('itemQuantity').value);

    if (!variantId || !variantName) {
        document.getElementById('productVariantSearchError').textContent = "Please select a product variant from search.";
        return;
    }
    if (isNaN(quantity) || quantity < 1) {
        document.getElementById('itemQuantityError').textContent = "Enter a valid quantity.";
        return;
    }
    if (quantity > stockLevel) {
        document.getElementById('itemQuantityError').textContent = `Only ${stockLevel} in stock.`;
        return;
    }
    document.getElementById('productVariantSearchError').textContent = '';
    document.getElementById('itemQuantityError').textContent = '';

    // Add to saleItems
    saleItems.push({
        variantId,
        variantName,
        unitPrice,
        quantity,
        subtotal: unitPrice * quantity
    });
    renderSaleItems();
    // Reset fields
    document.getElementById('productVariantSearch').value = '';
    document.getElementById('productVariantSearch').dataset.variantId = '';
    document.getElementById('productVariantSearch').dataset.unitPrice = '';
    document.getElementById('productVariantSearch').dataset.stockLevel = '';
    document.getElementById('itemQuantity').value = 1;
};

// Render sale items table
function renderSaleItems() {
    const tbody = document.querySelector('#saleItemsList tbody');
    tbody.innerHTML = '';
    let total = 0;
    saleItems.forEach((item, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.variantName}</td>
            <td>${formatCurrency(item.unitPrice)}</td>
            <td>${item.quantity}</td>
            <td>${formatCurrency(item.subtotal)}</td>
            <td><button type="button" class="btn btn-danger btn-sm" data-idx="${idx}">Remove</button></td>
        `;
        tbody.appendChild(tr);
        total += item.subtotal;
    });
    document.getElementById('saleGrandTotal').textContent = formatCurrency(total);
    document.getElementById('changeDue').textContent = formatCurrency(Math.max(0, parseFloat(document.getElementById('amountPaid').value || 0) - total));
    document.getElementById('emptySaleMessage').style.display = saleItems.length ? 'none' : 'block';
}

// Remove item from sale
document.querySelector('#saleItemsList').addEventListener('click', function (e) {
    if (e.target.matches('button[data-idx]')) {
        const idx = parseInt(e.target.dataset.idx);
        saleItems.splice(idx, 1);
        renderSaleItems();
    }
});

// Update change due on amount paid change
document.getElementById('amountPaid').addEventListener('input', function () {
    const total = parseFloat(document.getElementById('saleGrandTotal').textContent.replace(/[^\d.]/g, '')) || 0;
    const paid = parseFloat(this.value) || 0;
    document.getElementById('changeDue').textContent = formatCurrency(Math.max(0, paid - total));
});

// Handle sale form submission
document.getElementById('manualSaleForm').onsubmit = function (e) {
    e.preventDefault();
    if (!saleItems.length) {
        document.getElementById('manualSaleFormMessage').textContent = "Add at least one item to the sale.";
        return;
    }
    const customerName = document.getElementById('customerName').value;
    const amountPaid = parseFloat(document.getElementById('amountPaid').value);
    const paymentMode = document.getElementById('paymentMode').value;
    const totalCost = saleItems.reduce((sum, item) => sum + item.subtotal, 0);
    const changeGiven = Math.max(0, amountPaid - totalCost);

    // Prepare payload
    const payload = {
        customer_name: customerName,
        amount_paid: amountPaid,
        change_given: changeGiven,
        payment_mode: paymentMode,
        total_cost: totalCost,
        items: saleItems.map(item => ({
            product_variant_id: item.variantId,
            quantity: item.quantity,
            price_at_sale: item.unitPrice
        }))
    };

    // TODO: Replace with actual backend endpoint for offline sale
    fetch('/api/manual-offline-sale', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('manualSaleFormMessage').textContent = data.message || "Sale recorded successfully!";
            saleItems = [];
            renderSaleItems();
            document.getElementById('manualSaleForm').reset();
        } else {
            document.getElementById('manualSaleFormMessage').textContent = data.message || "Error saving sale.";
        }
    })
    .catch(() => {
        document.getElementById('manualSaleFormMessage').textContent = "Network error. Please try again.";
    });
};

document.addEventListener('DOMContentLoaded', () => {
    // --- Element declarations ---
    const productVariantSearchInput = document.getElementById('productVariantSearch');
    const searchResultsDiv = document.getElementById('searchResults');
    const itemQuantityInput = document.getElementById('itemQuantity');
    const addToSaleBtn = document.getElementById('addToSaleBtn');
    const saleItemsTableBody = document.querySelector('#saleItemsList tbody');
    const saleGrandTotalElement = document.getElementById('saleGrandTotal');
    const emptySaleMessage = document.getElementById('emptySaleMessage');
    const manualSaleForm = document.getElementById('manualSaleForm');
    const customerNameInput = document.getElementById('customerName');
    const amountPaidInput = document.getElementById('amountPaid');
    const paymentModeSelect = document.getElementById('paymentMode');
    const changeDueElement = document.getElementById('changeDue');
    const completeSaleBtn = document.getElementById('completeSaleBtn');
    const manualSaleFormMessage = document.getElementById('manualSaleFormMessage');

    // --- State ---
    let currentSaleItems = [];
    let selectedVariantForAdd = null;

    // --- Helper functions ---
    function displayFieldError(fieldId, errorMessage) {
        const errorElement = document.getElementById(fieldId + 'Error');
        const inputElement = document.getElementById(fieldId);
        if (errorElement) errorElement.textContent = errorMessage;
        if (inputElement) inputElement.classList.add('invalid');
    }
    function clearFieldError(fieldId) {
        const errorElement = document.getElementById(fieldId + 'Error');
        const inputElement = document.getElementById(fieldId);
        if (errorElement) errorElement.textContent = '';
        if (inputElement) inputElement.classList.remove('invalid');
    }
    function validateQuantity(fieldId, value) {
        const quantityInt = parseInt(value);
        if (!value || isNaN(quantityInt) || quantityInt <= 0) {
            displayFieldError(fieldId, 'Quantity must be a positive number.');
            return false;
        }
        clearFieldError(fieldId);
        return true;
    }
    function validateAmount(fieldId, value) {
        const amountFloat = parseFloat(value);
        if (!value || isNaN(amountFloat) || amountFloat < 0) {
            displayFieldError(fieldId, 'Amount must be a non-negative number.');
            return false;
        }
        clearFieldError(fieldId);
        return true;
    }

    // --- Product Variant Search ---
    let searchTimeout;
    productVariantSearchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const searchTerm = productVariantSearchInput.value.trim();
        if (searchTerm.length < 2) {
            searchResultsDiv.innerHTML = '';
            selectedVariantForAdd = null;
            return;
        }
        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/api/products?search=${encodeURIComponent(searchTerm)}`);
                const products = await response.json();
                searchResultsDiv.innerHTML = '';
                selectedVariantForAdd = null;
                if (products.length === 0) {
                    searchResultsDiv.innerHTML = '<p class="list-group-item">No matching products found.</p>';
                    return;
                }
                products.forEach(product => {
                    product.variants.forEach(variant => {
                        const resultItem = document.createElement('a');
                        resultItem.href = '#';
                        resultItem.className = 'list-group-item list-group-item-action';
                        resultItem.innerHTML = `
                            <strong>${product.name}</strong> (${variant.quantity_value}${variant.quantity_unit}) - KSh ${Number(variant.selling_price).toLocaleString()}
                            <br><small>Stock: ${variant.stock_level}</small>
                        `;
                        resultItem.addEventListener('click', (e) => {
                            e.preventDefault();
                            productVariantSearchInput.value = `${product.name} (${variant.quantity_value}${variant.quantity_unit})`;
                            searchResultsDiv.innerHTML = '';
                            selectedVariantForAdd = {
                                id: variant.id,
                                productName: product.name,
                                quantityValue: variant.quantity_value,
                                quantityUnit: variant.quantity_unit,
                                sellingPrice: variant.selling_price,
                                stockLevel: variant.stock_level
                            };
                        });
                        searchResultsDiv.appendChild(resultItem);
                    });
                });
            } catch (error) {
                searchResultsDiv.innerHTML = '<p class="list-group-item text-danger">Error searching. Please try again.</p>';
            }
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (!productVariantSearchInput.contains(e.target) && !searchResultsDiv.contains(e.target)) {
            searchResultsDiv.innerHTML = '';
        }
    });

    // --- Add to Sale Button Logic ---
    addToSaleBtn.addEventListener('click', () => {
        if (!selectedVariantForAdd) {
            displayFieldError('productVariantSearch', 'Please select a product variant from the search results.');
            return;
        }
        const quantity = parseInt(itemQuantityInput.value);
        if (!validateQuantity('itemQuantity', quantity)) return;
        if (quantity > selectedVariantForAdd.stockLevel) {
            displayFieldError('itemQuantity', `Only ${selectedVariantForAdd.stockLevel} in stock.`);
            return;
        }
        clearFieldError('itemQuantity');
        const existingItemIndex = currentSaleItems.findIndex(item => item.variantId === selectedVariantForAdd.id);
        if (existingItemIndex > -1) {
            currentSaleItems[existingItemIndex].quantity += quantity;
        } else {
            currentSaleItems.push({
                variantId: selectedVariantForAdd.id,
                productName: selectedVariantForAdd.productName,
                quantityValue: selectedVariantForAdd.quantityValue,
                quantityUnit: selectedVariantForAdd.quantityUnit,
                sellingPrice: selectedVariantForAdd.sellingPrice,
                quantity: quantity
            });
        }
        selectedVariantForAdd.stockLevel -= quantity;
        renderSaleItems();
        productVariantSearchInput.value = '';
        itemQuantityInput.value = '1';
        selectedVariantForAdd = null;
        clearFieldError('productVariantSearch');
    });

    // --- Render Current Sale Items & Calculate Total ---
    function renderSaleItems() {
        saleItemsTableBody.innerHTML = '';
        let currentTotal = 0;
        if (currentSaleItems.length === 0) {
            emptySaleMessage.style.display = 'block';
            saleItemsTableBody.style.display = 'none';
        } else {
            emptySaleMessage.style.display = 'none';
            saleItemsTableBody.style.display = 'table-row-group';
            currentSaleItems.forEach((item, index) => {
                const subtotal = item.sellingPrice * item.quantity;
                currentTotal += subtotal;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.productName} (${item.quantityValue}${item.quantityUnit})</td>
                    <td>KSh ${Number(item.sellingPrice).toLocaleString()}</td>
                    <td>${item.quantity}</td>
                    <td>KSh ${Number(subtotal).toLocaleString()}</td>
                    <td>
                        <button class="btn btn-danger btn-sm remove-sale-item" data-index="${index}">Remove</button>
                    </td>
                `;
                saleItemsTableBody.appendChild(row);
            });
        }
        saleGrandTotalElement.textContent = `KSh ${Number(currentTotal).toLocaleString()}`;
        calculateChange();
    }

    saleItemsTableBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-sale-item')) {
            const indexToRemove = parseInt(e.target.dataset.index);
            currentSaleItems.splice(indexToRemove, 1);
            renderSaleItems();
        }
    });

    // --- Calculate Change Due ---
    amountPaidInput.addEventListener('input', calculateChange);
    function calculateChange() {
        const amountPaid = parseFloat(amountPaidInput.value) || 0;
        const totalCost = currentSaleItems.reduce((sum, item) => sum + (item.sellingPrice * item.quantity), 0);
        const change = amountPaid - totalCost;
        changeDueElement.textContent = `KSh ${Number(change).toLocaleString()}`;
        changeDueElement.style.color = change < 0 ? 'red' : 'green';
    }

    // --- Complete Sale Button Logic ---
    manualSaleForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        manualSaleFormMessage.innerHTML = '';
        manualSaleFormMessage.classList.remove('success', 'error');
        let isValid = true;
        const customerName = customerNameInput.value.trim();
        const amountPaid = parseFloat(amountPaidInput.value);
        const paymentMode = paymentModeSelect.value;
        const totalCost = currentSaleItems.reduce((sum, item) => sum + (item.sellingPrice * item.quantity), 0);
        const changeGiven = amountPaid - totalCost;

        if (currentSaleItems.length === 0) {
            manualSaleFormMessage.textContent = 'Please add items to the sale.';
            manualSaleFormMessage.classList.add('error');
            isValid = false;
        }
        if (!validateAmount('amountPaid', amountPaid)) {
            isValid = false;
        }
        if (amountPaid < totalCost) {
            displayFieldError('amountPaid', 'Amount paid is less than total cost.');
            isValid = false;
        }
        if (!isValid) {
            setTimeout(() => {
                manualSaleFormMessage.classList.remove('success', 'error');
                manualSaleFormMessage.textContent = '';
            }, 5000);
            return;
        }
        const saleData = {
            customer_name: customerName || null,
            amount_paid: amountPaid,
            change_given: changeGiven,
            payment_mode: paymentMode,
            total_cost: totalCost,
            items_sold: currentSaleItems.map(item => ({
                product_variant_id: item.variantId,
                quantity: item.quantity,
                price_at_sale: item.sellingPrice
            }))
        };
        try {
            const response = await fetch('/api/manual-sale', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(saleData)
            });
            const result = await response.json();
            if (response.ok && result.status === 'success') {
                manualSaleFormMessage.textContent = result.message || 'Sale recorded successfully!';
                manualSaleFormMessage.classList.remove('error');
                manualSaleFormMessage.classList.add('success');
                currentSaleItems = [];
                renderSaleItems();
                customerNameInput.value = '';
                amountPaidInput.value = '';
                calculateChange();
            } else {
                manualSaleFormMessage.textContent = result.message || 'Error recording sale. Please try again.';
                manualSaleFormMessage.classList.remove('success');
                manualSaleFormMessage.classList.add('error');
            }
        } catch (error) {
            manualSaleFormMessage.textContent = 'Network error. Please try again.';
            manualSaleFormMessage.classList.add('error');
        } finally {
            setTimeout(() => {
                manualSaleFormMessage.classList.remove('success', 'error');
                manualSaleFormMessage.textContent = '';
            }, 5000);
        }
    });

    renderSaleItems();
    calculateChange();
});
