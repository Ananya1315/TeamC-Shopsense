/* ShopSense API Service Module */
const API_BASE_URL = window.location.origin;

const API = {
    // Auth APIs
    async vendorLogin(email, password) {
        const response = await fetch(`${API_BASE_URL}/vendors/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Invalid Email or Password');
        }
        return await response.json();
    },

    async vendorRegister(storeName, ownerName, email, phone, password, confirmPassword) {
        const response = await fetch(`${API_BASE_URL}/vendors/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: storeName,
                owner_name: ownerName,
                email: email,
                phone: phone,
                password: password,
                confirm_password: confirmPassword
            })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Registration failed');
        }
        return await response.json();
    },

    async adminLogin(email, password) {
        const response = await fetch(`${API_BASE_URL}/admin/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Invalid Email or Password');
        }
        return await response.json();
    },

    // Admin Marketplace Management APIs
    async getAdminDashboardMetrics() {
        const response = await fetch(`${API_BASE_URL}/admin/dashboard`);
        if (!response.ok) throw new Error('Failed to fetch admin dashboard metrics');
        return await response.json();
    },

    async getAdminVendors() {
        const response = await fetch(`${API_BASE_URL}/admin/vendors`);
        if (!response.ok) throw new Error('Failed to fetch marketplace vendors');
        return await response.json();
    },

    async updateVendorStatus(vendorId, isActive) {
        const response = await fetch(`${API_BASE_URL}/admin/vendors/${vendorId}/status?is_active=${isActive}`, {
            method: 'PUT'
        });
        if (!response.ok) throw new Error('Failed to update vendor status');
        return await response.json();
    },

    async deleteVendor(vendorId) {
        const response = await fetch(`${API_BASE_URL}/admin/vendors/${vendorId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete vendor');
        return await response.json();
    },

    async getAdminProducts() {
        const response = await fetch(`${API_BASE_URL}/admin/products`);
        if (!response.ok) throw new Error('Failed to fetch admin marketplace products');
        return await response.json();
    },

    // Product APIs
    async getProducts(vendorId = null) {
        const url = vendorId ? `${API_BASE_URL}/products/?vendor_id=${vendorId}` : `${API_BASE_URL}/products/`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch products');
        return await response.json();
    },

    async createProduct(productData, vendorId = 1) {
        productData.vendor_id = vendorId;
        const response = await fetch(`${API_BASE_URL}/products/?vendor_id=${vendorId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productData)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to create product');
        }
        return await response.json();
    },

    async deleteProduct(productId) {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete product');
        return await response.json();
    },

    // Analytics APIs
    async getDashboardMetrics(vendorId = 1) {
        const response = await fetch(`${API_BASE_URL}/analytics/dashboard?vendor_id=${vendorId}`);
        if (!response.ok) throw new Error('Failed to fetch dashboard metrics');
        return await response.json();
    },

    async getLowStockAlerts(vendorId = 1) {
        const response = await fetch(`${API_BASE_URL}/analytics/low-stock?vendor_id=${vendorId}`);
        if (!response.ok) throw new Error('Failed to fetch low stock alerts');
        return await response.json();
    },

    async runForecast(productId) {
        const response = await fetch(`${API_BASE_URL}/analytics/forecast`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: parseInt(productId) })
        });
        if (!response.ok) throw new Error('Failed to generate forecast');
        return await response.json();
    },

    async analyzeSentiment(productId, rating, reviewText) {
        const response = await fetch(`${API_BASE_URL}/analytics/sentiment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: parseInt(productId),
                rating: parseInt(rating),
                review_text: reviewText
            })
        });
        if (!response.ok) throw new Error('Failed to analyze sentiment');
        return await response.json();
    },

    async getCustomerSegmentation(vendorId = 1) {
        const response = await fetch(`${API_BASE_URL}/analytics/customer-segmentation?vendor_id=${vendorId}`);
        if (!response.ok) throw new Error('Failed to fetch customer segmentation');
        return await response.json();
    },

    async getRecommendations(vendorId = 1) {
        const response = await fetch(`${API_BASE_URL}/analytics/recommendations?vendor_id=${vendorId}`);
        if (!response.ok) throw new Error('Failed to fetch recommendations');
        return await response.json();
    },

    async seedHistoricalData(vendorId = 1) {
        const response = await fetch(`${API_BASE_URL}/analytics/seed?vendor_id=${vendorId}`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to seed historical data');
        return await response.json();
    }
};
