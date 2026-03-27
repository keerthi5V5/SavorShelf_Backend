/**
 * SavorShelf Web Application - Shared Logic
 */

const app = {
    API_BASE: "http://180.235.121.253:8121",

    getFormattedImageUrl: function (pathOrUrl) {
        if (!pathOrUrl) return `${this.API_BASE}/static/default.jpg`;
        if (pathOrUrl.startsWith('http')) return pathOrUrl;
        const prefix = pathOrUrl.startsWith('/') ? '' : '/';
        return `${this.API_BASE}${prefix}${pathOrUrl}`;
    },

    // Initial Mock Data (Fallback)
    defaultProducts: [
        { id: '1', name: 'Whole Milk', addedTime: '2 hours ago', statusLabel: 'Expires', statusValue: 'Apr 15', freshnessLabel: 'Use Soon', progress: 30, imageUrl: 'https://images.unsplash.com/photo-1550989460-0adf9ea622e2?w=600', category: 'Dairy', location: 'Fridge' },
        { id: '2', name: 'Avocados', addedTime: 'Yesterday', statusLabel: 'Freshness', statusValue: '85%', freshnessLabel: 'Fresh', progress: 85, imageUrl: 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=600', category: 'Produce', location: 'Pantry' }
    ],

    // Product state management
    getProducts: async function () {
        const userId = localStorage.getItem('user_id');
        if (!userId) return this.defaultProducts;

        try {
            const response = await fetch(`${this.API_BASE}/get-pantry-items?user_id=${userId}`);
            const data = await response.json();
            if (data.status === 'success') {
                return data.items;
            }
        } catch (error) {
            console.error("Error fetching products:", error);
        }
        return [];
    },

    removeProduct: async function (id) {
        if (!confirm("Are you sure you want to permanently delete this product?")) return false;
        try {
            const response = await fetch(`${this.API_BASE}/delete-product`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            });
            return (await response.json()).status === 'success';
        } catch (error) {
            console.error("Error deleting product:", error);
            return false;
        }
    },

    updateProductStatus: async function (id, status) {
        try {
            const response = await fetch(`${this.API_BASE}/update-item-status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: id, status: status })
            });
            return (await response.json()).status === 'success';
        } catch (error) {
            console.error("Error updating status:", error);
            return false;
        }
    },

    logout: function () {
        localStorage.clear();
        window.location.href = '/';
    },

    settings: {
        updateProfile: async function () {
            const userId = localStorage.getItem('user_id');
            const newName = document.getElementById('input-name').value;

            if (!newName) return alert("Name cannot be empty");

            try {
                const response = await fetch(`${app.API_BASE}/update-profile`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, full_name: newName })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    localStorage.setItem('full_name', newName);
                    document.getElementById('user-display-name').textContent = newName;
                    document.getElementById('avatar-initial').textContent = newName.charAt(0).toUpperCase();
                    alert("Profile updated successfully!");
                    goBack();
                } else {
                    alert(data.message || "Update failed");
                }
            } catch (error) {
                console.error("Profile update error:", error);
            }
        },

        changePassword: async function () {
            const userId = localStorage.getItem('user_id');
            const oldPass = document.getElementById('old-password').value;
            const newPass = document.getElementById('new-password').value;
            const confirmPass = document.getElementById('confirm-password').value;

            if (!oldPass || !newPass || !confirmPass) return alert("Please fill all fields");
            if (newPass !== confirmPass) return alert("New passwords do not match");

            const btn = document.getElementById('btn-update-password');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            btn.disabled = true;

            try {
                const response = await fetch(`${app.API_BASE}/change-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        current_password: oldPass,
                        new_password: newPass,
                        confirm_new_password: confirmPass
                    })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    alert("Password updated successfully!");
                    goBack();
                } else {
                    alert(data.message || "Password update failed");
                }
            } catch (error) {
                console.error("Password update error:", error);
            } finally {
                btn.innerHTML = 'Update Security Key';
                btn.disabled = false;
            }
        },

        deleteAccount: async function () {
            const userId = localStorage.getItem('user_id');
            const confirmText = document.getElementById('delete-confirm-input').value;

            if (confirmText !== 'DELETE') return alert("Please type DELETE to confirm");

            const btn = document.getElementById('btn-delete-account');
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
            btn.disabled = true;

            try {
                const response = await fetch(`${app.API_BASE}/delete-account`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    alert("Your account has been permanently deleted.");
                    app.logout();
                } else {
                    alert(data.message || "Account deletion failed");
                }
            } catch (error) {
                console.error("Account deletion error:", error);
            } finally {
                btn.innerHTML = 'I understand, delete my account';
                btn.disabled = false;
            }
        }
    },

    getSelectedProduct: function () {
        const product = localStorage.getItem('ss_selected_product');
        return product ? JSON.parse(product) : null;
    },

    // Get color based on shelf life
    getStatusColor: function (label) {
        switch (label) {
            case 'Expired': return '#E53935';
            case 'Use Soon': return '#FF9800';
            case 'Moderate': return '#F59E0B';
            default: return '#00C853';
        }
    },

    // 1. Dashboard Logic
    initDashboard: async function () {
        const userId = localStorage.getItem('user_id');
        const fullName = localStorage.getItem('full_name') || "User";

        // Update header
        const headerTitle = document.querySelector('.header-title h1');
        if (headerTitle) headerTitle.textContent = `Hello, ${fullName}!`;

        try {
            const response = await fetch(`${this.API_BASE}/get-dashboard?user_id=${userId}`);
            const data = await response.json();

            if (data.status === 'success') {
                // Update Summary Cards
                const summaryDivs = document.querySelectorAll('.dash-col-left > div:first-child > div > div');
                if (summaryDivs.length >= 3) {
                    const expiredCount = summaryDivs[0].querySelector('div');
                    const soonCount = summaryDivs[1].querySelector('div');
                    const freshCount = summaryDivs[2].querySelector('div');

                    if (expiredCount) expiredCount.textContent = data.summary.expired;
                    if (soonCount) soonCount.textContent = data.summary.use_soon;
                    if (freshCount) freshCount.textContent = data.summary.fresh;
                }

                // Update Tip
                const tipP = document.querySelector('.dash-col-right > div:first-child p');
                if (tipP) tipP.textContent = data.daily_tip;

                // Update Recent Items
                const recentContainer = document.getElementById('recent-items-list');
                if (recentContainer) {
                    if (data.recent_items.length === 0) {
                        recentContainer.innerHTML = '<p style="text-align: center; color: #64748b; font-size: 14px; padding: 20px;">No recent items yet.</p>';
                    } else {
                        recentContainer.innerHTML = data.recent_items.slice(0, 4).map(item => {
                            const bg = item.freshnessLabel === 'Expired' ? '#FFF1F2' : (item.freshnessLabel === 'Use Soon' ? '#FFFBEB' : '#F0FDF4');
                            const statusCol = item.freshnessLabel === 'Expired' ? '#E11D48' : (item.freshnessLabel === 'Use Soon' ? '#D97706' : '#15803D');

                            return `
                                <div style="display: flex; align-items: center; gap: 15px; padding: 15px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); transition: 0.2s; cursor: pointer;" onclick="app.viewProductDetail(${item.id})">
                                    <img src="${this.getFormattedImageUrl(item.imageUrl)}" alt="${item.name}" style="width: 45px; height: 45px; border-radius: 12px; object-fit: cover;">
                                    <div style="flex: 1;">
                                        <h5 style="font-weight: 800; font-size: 15px; color: #1e293b; margin-bottom: 4px;">${item.name}</h5>
                                        <p style="font-size: 12px; color: #64748b; font-weight: 500;">${item.addedTime} • ${item.storageType}</p>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="background: ${bg}; color: ${statusCol}; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;">${item.freshnessLabel}</div>
                                    </div>
                                </div>
                            `;
                        }).join('');
                    }
                }
            }
        } catch (error) {
            console.error("Dashboard init error:", error);
        }
    },

    viewProductDetail: function (id) {
        location.href = `product-detail?id=${id}`;
    },

    // 2. Products Page Logic
    initProductsPage: async function () {
        const grid = document.getElementById('product-grid');
        if (!grid) return;

        const userId = localStorage.getItem('user_id');
        try {
            const response = await fetch(`${this.API_BASE}/get-pantry-items?user_id=${userId}`);
            const data = await response.json();

            if (data.status === 'success') {
                const products = data.items;

                // Update counts
                const totalHeader = document.getElementById('total-count-header');
                if (totalHeader) totalHeader.textContent = products.length;

                if (document.getElementById('count-all')) document.getElementById('count-all').textContent = products.length;
                if (document.getElementById('count-fridge')) document.getElementById('count-fridge').textContent = products.filter(p => p.storageType === 'Fridge').length;
                if (document.getElementById('count-pantry')) document.getElementById('count-pantry').textContent = products.filter(p => p.storageType === 'Room Temperature').length;
                if (document.getElementById('count-freezer')) document.getElementById('count-freezer').textContent = products.filter(p => p.storageType === 'Freezer').length;
                if (document.getElementById('count-fresh')) document.getElementById('count-fresh').textContent = products.filter(p => p.freshnessLabel === 'Fresh').length;
                if (document.getElementById('count-soon')) document.getElementById('count-soon').textContent = products.filter(p => ['Use Soon', 'Moderate'].includes(p.freshnessLabel)).length;
                if (document.getElementById('count-expired')) document.getElementById('count-expired').textContent = products.filter(p => p.freshnessLabel === 'Expired').length;

                this.renderProductGrid(products);

                // Add Filter Chip Logic
                document.querySelectorAll('.category-chip').forEach(chip => {
                    chip.onclick = () => {
                        document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
                        chip.classList.add('active');
                        const filter = chip.dataset.filter;
                        let filtered = products;
                        if (filter === 'soon') {
                            filtered = products.filter(p => ['Use Soon', 'Moderate'].includes(p.freshnessLabel));
                        } else if (filter === 'fresh') {
                            filtered = products.filter(p => p.freshnessLabel === 'Fresh');
                        } else if (filter === 'expired') {
                            filtered = products.filter(p => p.freshnessLabel === 'Expired');
                        } else if (filter !== 'all') {
                            filtered = products.filter(p => p.storageType === (filter === 'Pantry' ? 'Room Temperature' : filter));
                        }
                        this.renderProductGrid(filtered);
                    };
                });

                // Add Search Logic
                const searchInput = document.getElementById('product-search');
                if (searchInput) {
                    searchInput.oninput = (e) => {
                        const val = e.target.value.toLowerCase();
                        const filtered = products.filter(p => p.name.toLowerCase().includes(val) || (p.category && p.category.toLowerCase().includes(val)));
                        this.renderProductGrid(filtered);
                    };
                }
            }
        } catch (error) {
            console.error("Products page init error:", error);
        }
    },

    renderProductGrid: function (items) {
        const grid = document.getElementById('product-grid');
        if (!grid) return;

        if (items.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 100px 0; opacity: 0.5;"><h3>No items found</h3></div>`;
            return;
        }

        grid.innerHTML = items.map(p => `
            <div class="web-product-card glass-card" style="padding: 0; border: 1px solid #E2E8F0; border-radius: 20px; overflow: hidden; cursor: pointer; transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); transform: translateY(0); box-shadow: 0 4px 15px rgba(0,0,0,0.02);" onclick="app.viewProductDetail(${p.id})">
                <div class="card-image-wrap" style="height: 180px; overflow: hidden; position: relative;">
                    <img src="${this.getFormattedImageUrl(p.imageUrl)}" alt="${p.name}" style="width: 100%; height: 100%; object-fit: cover; transition: 0.5s;">
                    <div class="status-tag" style="position: absolute; top: 15px; right: 15px; padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: 800; color: white; background: ${this.getStatusColor(p.freshnessLabel)}; box-shadow: 0 4px 12px rgba(0,0,0,0.15); text-transform: uppercase; letter-spacing: 0.5px;">
                        ${p.freshnessLabel}
                    </div>
                </div>
                <div class="card-content" style="padding: 24px;">
                    <span class="category" style="display: block; font-size: 11px; font-weight: 800; color: ${this.getStatusColor(p.freshnessLabel)}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; opacity: 0.8;">${p.category || 'General'}</span>
                    <h4 style="font-size: 19px; font-weight: 800; color: #1e293b; margin: 0 0 6px 0; letter-spacing: -0.4px;">${p.name}</h4>
                    <p style="font-size: 14px; color: #64748b; font-weight: 600; margin: 0 0 20px 0; display: flex; align-items: center; gap: 6px;">
                        <i class="fas fa-map-marker-alt" style="font-size: 12px;"></i> ${p.storageType}
                    </p>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 800; color: #1e293b;">Freshness Balance</span>
                        <span style="font-size: 13px; font-weight: 800; color: ${this.getStatusColor(p.freshnessLabel)};">${p.progress}%</span>
                    </div>
                    
                    <div class="progress-container" style="background: #F1F5F9; border-radius: 12px; height: 10px; overflow: hidden; width: 100%;">
                        <div class="progress-fill" style="width: ${p.progress}%; height: 100%; background: linear-gradient(90deg, ${this.getStatusColor(p.freshnessLabel)}, ${this.getStatusColor(p.freshnessLabel)}cc); border-radius: 12px;"></div>
                    </div>
                </div>
            </div>
        `).join('');
    },

    initFreshnessPage: async function () {
        const container = document.querySelector('.product-grid-premium');
        if (!container) return;

        const userId = localStorage.getItem('user_id');
        try {
            const response = await fetch(`${this.API_BASE}/get-freshness-report?user_id=${userId}`);
            const data = await response.json();

            if (data.status === 'success') {
                const s = data.summary;

                // Update stats cards
                if (document.getElementById('peak-freshness-count')) document.getElementById('peak-freshness-count').textContent = s.fresh;
                if (document.getElementById('use-soon-count')) document.getElementById('use-soon-count').textContent = s.use_soon;
                if (document.getElementById('expired-count')) document.getElementById('expired-count').textContent = s.expired;

                // Update Waste Impact Widget
                const total = s.weekly_consumed + s.weekly_wasted;
                const consumedPct = total > 0 ? Math.round((s.weekly_consumed / total) * 100) : 100;
                const wastedPct = total > 0 ? 100 - consumedPct : 0;

                const impactText = document.getElementById('waste-impact-text');
                if (impactText) {
                    if (total === 0) {
                        impactText.textContent = "Start tracking your consumption to see your sustainability impact!";
                    } else if (s.weekly_wasted === 0) {
                        impactText.textContent = "Zero waste detected this week. You're doing an amazing job for the planet!";
                    } else {
                        const mostWasted = s.most_wasted_item ? ` (primarily ${s.most_wasted_item})` : "";
                        impactText.textContent = `You've avoided ${consumedPct}% of potential waste this week. Let's try to reduce your wasted items${mostWasted}!`;
                    }
                }

                if (document.getElementById('consumed-pct-text')) document.getElementById('consumed-pct-text').textContent = `Consumed: ${consumedPct}%`;
                if (document.getElementById('wasted-pct-text')) document.getElementById('wasted-pct-text').textContent = `Wasted: ${wastedPct}%`;

                const progressFill = document.getElementById('waste-progress-fill');
                if (progressFill) {
                    progressFill.style.width = `${consumedPct}%`;
                    progressFill.style.background = consumedPct > 70 ? '#0ACF83' : (consumedPct > 40 ? '#FF7600' : '#F04438');
                }

                // Render items
                container.innerHTML = data.items.map((item, index) => {
                    const color = this.getStatusColor(item.freshnessLabel);
                    const expiryMsg = item.daysRemaining < 0 ? `Expired ${Math.abs(item.daysRemaining)} days ago` : (item.daysRemaining === 0 ? "Expires Today" : `Expires in ${item.daysRemaining} days`);

                    return `
                        <div class="product-card-premium anim-card d-${index % 5}" data-expiry="${item.daysRemaining <= 0 ? 'today' : 'future'}">
                            <div class="item-header">
                                <div class="item-name-wrap" onclick="app.viewProductDetail(${item.id})" style="cursor: pointer;">
                                    <div class="item-emoji" style="padding: 0; overflow: hidden;">
                                        <img src="${this.getFormattedImageUrl(item.imageUrl)}" style="width: 100%; height: 100%; object-fit: cover;">
                                    </div>
                                    <h4>${item.name}</h4>
                                </div>
                                <span class="badge-fresh" style="background: ${color};">${item.freshnessLabel}</span>
                            </div>
                            <div class="expiry-info">
                                <div class="expiry-text">
                                    <span>Freshness Scale</span>
                                    <span style="color: ${color};">${expiryMsg}</span>
                                </div>
                                <div class="progress-bar-premium">
                                    <div class="progress-fill-premium" style="width: ${item.progress}%; background: ${color};"></div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        } catch (error) {
            console.error("Freshness page init error:", error);
        }
    },

    filterInventory: function (type, el) {
        // Toggle active class on buttons
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        el.classList.add('active');

        // Filter cards
        const cards = document.querySelectorAll('.product-card-premium');
        cards.forEach(card => {
            if (type === 'all') {
                card.style.display = 'block';
            } else if (type === 'expiring') {
                // Show only if data-expiry is 'today'
                if (card.getAttribute('data-expiry') === 'today') {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            }
        });

        // Show empty message if nothing found
        const visibleCards = Array.from(cards).filter(c => c.style.display !== 'none');
        const container = document.querySelector('.product-grid-premium');
        let emptyMsg = document.getElementById('filter-empty-msg');

        if (visibleCards.length === 0) {
            if (!emptyMsg) {
                emptyMsg = document.createElement('div');
                emptyMsg.id = 'filter-empty-msg';
                emptyMsg.style.cssText = 'grid-column: 1/-1; text-align: center; padding: 60px; opacity: 0.5; font-weight: 700;';
                emptyMsg.innerHTML = '<h3>No items matching this filter</h3>';
                container.appendChild(emptyMsg);
            }
            emptyMsg.style.display = 'block';
        } else if (emptyMsg) {
            emptyMsg.style.display = 'none';
        }
    },

    getCategoryEmoji: function (category) {
        const mapping = {
            'Fruits': '🍎',
            'Vegetables': '🥦',
            'Leafy Greens': '🥬',
            'Meat & Seafood': '🍗',
            'Dairy': '🧀',
            'Herbs & Seasonings': '🌿',
            'Grains': '🌾',
            'Snacks': '🥨'
        };
        return mapping[category] || '📦';
    },

    // 3. Product Detail Logic
    initProductDetails: async function () {
        const params = new URLSearchParams(window.location.search);
        const productId = params.get('id');
        if (!productId) {
            // Only redirect if we are strictly on the single product view page
            if (window.location.pathname.includes('product-detail') && !window.location.pathname.includes('add-product-details')) {
                location.href = 'products';
            }
            return;
        }

        try {
            const response = await fetch(`${this.API_BASE}/get-product-details?id=${productId}`);
            const result = await response.json();

            if (result.status === 'success') {
                const product = result.data;
                const color = this.getStatusColor(product.freshness_label);

                // Populate Details
                document.title = `SavorShelf | ${product.item_name} Details`;
                const img = document.getElementById('product-img');
                if (img) img.src = this.getFormattedImageUrl(product.image_path);

                const nameHeader = document.getElementById('product-name');
                if (nameHeader) nameHeader.textContent = product.item_name;

                const statusText = document.getElementById('product-status-text');
                if (statusText) statusText.textContent = product.freshness_label;

                const badge = document.getElementById('product-status-badge');
                if (badge) badge.style.color = color;

                const progPct = document.getElementById('product-progress-pct');
                if (progPct) {
                    progPct.textContent = `${product.freshness_progress}%`;
                    progPct.style.color = color;
                }

                const fill = document.getElementById('product-progress-fill');
                if (fill) {
                    fill.style.background = `linear-gradient(90deg, ${color}, ${color}dd)`;
                    setTimeout(() => { fill.style.width = `${product.freshness_progress}%`; }, 100);
                }

                const catTag = document.getElementById('product-cat-tag');
                if (catTag) {
                    catTag.textContent = product.category || 'General';
                    catTag.style.background = `${color}15`;
                    catTag.style.color = color;
                }

                const locSpan = document.getElementById('product-loc');
                if (locSpan) locSpan.textContent = product.storage_location || 'Kitchen';

                const expiryVal = document.getElementById('product-expiry-val');
                if (expiryVal) {
                    expiryVal.textContent = product.expiry_value || 'N/A';
                    expiryVal.style.color = color;
                }

                const iconBox = document.getElementById('expiry-icon-box');
                if (iconBox) {
                    iconBox.style.background = `${color}15`;
                    const icon = iconBox.querySelector('i');
                    if (icon) icon.style.color = color;
                }

                const addedDate = document.getElementById('product-added');
                if (addedDate) addedDate.textContent = product.primary_date_value;

                const meta = document.getElementById('product-meta');
                if (meta) meta.textContent = `${product.primary_date_label}: ${product.primary_date_value} • Lot: ${product.lot_number || 'None'}`;

                // Advice Logic
                const advice = document.getElementById('product-advice');
                const aiTip = document.getElementById('ai-tip');
                if (product.freshness_progress < 20) {
                    if (advice) advice.textContent = "This item is critically low on freshness. consume or freeze it immediately!";
                    if (aiTip) aiTip.textContent = "Signs of spoilage: Discoloration, strange smell, or slimy texture. Always check before consuming!";
                } else if (product.freshness_progress < 50) {
                    if (advice) advice.textContent = "This item is expiring within the next few days. Plan your meals accordingly!";
                } else {
                    if (advice) advice.textContent = "This item is perfectly fresh. Ideal for salads or raw consumption.";
                }

                // Consumed Button Logic
                const consumedBtn = document.getElementById('consumed-btn');
                if (consumedBtn) {
                    consumedBtn.onclick = async () => {
                        consumedBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                        consumedBtn.style.opacity = '0.7';
                        const success = await this.updateProductStatus(productId, 'consumed');
                        if (success) {
                            location.href = 'products';
                        } else {
                            alert("Failed to update product status.");
                            consumedBtn.innerHTML = '<i class="fas fa-check-circle"></i> Consumed';
                            consumedBtn.style.opacity = '1';
                        }
                    };
                }

                // Delete Button Logic (if exists)
                const deleteBtn = document.getElementById('delete-product-btn');
                if (deleteBtn) {
                    deleteBtn.onclick = async () => {
                        const success = await this.removeProduct(productId);
                        if (success) {
                            location.href = 'products';
                        }
                    };
                }
            } else {
                alert("Product details not found.");
                location.href = 'products';
            }
        } catch (error) {
            console.error("Product details init error:", error);
        }
    }
};

// Initialize based on page
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    // Exact or nearly exact matching to avoid "add-product-details" matching "product-detail" or "products"
    if (path.endsWith('dashboard') || path.includes('dashboard.html')) {
        app.initDashboard();
    } else if (path.endsWith('products') || path.includes('products.html')) {
        app.initProductsPage();
    } else if (path.endsWith('freshness') || path.includes('freshness.html')) {
        app.initFreshnessPage();
    } else if (path.endsWith('product-detail') || path.includes('product-detail.html')) {
        // Special case: "add-product-details" should NOT trigger single item detail logic
        if (!path.includes('add-product-details')) {
            app.initProductDetails();
        }
    }

    // Auth Check (Except index and auth pages)
    const isAuthPage = path === '/' || path.endsWith('index') || path.includes('login') || path.includes('register') || path.includes('forgot-password');
    if (!isAuthPage) {
        if (!localStorage.getItem('user_id')) {
            window.location.href = 'index';
        }
    }

    // Sidebar & Mobile Nav Active State Handle
    const currentPath = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-link, .mobile-bottom-nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '' && href === 'dashboard')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Landing Page Scroll Spy for Navigation Underline
    if (path === '/' || path.includes('index')) {
        const sections = document.querySelectorAll('section, footer');
        const navItems = document.querySelectorAll('.landing-nav .nav-link-item');

        if (sections.length > 0 && navItems.length > 0) {
            window.addEventListener('scroll', () => {
                let current = '';
                sections.forEach(sec => {
                    const sectionTop = sec.offsetTop;
                    // Trigger section when it's halfway into viewport
                    if (window.pageYOffset >= (sectionTop - window.innerHeight / 2)) {
                        current = sec.getAttribute('id');
                    }
                });

                // Guarantee "about" triggering when reaching the absolute bottom of the page
                if ((window.innerHeight + window.pageYOffset) >= document.body.offsetHeight - 50) {
                    current = 'about';
                }

                navItems.forEach(li => {
                    li.classList.remove('active');
                    if (li.getAttribute('href') === `#${current}`) {
                        li.classList.add('active');
                    }
                });
            });
        }
    }
});
