/* ShopSense Multi-Vendor Application Controller & Marketplace Intelligence Engine */

let currentUser = null; // { id, name, owner_name, email, role }
let currentView = 'dashboard';
let allCatalogProducts = [];

const DEFAULT_SVG_PLACEHOLDER = "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22400%22%20height%3D%22300%22%20viewBox%3D%220%200%20400%20300%22%3E%3Crect%20width%3D%22400%22%20height%3D%22300%22%20fill%3D%22%23f1f5f9%22%2F%3E%3Ccircle%20cx%3D%22200%22%20cy%3D%22120%22%20r%3D%2232%22%20fill%3D%22%23cbd5e1%22%2F%3E%3Cpath%20d%3D%22M150%20200c0-28%2022-50%2050-50s50%2022%2050%2050%22%20fill%3D%22%23cbd5e1%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2282%25%22%20dominant-baseline%3D%22middle%22%20text-anchor%3D%22middle%22%20fill%3D%22%2364748b%22%20font-family%3D%22sans-serif%22%20font-size%3D%2214%22%20font-weight%3D%22600%22%3ENo%20Image%3C%2Ftext%3E%3C%2Fsvg%3E";

function handleImgError(img) {
    img.onerror = null;
    img.src = DEFAULT_SVG_PLACEHOLDER;
}

// Toast Notification System
function showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <div style="font-size: 18px;">${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</div>
        <div style="flex: 1;">
            <div style="font-size: 13px; font-weight: 700; color: var(--dark-slate);">${title}</div>
            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">${message}</div>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

document.addEventListener('DOMContentLoaded', () => {
    const storedAdmin = localStorage.getItem('shopsense_admin');
    const storedVendor = localStorage.getItem('shopsense_vendor');

    if (storedAdmin) {
        try {
            const aObj = JSON.parse(storedAdmin);
            currentUser = { id: 'admin', name: aObj.name || 'System Admin', email: aObj.email, role: 'Admin' };
        } catch (e) {
            currentUser = { id: 'admin', name: 'System Admin', email: 'admin@shopsense.com', role: 'Admin' };
        }
    } else if (storedVendor) {
        try {
            const vObj = JSON.parse(storedVendor);
            currentUser = { 
                id: vObj.id, 
                name: vObj.name, 
                owner_name: vObj.owner_name || vObj.name,
                email: vObj.email, 
                role: 'Vendor' 
            };
        } catch (e) {
            window.location.href = '/frontend/login.html';
            return;
        }
    } else {
        window.location.href = '/frontend/login.html';
        return;
    }

    applyPortalBranding();
    navigate('dashboard');
    initRealtimeWebSocket();
    initNotificationBell();
});

function applyPortalBranding() {
    const displayName = currentUser.name || 'User';
    document.getElementById('userPillName').textContent = displayName;
    document.getElementById('userPillAvatar').textContent = displayName.substring(0, 2).toUpperCase();

    const isAdmin = currentUser.role === 'Admin';

    if (isAdmin) {
        // Hide Product Creation for Admin (Admin is not a seller)
        document.getElementById('topbarAddBtn').style.display = 'none';
        document.getElementById('heroAddBtn').style.display = 'none';
        document.getElementById('sidebarItemAddProduct').style.display = 'none';
        document.getElementById('vendorShortcutsRow').style.display = 'none';
        document.getElementById('vendorHealthPanel').style.display = 'none';

        // Show Admin Sections & Columns
        document.getElementById('sidebarItemVendors').style.display = 'block';
        document.getElementById('sectionAdminVendors').style.display = 'block';

        document.querySelectorAll('.admin-only-col').forEach(col => col.style.display = 'table-cell');

        // Admin Custom Texts
        document.getElementById('sidebarMenuLabel').textContent = "ADMIN CONTROL";
        document.getElementById('menuCatalogText').textContent = "Marketplace Catalog";
        document.getElementById('userPillRole').textContent = "Marketplace Admin";
        document.getElementById('heroTitle').textContent = "Welcome to ShopSense Admin Control Console 👋";
        document.getElementById('heroSubtext').textContent = "Overview of registered vendors, total revenue, stock values, and marketplace products.";
        
        document.getElementById('recentSectionTitle').textContent = "All Marketplace Products";
        document.getElementById('recentSectionSubtext').textContent = "Global product inventory from all registered vendors";
        document.getElementById('catalogPageTitle').textContent = "Global Marketplace Catalog";
        document.getElementById('catalogPageSubtext').textContent = "View, monitor, and organize products from all registered marketplace vendors.";
    } else {
        // Show Vendor Product Creation & Shortcuts
        document.getElementById('topbarAddBtn').style.display = 'inline-flex';
        document.getElementById('heroAddBtn').style.display = 'inline-block';
        document.getElementById('sidebarItemAddProduct').style.display = 'block';
        document.getElementById('vendorShortcutsRow').style.display = 'flex';
        document.getElementById('vendorHealthPanel').style.display = 'block';

        // Hide Admin Sections & Columns
        document.getElementById('sidebarItemVendors').style.display = 'none';
        document.getElementById('sectionAdminVendors').style.display = 'none';

        document.querySelectorAll('.admin-only-col').forEach(col => col.style.display = 'none');

        // Vendor Texts
        document.getElementById('sidebarMenuLabel').textContent = "VENDOR WORKSPACE";
        document.getElementById('menuCatalogText').textContent = "Inventory";
        document.getElementById('userPillRole').textContent = "Verified Merchant";
        document.getElementById('heroTitle').textContent = "Welcome to your ShopSense Vendor Workspace 👋";
        document.getElementById('heroSubtext').textContent = "Here is your live store performance, sales summary, and inventory overview.";
        
        document.getElementById('recentSectionTitle').textContent = "Recent Inventory Items";
        document.getElementById('recentSectionSubtext').textContent = "Newly added items in your store inventory";
        document.getElementById('catalogPageTitle').textContent = "My Inventory Catalog";
        document.getElementById('catalogPageSubtext').textContent = "Manage, edit, and organize all your store items.";
    }
}

function navigate(viewId) {
    currentView = viewId;

    const navMap = {
        'dashboard': 'menuDashboard',
        'vendors': 'menuVendors',
        'catalog': 'menuCatalog',
        'add-product': 'menuAddProduct',
        'analytics': 'menuAnalytics',
        'reports': 'menuReports',
        'media': 'menuMedia',
        'settings': 'menuSettings'
    };

    Object.keys(navMap).forEach(v => {
        const el = document.getElementById(navMap[v]);
        if (el) {
            if (v === viewId) el.classList.add('active');
            else el.classList.remove('active');
        }
    });

    const pageMap = {
        'dashboard': 'pageDashboard',
        'vendors': 'pageVendors',
        'catalog': 'pageCatalog',
        'add-product': 'pageAddProduct',
        'analytics': 'pageAnalytics',
        'reports': 'pageReports',
        'media': 'pageMedia',
        'settings': 'pageSettings'
    };

    Object.keys(pageMap).forEach(v => {
        const el = document.getElementById(pageMap[v]);
        if (el) {
            if (v === viewId) el.style.display = 'block';
            else el.style.display = 'none';
        }
    });

    if (viewId === 'dashboard') fetchDashboardData();
    if (viewId === 'vendors') fetchVendorsData();
    if (viewId === 'catalog') fetchCatalogData();
    if (viewId === 'analytics') fetchAnalyticsData();
    if (viewId === 'reports') loadReports();
    if (viewId === 'media') fetchMediaData();
    if (viewId === 'settings') populateSettingsData();
    if (viewId === 'analytics') fetchAnalyticsData();
}

async function fetchDashboardData() {
    const isAdmin = currentUser && currentUser.role === 'Admin';
    const grid = document.getElementById('statsCardsGrid');

    try {
        if (isAdmin) {
            // Fetch Admin Metrics from REST API /admin/dashboard
            const stats = await API.getAdminDashboardMetrics();

            grid.innerHTML = `
                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-emerald">👥</div>
                        <span class="stat-trend" style="background: #ecfdf5; color: #059669; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">${stats.active_vendors} Active</span>
                    </div>
                    <div class="stat-number">${stats.total_vendors}</div>
                    <div class="stat-title">Total Registered Vendors</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-blue">📦</div>
                        <span class="stat-trend">+14%</span>
                    </div>
                    <div class="stat-number">${stats.total_products}</div>
                    <div class="stat-title">Total Products</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-indigo">💰</div>
                        <span class="stat-trend">Gross Revenue</span>
                    </div>
                    <div class="stat-number">$${stats.total_revenue.toFixed(2)}</div>
                    <div class="stat-title">Total Revenue</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-amber">🏷️</div>
                        <span class="stat-trend" style="color: #b45309;">${stats.low_stock_products} Low Stock</span>
                    </div>
                    <div class="stat-number">$${stats.stock_value.toFixed(2)}</div>
                    <div class="stat-title">Total Stock Value</div>
                </div>
            `;

            // Fetch Vendors List from PostgreSQL
            const vendors = await API.getAdminVendors();
            renderVendorsTable('adminVendorsTableBody', vendors);

            // Fetch All Products across all vendors from /admin/products
            const products = await API.getAdminProducts();
            const tbody = document.getElementById('dashboardTableBody');
            tbody.innerHTML = '';

            if (!products || products.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">No registered products in marketplace database yet.</td></tr>`;
                return;
            }

            products.slice(0, 5).forEach(p => {
                tbody.appendChild(buildCatalogTableRow(p, true));
            });
        } else {
            // Fetch Vendor Metrics from REST API /analytics/dashboard
            const stats = await API.getDashboardMetrics(currentUser.id);
            const products = await API.getProducts(currentUser.id);

            // Calculate Inventory Health Summary
            let availCount = 0, lowCount = 0, outCount = 0;
            let stockValSum = 0;

            products.forEach(p => {
                stockValSum += (p.price * p.stock_quantity);
                if (p.stock_quantity > 20) availCount++;
                else if (p.stock_quantity >= 10) lowCount++;
                else outCount++;
            });

            document.getElementById('healthAvailableCount').textContent = availCount;
            document.getElementById('healthLowCount').textContent = lowCount;
            document.getElementById('healthOutCount').textContent = outCount;

            grid.innerHTML = `
                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-emerald">📦</div>
                        <span class="stat-trend">+14.2%</span>
                    </div>
                    <div class="stat-number">${stats.products_listed}</div>
                    <div class="stat-title">Products Sold / Listed</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-blue">💰</div>
                        <span class="stat-trend">+18.5%</span>
                    </div>
                    <div class="stat-number">$${stats.sale_revenue.toFixed(2)}</div>
                    <div class="stat-title">Today's / Gross Revenue</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-indigo">📊</div>
                        <span class="stat-trend">+5.4%</span>
                    </div>
                    <div class="stat-number">${stats.total_transactions}</div>
                    <div class="stat-title">Total Transactions</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-amber">🛍️</div>
                        <span class="stat-trend">AOV</span>
                    </div>
                    <div class="stat-number">$${(stats.total_transactions > 0 ? stats.sale_revenue / stats.total_transactions : 0).toFixed(2)}</div>
                    <div class="stat-title">Average Order Value</div>
                </div>

                <div class="stat-card-modern">
                    <div class="stat-header">
                        <div class="stat-icon-badge stat-badge-amber">🏷️</div>
                        <span class="stat-trend">Inventory Value</span>
                    </div>
                    <div class="stat-number">$${stockValSum.toFixed(2)}</div>
                    <div class="stat-title">Total Stock Value</div>
                </div>
            `;

            const tbody = document.getElementById('dashboardTableBody');
            tbody.innerHTML = '';

            if (!products || products.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">No products found for your store in database. Click "+ Add Product" to create an item!</td></tr>`;
                return;
            }

            products.slice(0, 5).forEach(p => {
                tbody.appendChild(buildCatalogTableRow(p, false));
            });
        }
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

async function fetchVendorsData() {
    try {
        const vendors = await API.getAdminVendors();
        renderVendorsTable('fullVendorsTableBody', vendors);
    } catch (err) {
        console.error("Vendors data error:", err);
    }
}

function renderVendorsTable(tbodyId, vendorsList) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!vendorsList || vendorsList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">No registered vendors found in PostgreSQL database.</td></tr>`;
        return;
    }

    vendorsList.forEach(v => {
        const tr = document.createElement('tr');
        const isAct = v.is_active !== false;
        const statusBadge = isAct ? `<span class="status-badge-available">Active</span>` : `<span class="status-badge-outofstock">Disabled</span>`;
        const toggleBtn = isAct 
            ? `<button class="btn-act btn-act-disable" onclick="executeToggleVendorStatus(${v.id}, false)">Disable</button>`
            : `<button class="btn-act btn-act-enable" onclick="executeToggleVendorStatus(${v.id}, true)">Enable</button>`;

        tr.innerHTML = `
            <td>
                <div style="font-weight: 700; color: var(--dark-slate);">${v.name}</div>
                <div style="font-size: 11px; color: var(--text-muted);">Vendor ID: #${v.id}</div>
            </td>
            <td><strong>${v.owner_name || v.name}</strong></td>
            <td>${v.email}</td>
            <td>${v.phone || 'N/A'}</td>
            <td><strong style="color: var(--primary);">${v.products_count} items</strong></td>
            <td><strong style="color: var(--primary);">${v.products_sold || 0} items</strong></td>
            <td>${statusBadge}</td>
            <td>
                <div class="action-btns">
                    ${toggleBtn}
                    <button class="btn-act btn-act-delete" onclick="executeDeleteVendor(${v.id})">Delete</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function executeToggleVendorStatus(vendorId, isActive) {
    try {
        await API.updateVendorStatus(vendorId, isActive);
        showToast("Vendor Status Updated", `Vendor #${vendorId} set to ${isActive ? 'Active' : 'Disabled'}.`, "info");
        fetchVendorsData();
        if (currentView === 'dashboard') fetchDashboardData();
    } catch (err) {
        showToast("Action Failed", err.message, "error");
    }
}

async function executeDeleteVendor(vendorId) {
    if (!confirm("Are you sure you want to delete this vendor store and all their products?")) return;
    try {
        await API.deleteVendor(vendorId);
        showToast("Vendor Removed", `Vendor store #${vendorId} deleted successfully.`, "success");
        fetchVendorsData();
        if (currentView === 'dashboard') fetchDashboardData();
    } catch (err) {
        showToast("Action Failed", err.message, "error");
    }
}

async function fetchCatalogData() {
    const isAdmin = currentUser && currentUser.role === 'Admin';

    try {
        if (isAdmin) {
            allCatalogProducts = await API.getAdminProducts();
        } else {
            allCatalogProducts = await API.getProducts(currentUser.id);
        }
        renderCatalogRows(allCatalogProducts);
    } catch (err) {
        console.error("Catalog error:", err);
    }
}

function renderCatalogRows(productsList) {
    const tbody = document.getElementById('fullCatalogTableBody');
    tbody.innerHTML = '';

    if (!productsList || productsList.length === 0) {
        const colspan = (currentUser && currentUser.role === 'Admin') ? "7" : "6";
        tbody.innerHTML = `<tr><td colspan="${colspan}" style="text-align: center; color: var(--text-muted); padding: 30px;">No catalog products found in database.</td></tr>`;
        return;
    }

    const isAdmin = currentUser && currentUser.role === 'Admin';
    productsList.forEach(p => {
        tbody.appendChild(buildCatalogTableRow(p, isAdmin));
    });
}

function buildCatalogTableRow(product, showVendorName = false) {
    const src = (product.image_url && product.image_url.trim() !== '') ? product.image_url : DEFAULT_SVG_PLACEHOLDER;
    const desc = product.description && product.description.trim() !== '' ? product.description : "No description provided.";
    
    // Inventory Status Calculation Rules
    let statusBadge = "";
    if (product.stock_quantity > 20) {
        statusBadge = `<span class="status-badge-available">Available</span>`;
    } else if (product.stock_quantity >= 10) {
        statusBadge = `<span class="status-badge-lowstock">⚠️ Low Stock (${product.stock_quantity} left)</span>`;
    } else {
        statusBadge = `<span class="status-badge-outofstock">🚨 Out of Stock Warning (${product.stock_quantity} left)</span>`;
    }

    const vName = product.vendor_name || `Vendor #${product.vendor_id}`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>
            <div class="table-product-box">
                <img src="${src}" class="table-product-thumb" alt="${product.name}" onerror="handleImgError(this)">
                <div class="table-product-info">
                    <span class="table-product-name">${product.name}</span>
                    <span class="table-product-desc">${desc}</span>
                </div>
            </div>
        </td>
        ${showVendorName ? `<td class="admin-only-col"><strong style="color: var(--dark-slate);">${vName}</strong></td>` : ''}
        <td>
            <span class="category-pill">${product.category || 'General'}</span>
        </td>
        <td>
            <span class="price-text">$${parseFloat(product.price).toFixed(2)}</span>
        </td>
        <td>
            <span class="stock-count">${product.stock_quantity}</span>
        </td>
        <td>
            ${statusBadge}
        </td>
        <td>
            <div class="action-btns">
                <button class="btn-act btn-act-view" onclick="openViewModal(${product.id})">👁 View</button>
                <button class="btn-act btn-act-edit" onclick="openEditModal(${product.id})">✏️ Edit</button>
                <button class="btn-act btn-act-delete" onclick="executeDeleteProduct(${product.id})">🗑️ Delete</button>
            </div>
        </td>
    `;
    return tr;
}

function handleCatalogSearch() {
    const query = document.getElementById('catalogSearchInput').value.toLowerCase().trim();
    const catFilter = document.getElementById('filterCategory').value.toLowerCase();
    const sortP = document.getElementById('sortPrice').value;
    const sortS = document.getElementById('sortStock').value;

    let filtered = [...allCatalogProducts];

    if (query) {
        filtered = filtered.filter(p => 
            (p.name && p.name.toLowerCase().includes(query)) ||
            (p.category && p.category.toLowerCase().includes(query)) ||
            (p.vendor_name && p.vendor_name.toLowerCase().includes(query)) ||
            (p.tags && p.tags.toLowerCase().includes(query))
        );
    }

    if (catFilter) {
        filtered = filtered.filter(p => p.category && p.category.toLowerCase().includes(catFilter));
    }

    if (sortP === 'low-high') {
        filtered.sort((a, b) => a.price - b.price);
    } else if (sortP === 'high-low') {
        filtered.sort((a, b) => b.price - a.price);
    }

    if (sortS === 'low-stock') {
        filtered.sort((a, b) => a.stock_quantity - b.stock_quantity);
    } else if (sortS === 'high-stock') {
        filtered.sort((a, b) => b.stock_quantity - a.stock_quantity);
    }

    renderCatalogRows(filtered);
}

function handleGlobalSearch(query) {
    if (currentView !== 'catalog') navigate('catalog');
    document.getElementById('catalogSearchInput').value = query;
    handleCatalogSearch();
}

function openViewModal(productId) {
    const prod = allCatalogProducts.find(p => p.id === productId);
    if (!prod) return;

    const src = (prod.image_url && prod.image_url.trim() !== '') ? prod.image_url : DEFAULT_SVG_PLACEHOLDER;
    const imgElem = document.getElementById('viewImg');
    imgElem.src = src;
    imgElem.onerror = () => { imgElem.src = DEFAULT_SVG_PLACEHOLDER; };

    let statusText = "Available";
    if (prod.stock_quantity <= 20 && prod.stock_quantity >= 10) statusText = "Low Stock ⚠️";
    else if (prod.stock_quantity < 10) statusText = "Out of Stock Warning 🚨";

    document.getElementById('viewName').textContent = prod.name;
    document.getElementById('viewCategory').textContent = prod.category || 'General';
    document.getElementById('viewPrice').textContent = `$${parseFloat(prod.price).toFixed(2)}`;
    document.getElementById('viewDesc').textContent = prod.description || "No description provided.";
    document.getElementById('viewStock').textContent = prod.stock_quantity;
    document.getElementById('viewStatusBadge').textContent = statusText;
    document.getElementById('viewId').textContent = `#${prod.id}`;
    document.getElementById('viewVendor').textContent = prod.vendor_name || `Vendor #${prod.vendor_id}`;

    document.getElementById('modalView').style.display = 'flex';
}

function closeViewModal() {
    document.getElementById('modalView').style.display = 'none';
}

function openEditModal(productId) {
    const prod = allCatalogProducts.find(p => p.id === productId);
    if (!prod) return;

    document.getElementById('editId').value = prod.id;
    document.getElementById('editName').value = prod.name;
    document.getElementById('editDesc').value = prod.description || '';
    document.getElementById('editPrice').value = prod.price;
    document.getElementById('editQty').value = prod.stock_quantity;
    document.getElementById('editCategory').value = prod.category || '';
    document.getElementById('editTags').value = prod.tags || '';
    document.getElementById('editImage').value = prod.image_url || '';

    document.getElementById('modalEdit').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('modalEdit').style.display = 'none';
}

async function executeSaveEditProduct(event) {
    event.preventDefault();
    const id = parseInt(document.getElementById('editId').value);
    
    const updatePayload = {
        name: document.getElementById('editName').value.trim(),
        description: document.getElementById('editDesc').value.trim(),
        price: parseFloat(document.getElementById('editPrice').value),
        stock_quantity: parseInt(document.getElementById('editQty').value),
        category: document.getElementById('editCategory').value.trim(),
        tags: document.getElementById('editTags').value.trim(),
        image_url: document.getElementById('editImage').value.trim()
    };

    try {
        const response = await fetch(`${window.location.origin}/products/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatePayload)
        });
        if (!response.ok) throw new Error('Failed to update product');
        
        showToast("Product Updated Successfully", `Listing #${id} updated in catalog.`, "success");
        closeEditModal();
        fetchCatalogData();
        if (currentView === 'dashboard') fetchDashboardData();
    } catch (err) {
        showToast("Update Error", err.message || 'Failed to update product', "error");
    }
}

async function executeAddProduct(event) {
    event.preventDefault();
    if (currentUser && currentUser.role === 'Admin') {
        showToast("Action Denied", "Admins are not sellers and cannot create products.", "warning");
        return;
    }

    const vid = currentUser ? currentUser.id : 1;
    const notice = document.getElementById('addNotice');

    const productPayload = {
        name: document.getElementById('inName').value.trim(),
        description: document.getElementById('inDesc').value.trim(),
        price: parseFloat(document.getElementById('inPrice').value),
        stock_quantity: parseInt(document.getElementById('inQty').value),
        category: document.getElementById('inCategory').value.trim(),
        tags: document.getElementById('inTags').value.trim(),
        image_url: document.getElementById('inImage').value.trim()
    };

    try {
        await API.createProduct(productPayload, vid);
        showToast("Product Added Successfully", `"${productPayload.name}" added to inventory catalog.`, "success");
        notice.style.display = 'block';
        notice.style.background = '#ecfdf5';
        notice.style.color = '#065f46';
        notice.style.border = '1px solid #a7f3d0';
        notice.textContent = 'Product successfully published to store inventory!';

        document.getElementById('createProdForm').reset();

        setTimeout(() => {
            notice.style.display = 'none';
            navigate('catalog');
        }, 1000);
    } catch (err) {
        showToast("Failed to Add Product", err.message || 'Error publishing item', "error");
    }
}

async function executeDeleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product listing?')) return;
    try {
        await API.deleteProduct(productId);
        showToast("Product Deleted", `Product listing #${productId} removed.`, "info");
        fetchCatalogData();
        if (currentView === 'dashboard') fetchDashboardData();
    } catch (err) {
        showToast("Delete Error", 'Failed to delete item', "error");
    }
}

async function executeForecast() {
    const id = document.getElementById('forecastId').value;
    const box = document.getElementById('forecastBox');
    if (!id) {
        alert("Please select a product");
        return;
    }

    try {
        const data = await API.runForecast(id);
        box.style.display = 'block';

        let listItems = data.forecast.map(p => `<div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px;"><span>${p.day}</span><strong style="color: var(--primary);">${p.predicted_sales} units</strong></div>`).join('');
        
        let listHtml = listItems ? `<div style="margin-bottom: 12px; background: #fff; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color);">${listItems}</div>` : '';

        box.innerHTML = `
            <div style="font-weight: 800; font-size: 15px; color: var(--dark-slate); margin-bottom: 8px;">Product: ${data.product_name} (Current Stock: ${data.current_stock})</div>
            ${listHtml}
            <div style="font-weight: 700; color: #065f46; background: #dcfce7; padding: 8px 12px; border-radius: 6px; font-size: 12px;">${data.recommendation}</div>
        `;
    } catch (err) {
        box.style.display = 'block';
        box.innerHTML = `<span style="color: #dc2626;">${err.message || 'Forecast error'}</span>`;
    }
}

async function executeSentiment() {
    const id = document.getElementById('sentProdId').value;
    const rating = document.getElementById('sentRating').value;
    const text = document.getElementById('sentText').value;
    const box = document.getElementById('sentimentBox');

    if (!id || !rating || !text) {
        alert("Please complete all fields for sentiment evaluation");
        return;
    }

    try {
        const res = await API.analyzeSentiment(id, rating, text);
        box.style.display = 'block';

        const prosHtml = res.top_pros && res.top_pros.length > 0 ? 
            `<div style="margin-top: 8px;"><strong>Top Pros:</strong> <span style="color: #059669;">${res.top_pros.join(', ')}</span></div>` : '';
            
        const consHtml = res.top_cons && res.top_cons.length > 0 ? 
            `<div style="margin-top: 4px;"><strong>Top Cons:</strong> <span style="color: #dc2626;">${res.top_cons.join(', ')}</span></div>` : '';

        box.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-weight: 800; font-size: 15px;">Analysis Score:</span>
                <span style="background: #dcfce7; color: #065f46; padding: 4px 12px; border-radius: 12px; font-weight: 800; font-size: 12px;">${res.sentiment} (${(res.confidence_score*100).toFixed(0)}%)</span>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4; margin-bottom: 8px;">${res.summary}</p>
            <div style="font-size: 12px; border-top: 1px solid var(--border-color); padding-top: 8px;">
                ${prosHtml}
                ${consHtml}
            </div>
        `;
    } catch (err) {
        box.style.display = 'block';
        box.innerHTML = `<span style="color: #dc2626;">${err.message || 'Sentiment error'}</span>`;
    }
}

function populateSettingsData() {
    const nameInput = document.getElementById('settingsName');
    const emailInput = document.getElementById('settingsEmail');
    if (nameInput && currentUser) nameInput.value = currentUser.name || 'User Account';
    if (emailInput && currentUser) emailInput.value = currentUser.email || 'user@shopsense.com';
}

async function fetchMediaData() {
    const isVendor = currentUser && currentUser.role === 'Vendor';
    const targetVendorId = isVendor ? currentUser.id : null;

    try {
        const products = await API.getProducts(targetVendorId);
        const grid = document.getElementById('mediaAssetGrid');
        grid.innerHTML = '';

        if (!products || products.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted);">No image assets in media library.</div>`;
            return;
        }

        products.forEach(p => {
            const url = (p.image_url && p.image_url.trim() !== '') ? p.image_url : DEFAULT_SVG_PLACEHOLDER;
            const div = document.createElement('div');
            div.className = 'stat-card-modern';
            div.innerHTML = `
                <div style="height: 140px; background: #f8fafc; overflow: hidden; border-radius: var(--radius-md); margin-bottom: 12px;">
                    <img src="${url}" style="width: 100%; height: 100%; object-fit: cover;" alt="${p.name}" onerror="handleImgError(this)">
                </div>
                <div style="text-align: center;">
                    <h5 style="font-size: 14px; font-weight: 700;">${p.name}</h5>
                    ${p.image_url && p.image_url.trim() !== '' ? `<button onclick="navigator.clipboard.writeText('${p.image_url}'); showToast('Copied', 'Image URL copied to clipboard.', 'info');" style="margin-top: 6px; padding: 4px 10px; background: #f1f5f9; border: none; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer;">Copy Image URL</button>` : `<span style="font-size: 11px; color: var(--text-muted);">No external URL</span>`}
                </div>
            `;
            grid.appendChild(div);
        });
    } catch (err) {
        console.error("Media error:", err);
    }
}

async function fetchAnalyticsData() {
    if (!currentUser) return;
    const isVendor = currentUser.role === 'Vendor';
    const targetVendorId = isVendor ? currentUser.id : null;

    try {
        if (isVendor) {
            // Fetch Customer Segmentation
            const customerData = await API.getCustomerSegmentation(targetVendorId);
            const segmentBox = document.getElementById('customerSegmentsBox');
            if (customerData.segments) {
                segmentBox.innerHTML = customerData.segments.map(s => `
                <div class="glass-panel">
                    <h4 style="font-size: 16px; font-weight: 800; margin-bottom: 8px;">${s.segment_name}</h4>
                    <div style="font-size: 24px; font-weight: 800; color: var(--primary); margin-bottom: 4px;">${s.customer_count} Customers</div>
                    <div style="font-size: 14px; color: var(--dark-slate); font-weight: 700; margin-bottom: 8px;">$${s.total_spending.toFixed(2)} Total Spent</div>
                    <p style="font-size: 12px; color: var(--text-secondary);">${s.description}</p>
                </div>
            `).join('');
        }

        // Fetch Recommendations
        const recData = await API.getRecommendations(currentUser.id);
        const recBox = document.getElementById('recommendationsBox');
        if (recData.recommendations && recData.recommendations.length > 0) {
            recBox.innerHTML = recData.recommendations.map(r => `
                <div class="glass-panel" style="background: linear-gradient(145deg, #ffffff, #f1f5f9);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="font-size: 12px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase;">${r.category}</span>
                        <span style="font-size: 12px; background: #dcfce7; color: #059669; padding: 2px 8px; border-radius: 12px; font-weight: 700;">Top Pick</span>
                    </div>
                    <h4 style="font-size: 16px; font-weight: 800; margin-bottom: 6px;">${r.product_name}</h4>
                    <p style="font-size: 13px; color: var(--text-secondary);">${r.reason}</p>
                </div>
            `).join('');
            } else {
                recBox.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted);">No recommendations available yet. Try seeding test data.</div>`;
            }
        }
    } catch (err) {
        console.error("Failed to load analytics data:", err);
    }
    
    // Load products into ARIMA dropdowns
    try {
        console.log("Fetching products for vendor ID:", targetVendorId);
        const products = await API.getProducts(targetVendorId);
        console.log("Products API response:", products);
        
        const fSelect = document.getElementById('forecastId');
        const sSelect = document.getElementById('sentProdId');
        
        console.log("Found DOM elements - fSelect:", !!fSelect, "sSelect:", !!sSelect);
        
        let options = '<option value="">Select Product...</option>';
        if (Array.isArray(products)) {
            products.forEach(p => {
                options += `<option value="${p.id}">${p.name} (ID: ${p.id})</option>`;
            });
        } else {
            console.error("Products is not an array:", products);
        }
        
        if (fSelect) fSelect.innerHTML = options;
        if (sSelect) sSelect.innerHTML = options;
        
        console.log("Dropdowns successfully populated.");
    } catch (e) {
        console.error("Failed to load products for dropdown:", e);
    }
}

async function executeSeedData() {
    if (!currentUser || currentUser.role !== 'Vendor') return;
    try {
        const res = await API.seedHistoricalData(currentUser.id);
        showToast('Data Seeded', `Added ${res.customers_added} customers and ${res.transactions_added} transactions.`, 'success');
        fetchAnalyticsData();
        fetchDashboardData();
    } catch (err) {
        showToast('Error', err.message || 'Failed to seed data', 'error');
    }
}

function executeLogout() {
    localStorage.removeItem('shopsense_token');
    localStorage.removeItem('shopsense_vendor');
    localStorage.removeItem('shopsense_admin');
    localStorage.removeItem('shopsense_admin_token');
    window.location.href = '/frontend/login.html';
}


let revenueChartInstance = null;
let unitsChartInstance = null;
let performanceChartInstance = null;

let topProductsChartInstance = null;

async function loadReports() {
    if (!currentUser) return;
    initAnalystChips();
    const isAdmin = currentUser.role === 'Admin';
    const targetVendorId = isAdmin ? null : currentUser.id;

    try {
        const data = await API.getReportsData(targetVendorId);

        // Update New KPI Cards
        // (Removed from layout per final user request, but variables exist in API)
        const revTotal = '$' + parseFloat(data.total_revenue || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

        // Revenue Trend Chart
        const trendDates = data.trends.map(t => t.date);
        const trendRevenues = data.trends.map(t => t.revenue);
        const trendUnits = data.trends.map(t => t.units_sold);

        if (revenueChartInstance) revenueChartInstance.destroy();
        const ctxRev = document.getElementById('revenueChart').getContext('2d');
        revenueChartInstance = new Chart(ctxRev, {
            type: 'line',
            data: {
                labels: trendDates,
                datasets: [{
                    label: 'Revenue ($)',
                    data: trendRevenues,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // Units Sold Trend Chart
        if (unitsChartInstance) unitsChartInstance.destroy();
        const ctxUnits = document.getElementById('unitsChart').getContext('2d');
        unitsChartInstance = new Chart(ctxUnits, {
            type: 'bar',
            data: {
                labels: trendDates,
                datasets: [{
                    label: 'Units Sold',
                    data: trendUnits,
                    backgroundColor: '#16a34a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // Top Products by Sales Chart
        // Sort products descending by units_sold and take top 5
        const sortedProducts = [...data.products].sort((a, b) => b.units_sold - a.units_sold).slice(0, 5);
        const topProdNames = sortedProducts.map(p => p.product_name.substring(0, 20) + (p.product_name.length > 20 ? '...' : ''));
        const topProdUnits = sortedProducts.map(p => p.units_sold);

        if (topProductsChartInstance) topProductsChartInstance.destroy();
        const ctxTop = document.getElementById('topProductsChart').getContext('2d');
        topProductsChartInstance = new Chart(ctxTop, {
            type: 'bar',
            data: {
                labels: topProdNames,
                datasets: [{
                    label: 'Units Sold',
                    data: topProdUnits,
                    backgroundColor: '#3b82f6'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: true }
                }
            }
        });

        // Product / Category Performance Chart (Doughnut)
        const catNames = data.categories.map(c => c.category);
        const catRevenues = data.categories.map(c => c.revenue);
        
        if (performanceChartInstance) performanceChartInstance.destroy();
        const ctxPerf = document.getElementById('performanceChart').getContext('2d');
        performanceChartInstance = new Chart(ctxPerf, {
            type: 'doughnut',
            data: {
                labels: catNames,
                datasets: [{
                    data: catRevenues,
                    backgroundColor: [
                        '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981', '#06b6d4', '#64748b'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Recent Transactions Table
        const txBody = document.getElementById('recentTransactionsBody');
        txBody.innerHTML = '';
        if (data.recent_transactions && data.recent_transactions.length > 0) {
            data.recent_transactions.forEach(tx => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">${tx.date}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">${tx.product_name.substring(0, 15)}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">${tx.quantity}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: 600; color: #059669;">$${tx.amount.toFixed(2)}</td>
                `;
                txBody.appendChild(tr);
            });
        } else {
            txBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 10px; color: var(--text-muted);">No recent transactions</td></tr>`;
        }

    } catch (err) {
        console.error('Failed to load reports data:', err);
    }
}

function downloadReportsExcel() {
    if (!currentUser) return;
    const isAdmin = currentUser.role === 'Admin';
    const targetVendorId = isAdmin ? null : currentUser.id;
    API.downloadReportsExcel(targetVendorId);
}

// -------------------------------------------------------------
// Advanced Feature 3: Hybrid AI Business Data Analyst
// -------------------------------------------------------------
function initAnalystChips() {
    const chipsContainer = document.getElementById('analystChips');
    if (!chipsContainer || chipsContainer.children.length > 0) return;

    const isAdmin = currentUser && currentUser.role === 'Admin';
    const suggestions = isAdmin ? [
        "What was the total marketplace revenue?",
        "Which vendor generated the most revenue?",
        "What was the best sold product?",
        "What are the latest smartphones?",
        "Which category generated the highest revenue?",
        "Compare my product performance with current market trends"
    ] : [
        "What was the best sold product?",
        "What's our total revenue?",
        "What should I restock?",
        "What are the latest smartphones?",
        "Which phone is best under ₹50,000?",
        "What are the current market trends and how can my store benefit?"
    ];

    chipsContainer.innerHTML = suggestions.map(q => `
        <button type="button" class="analyst-chip-btn" onclick="selectAnalystQuery('${q.replace(/'/g, "\\'")}')" 
            onmouseover="this.style.background='#e0e7ff'; this.style.borderColor='#818cf8'" 
            onmouseout="this.style.background='#ffffff'; this.style.borderColor='#cbd5e1'"
            style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 9999px; padding: 6px 14px; font-size: 12px; color: #334155; cursor: pointer; font-weight: 500; transition: all 0.2s ease;">
            💬 ${q}
        </button>
    `).join('');
}

function selectAnalystQuery(query) {
    const input = document.getElementById('analystQuestionInput');
    if (input) {
        input.value = query;
        handleAskAnalyst(null, query);
    }
}

async function handleAskAnalyst(event, directQuery = null) {
    if (event) event.preventDefault();
    if (!currentUser) return;

    const input = document.getElementById('analystQuestionInput');
    const question = directQuery || (input ? input.value.trim() : '');
    if (!question) return;

    const submitBtn = document.getElementById('analystSubmitBtn');
    const responseCard = document.getElementById('analystResponseCard');
    const answerText = document.getElementById('analystAnswerText');
    const sourceBadge = document.getElementById('analystSourceBadge');
    const sqlBadge = document.getElementById('analystSqlBadge');
    const tableWrapper = document.getElementById('analystTableWrapper');
    const tableHead = document.getElementById('analystTableHead');
    const tableBody = document.getElementById('analystTableBody');
    const citationsBox = document.getElementById('analystCitationsBox');
    const citationsList = document.getElementById('analystCitationsList');

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Thinking... ⏳</span>';
    }

    if (responseCard) responseCard.style.display = 'block';
    if (answerText) answerText.innerHTML = '<span style="color: #64748b; font-style: italic;">Analyzing data sources and generating response...</span>';
    if (sourceBadge) sourceBadge.style.display = 'none';
    if (sqlBadge) sqlBadge.style.display = 'none';
    if (tableWrapper) tableWrapper.style.display = 'none';
    if (citationsBox) citationsBox.style.display = 'none';

    try {
        const role = currentUser.role || 'Vendor';
        const vendorId = role === 'Admin' ? null : currentUser.id;

        const res = await API.askDataAnalyst(question, role, vendorId);

        // 1. Render Source Badge
        if (sourceBadge && res.source) {
            const srcLower = res.source.toLowerCase();
            let bg = '#ecfdf5', color = '#065f46', border = '#a7f3d0', icon = '📊';

            if (srcLower.includes('+') || (srcLower.includes('web') && srcLower.includes('business'))) {
                bg = '#f3e8ff'; color = '#6b21a8'; border = '#d8b4fe'; icon = '⚡';
            } else if (srcLower.includes('web')) {
                bg = '#e0e7ff'; color = '#3730a3'; border = '#a5b4fc'; icon = '🌐';
            } else if (srcLower.includes('concept') || srcLower.includes('clarif')) {
                bg = '#fffbeb'; color = '#92400e'; border = '#fde68a'; icon = '💡';
            }

            sourceBadge.textContent = `${icon} ${res.source}`;
            sourceBadge.style.background = bg;
            sourceBadge.style.color = color;
            sourceBadge.style.border = `1px solid ${border}`;
            sourceBadge.style.display = 'inline-block';
        }

        // 2. Render Answer Text
        if (answerText) {
            let formatted = (res.answer || 'No response returned.')
                .replace(/###\s*(.*)/g, '<div style="font-weight: 800; font-size: 15px; color: #1e1b4b; margin: 8px 0 4px;">$1</div>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
            answerText.innerHTML = formatted;
        }

        // 3. Render Executed SQL Badge (if applicable)
        if (res.sql_executed && sqlBadge) {
            sqlBadge.textContent = `SQL: ${res.sql_executed}`;
            sqlBadge.style.display = 'inline-block';
        } else if (sqlBadge) {
            sqlBadge.style.display = 'none';
        }

        // 4. Render Dynamic Table (if tabular data rows returned)
        if (res.data && Array.isArray(res.data) && res.data.length > 0 && tableWrapper && tableHead && tableBody) {
            const cols = Object.keys(res.data[0]);
            
            tableHead.innerHTML = `<tr>${cols.map(c => `<th style="padding: 8px 12px; background: #f8fafc; border-bottom: 2px solid #e2e8f0; text-align: left; text-transform: capitalize; font-weight: 700; color: #475569;">${c.replace(/_/g, ' ')}</th>`).join('')}</tr>`;

            tableBody.innerHTML = res.data.map(row => `
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    ${cols.map(c => {
                        let val = row[c];
                        if (val === null || val === undefined) val = '-';
                        else if (typeof val === 'number') {
                            if (c.toLowerCase().includes('revenue') || c.toLowerCase().includes('amount') || c.toLowerCase().includes('price')) {
                                val = '$' + val.toFixed(2);
                            }
                        }
                        return `<td style="padding: 8px 12px; color: #1e293b;">${val}</td>`;
                    }).join('')}
                </tr>
            `).join('');

            tableWrapper.style.display = 'block';
        } else if (tableWrapper) {
            tableWrapper.style.display = 'none';
        }

        // 5. Render Citations Box (if web sources returned)
        if (res.citations && Array.isArray(res.citations) && res.citations.length > 0 && citationsBox && citationsList) {
            citationsList.innerHTML = res.citations.map(c => `
                <div style="font-size: 11px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px 10px;">
                    <a href="${c.url}" target="_blank" rel="noopener noreferrer" style="font-weight: 700; color: #4f46e5; text-decoration: none;">
                        ${c.title} ↗
                    </a>
                    ${c.snippet ? `<div style="color: #64748b; margin-top: 2px; line-height: 1.3;">${c.snippet}</div>` : ''}
                </div>
            `).join('');
            citationsBox.style.display = 'block';
        } else if (citationsBox) {
            citationsBox.style.display = 'none';
        }

    } catch (err) {
        console.error('AI Analyst Error:', err);
        if (answerText) {
            answerText.innerHTML = `<span style="color: #dc2626;">Error: ${err.message || 'Failed to query AI Analyst.'}</span>`;
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Ask Analyst</span>';
        }
    }
}


// -------------------------------------------------------------
// Real-Time WebSocket Connection & Notification Handler
// -------------------------------------------------------------
let realtimeSocket = null;
let wsReconnectTimer = null;

function setWsStatus(connected, text = null) {
    const badge = document.getElementById('wsStatusBadge');
    const dot = document.getElementById('wsStatusDot');
    const statusText = document.getElementById('wsStatusText');
    if (!badge || !dot || !statusText) return;

    if (connected) {
        badge.style.color = '#059669';
        badge.style.background = '#ecfdf5';
        badge.style.borderColor = '#a7f3d0';
        dot.style.background = '#10b981';
        statusText.textContent = text || 'LIVE';
    } else {
        badge.style.color = '#d97706';
        badge.style.background = '#fffbeb';
        badge.style.borderColor = '#fde68a';
        dot.style.background = '#f59e0b';
        statusText.textContent = text || 'CONNECTING...';
    }
}

function initRealtimeWebSocket() {
    if (!currentUser) return;
    if (realtimeSocket && (realtimeSocket.readyState === WebSocket.OPEN || realtimeSocket.readyState === WebSocket.CONNECTING)) {
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const role = currentUser.role || 'Vendor';
    const vendorId = currentUser.role === 'Admin' ? '' : (currentUser.id || '');
    const wsUrl = `${protocol}//${host}/ws?role=${encodeURIComponent(role)}${vendorId ? `&vendor_id=${encodeURIComponent(vendorId)}` : ''}`;

    setWsStatus(false, 'CONNECTING...');

    try {
        realtimeSocket = new WebSocket(wsUrl);

        realtimeSocket.onopen = () => {
            console.log('[ShopSense WebSocket] Connected to real-time notification service');
            setWsStatus(true, 'LIVE');
            if (wsReconnectTimer) {
                clearTimeout(wsReconnectTimer);
                wsReconnectTimer = null;
            }
        };

        realtimeSocket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.event === 'new_sale') {
                    handleRealtimeSaleEvent(message.data);
                }
            } catch (err) {
                console.warn('[ShopSense WebSocket] Message parse error:', err);
            }
        };

        realtimeSocket.onclose = (event) => {
            console.log('[ShopSense WebSocket] Connection closed, retrying in 3s...', event.reason);
            setWsStatus(false, 'OFFLINE');
            if (!wsReconnectTimer) {
                wsReconnectTimer = setTimeout(() => {
                    wsReconnectTimer = null;
                    initRealtimeWebSocket();
                }, 3000);
            }
        };

        realtimeSocket.onerror = (err) => {
            console.warn('[ShopSense WebSocket] Error occurred:', err);
            setWsStatus(false, 'RECONNECTING');
        };

    } catch (e) {
        console.error('[ShopSense WebSocket] Setup failed:', e);
        setWsStatus(false, 'ERROR');
        if (!wsReconnectTimer) {
            wsReconnectTimer = setTimeout(() => {
                wsReconnectTimer = null;
                initRealtimeWebSocket();
            }, 5000);
        }
    }
}

// -------------------------------------------------------------
// Notification Bell & Dropdown Management
// -------------------------------------------------------------
let notifications = [];

function getNotifStorageKey() {
    return currentUser ? `shopsense_notifications_${currentUser.role}_${currentUser.id}` : 'shopsense_notifications_guest';
}

function loadSavedNotifications() {
    try {
        const saved = localStorage.getItem(getNotifStorageKey());
        notifications = saved ? JSON.parse(saved) : [];
    } catch (e) {
        notifications = [];
    }
}

function saveNotifications() {
    try {
        localStorage.setItem(getNotifStorageKey(), JSON.stringify(notifications));
    } catch (e) {
        console.warn('Failed to save notifications to localStorage:', e);
    }
}

function initNotificationBell() {
    loadSavedNotifications();
    updateNotificationBellUI();

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const bellWrap = document.getElementById('notificationBellWrap');
        const dropdown = document.getElementById('notifDropdown');
        if (bellWrap && dropdown && !bellWrap.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

function toggleNotificationDropdown() {
    const dropdown = document.getElementById('notifDropdown');
    if (!dropdown) return;

    const isVisible = dropdown.style.display === 'block';
    if (!isVisible) {
        dropdown.style.display = 'block';
        // Mark all as read when panel is opened
        notifications.forEach(n => { n.read = true; });
        saveNotifications();
        updateNotificationBellUI();
    } else {
        dropdown.style.display = 'none';
    }
}

function dismissNotification(event, notifId) {
    if (event) event.stopPropagation();
    notifications = notifications.filter(n => String(n.id) !== String(notifId));
    saveNotifications();
    updateNotificationBellUI();
}

function clearAllNotifications() {
    notifications = [];
    saveNotifications();
    updateNotificationBellUI();
}

function updateNotificationBellUI() {
    const badge = document.getElementById('notifBadge');
    const countLabel = document.getElementById('notifCountLabel');
    const list = document.getElementById('notifList');
    if (!badge || !list) return;

    const unreadCount = notifications.filter(n => !n.read).length;

    // Update unread count badge
    if (unreadCount > 0) {
        badge.style.display = 'inline-block';
        badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
    } else {
        badge.style.display = 'none';
    }

    if (countLabel) {
        countLabel.textContent = notifications.length;
    }

    // Render notifications list
    if (notifications.length === 0) {
        list.innerHTML = `
            <div id="emptyNotifMsg" style="padding: 24px; text-align: center; color: #94a3b8; font-size: 12px;">
                No notifications yet
            </div>
        `;
        return;
    }

    list.innerHTML = notifications.map(n => `
        <div style="padding: 10px 16px; border-bottom: 1px solid #f1f5f9; display: flex; gap: 10px; align-items: flex-start; background: ${n.read ? 'white' : '#f0fdf4'}; transition: background 0.15s;">
            <div style="font-size: 16px; margin-top: 2px;">🛍️</div>
            <div style="flex: 1; min-width: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                    <span style="font-size: 12px; font-weight: 700; color: #0f172a;">${n.title || 'New Order Received'}</span>
                    <span style="font-size: 10px; color: #94a3b8;">${n.timestamp || 'Just now'}</span>
                </div>
                <div style="font-size: 12px; color: #334155; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${n.product_name}">${n.product_name}</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 2px; display: flex; justify-content: space-between;">
                    <span>Qty: <strong>${n.quantity}</strong></span>
                    <span style="color: #059669; font-weight: 700;">$${n.total_amount}</span>
                </div>
            </div>
            <button onclick="dismissNotification(event, '${n.id}')" style="border: none; background: none; color: #94a3b8; font-size: 16px; cursor: pointer; padding: 0 4px; line-height: 1;" title="Dismiss">&times;</button>
        </div>
    `).join('');
}

function handleRealtimeSaleEvent(data) {
    const prodName = data.product_name || 'Product';
    const qty = data.quantity || 1;
    const amt = parseFloat(data.total_amount || 0).toFixed(2);
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. Add persistent notification to the bell system
    const newNotif = {
        id: data.transaction_id ? String(data.transaction_id) : String(Date.now()),
        title: "New Order Received",
        product_name: prodName,
        quantity: qty,
        total_amount: amt,
        time: "Just now",
        timestamp: timeStr,
        read: false
    };

    // Avoid duplicate if same transaction id is broadcast
    const existingIdx = notifications.findIndex(n => String(n.id) === String(newNotif.id));
    if (existingIdx === -1) {
        notifications.unshift(newNotif);
    } else {
        notifications[existingIdx] = newNotif;
    }

    saveNotifications();
    updateNotificationBellUI();

    // 2. Show live toast notification
    showToast(
        "New Sale Recorded 🎉",
        `${prodName} · Qty: ${qty} · $${amt}`,
        "success"
    );

    // 3. Automatically refresh active view data without manual page reload
    if (currentView === 'dashboard') {
        fetchDashboardData();
    } else if (currentView === 'reports') {
        loadReports();
    } else if (currentView === 'catalog') {
        fetchCatalogData();
    }
}



