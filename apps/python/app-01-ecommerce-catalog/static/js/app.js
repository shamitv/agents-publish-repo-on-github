// -------------------------------------------------------------
// App 01 - Cyberpunk E-Commerce SPA Frontend Client Logic
// -------------------------------------------------------------

let currentUser = null;
let currentView = 'catalog';
let cart = []; // client-side session basket: {id, name, price, qty}

document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication();
});

// Verify active session profile
function checkAuthentication() {
    fetch("/api/auth/me")
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Unauthenticated");
        })
        .then(user => {
            currentUser = user;
            document.getElementById("currentUserLabel").innerText = user.username;
            document.getElementById("currentUserRoleLabel").innerText = `ROLE: ${user.role}`;

            // Admin features
            if (user.role === 'ADMIN') {
                document.getElementById("addProductBtn").style.display = 'inline-flex';
            } else {
                document.getElementById("addProductBtn").style.display = 'none';
            }

            document.getElementById("authPortal").style.display = 'none';
            document.getElementById("appLayout").style.display = 'flex';
            
            showView(currentView);
        })
        .catch(() => {
            currentUser = null;
            document.getElementById("appLayout").style.display = 'none';
            document.getElementById("authPortal").style.display = 'flex';
        });
}

// Authentication handlers
function handleLoginSubmit(e) {
    e.preventDefault();
    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();
    const errBlock = document.getElementById("loginError");

    errBlock.style.display = 'none';

    fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass })
    })
    .then(res => {
        if (res.status === 200) {
            checkAuthentication();
        } else {
            errBlock.style.display = 'block';
        }
    })
    .catch(err => {
        console.error("Login request failed:", err);
        errBlock.style.display = 'block';
    });
}

function handleLogout() {
    fetch("/api/auth/logout", { method: "POST" })
        .then(() => {
            currentUser = null;
            cart = [];
            updateCartUI();
            document.getElementById("appLayout").style.display = 'none';
            document.getElementById("authPortal").style.display = 'flex';
        })
        .catch(err => console.error("Logout failed:", err));
}

// Router switcher
function showView(viewName) {
    currentView = viewName;

    // Toggle active link highlights
    document.querySelectorAll(".sidebar .nav-link").forEach(link => {
        link.classList.remove("active");
    });
    const activeLink = document.getElementById(`nav-${viewName}`);
    if (activeLink) activeLink.classList.add("active");

    // Toggle view visibility
    document.querySelectorAll(".spa-view").forEach(view => {
        view.style.display = 'none';
    });
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) targetView.style.display = 'block';

    // Populate data depending on view
    if (viewName === 'catalog') {
        loadCatalog();
    } else if (viewName === 'orders') {
        loadOrders();
    }
}

// 1. Catalog View
function loadCatalog(searchQuery = '') {
    const consoleFeed = document.getElementById("sqlConsoleFeed");
    let url = "/api/products";
    if (searchQuery) {
        url += `?q=${encodeURIComponent(searchQuery)}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            // Update pipeline console feed (SQL Injection target A03 tracer!)
            if (data.success === false) {
                consoleFeed.innerHTML = `<span style="color: var(--danger);">[SQL EXCEPTION ERROR]:\n${data.error}\n\nQuery executed:\n${data.query_executed}</span>`;
                return;
            }

            consoleFeed.innerText = `[SQL INJECTION TELEMETRY FEED] - Status: 200 OK\nQuery Executed: ${data.debug_query}`;
            
            const grid = document.getElementById("productsGrid");
            grid.innerHTML = '';

            data.products.forEach(p => {
                const card = document.createElement("div");
                card.className = "product-card";
                card.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="category">${p.category}</span>
                            <span class="sku-badge">${p.sku}</span>
                        </div>
                        <div class="name">${p.name}</div>
                        <div class="description">${p.description}</div>
                    </div>
                    <div class="footer">
                        <div>
                            <div class="price">$${p.price.toFixed(2)}</div>
                            <div class="qty-badge">Stock: ${p.quantity} units</div>
                        </div>
                        <button onclick="addToCart(${p.id}, '${p.name.replace(/'/g, "\\'")}', ${p.price})" class="btn" ${p.quantity === 0 ? 'disabled' : ''}>
                            ${p.quantity === 0 ? 'SOLD OUT' : 'ADD TO UNIT'}
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => {
            console.error("Failed to load catalog:", err);
            consoleFeed.innerHTML = `<span style="color: var(--danger);">Connection Error: ${err.message}</span>`;
        });
}

function triggerCatalogSearch() {
    const q = document.getElementById("catalogSearchInput").value.trim();
    loadCatalog(q);
}

// 2. Client Cart Basket
function addToCart(id, name, price) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({ id, name, price, qty: 1 });
    }
    updateCartUI();
    toggleCartDrawer(true);
}

function updateCartUI() {
    const countLabel = document.getElementById("cartCountLabel");
    const itemsList = document.getElementById("cartItemsList");
    const totalLabel = document.getElementById("cartTotalLabel");

    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    countLabel.innerText = totalQty;

    itemsList.innerHTML = '';
    if (cart.length === 0) {
        itemsList.innerHTML = `<span style="color: var(--text-muted); font-size: 14px; text-align: center; display: block; margin-top: 32px;">Your basket is empty.</span>`;
        totalLabel.innerText = "$0.00";
        return;
    }

    let totalVal = 0.0;
    cart.forEach((item, idx) => {
        const cost = item.price * item.qty;
        totalVal += cost;

        const row = document.createElement("div");
        row.style.background = "#11131c";
        row.style.border = "1px solid var(--border-color)";
        row.style.borderRadius = "6px";
        row.style.padding = "12px 16px";
        row.style.display = "flex";
        row.style.justify-content = "space-between";
        row.style.align-items = "center";
        
        row.innerHTML = `
            <div>
                <div style="font-weight: 700; color: #fff; font-size: 14px;">${item.name}</div>
                <div style="font-family: var(--font-mono); font-size: 11px; color: var(--secondary); margin-top: 2px;">$${item.price.toFixed(2)} x ${item.qty}</div>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-family: var(--font-mono); font-weight: 700;">$${cost.toFixed(2)}</span>
                <button onclick="removeFromCart(${idx})" class="modal-close" style="font-size: 18px; color: var(--danger);">×</button>
            </div>
        `;
        itemsList.appendChild(row);
    });

    totalLabel.innerText = `$${totalVal.toFixed(2)}`;
}

function removeFromCart(idx) {
    cart.splice(idx, 1);
    updateCartUI();
}

function toggleCartDrawer(forceShow = null) {
    const drawer = document.getElementById("cartDrawer");
    if (forceShow === true) {
        drawer.classList.add("active");
    } else if (forceShow === false) {
        drawer.classList.remove("active");
    } else {
        drawer.classList.toggle("active");
    }
}

function commitCheckout() {
    if (cart.length === 0) return;

    const payloadItems = cart.map(item => ({
        product_id: item.id,
        quantity: item.qty
    }));

    fetch("/api/orders", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: payloadItems })
    })
    .then(res => {
        if (res.ok) return res.json();
        throw new Error("Checkout Transaction Rejected");
    })
    .then(() => {
        cart = [];
        updateCartUI();
        toggleCartDrawer(false);
        showView('orders');
    })
    .catch(err => {
        console.error("Checkout Failure:", err);
        alert(err.message);
    });
}

// 3. Orders View
function loadOrders() {
    fetch("/api/orders")
        .then(res => res.json())
        .then(orders => {
            const tbody = document.getElementById("ordersTableBody");
            tbody.innerHTML = '';

            if (orders.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No active orders recorded.
                        </td>
                    </tr>
                `;
                return;
            }

            orders.forEach(o => {
                const tr = document.createElement("tr");
                const dateStr = o.created_at ? o.created_at.substring(0, 16).replace("T", " ") : "-";
                
                tr.innerHTML = `
                    <td class="sku-badge" style="display: table-cell;">${o.id}</td>
                    <td style="font-family: var(--font-mono); color: #fff;">${o.order_number}</td>
                    <td style="font-family: var(--font-cyber); font-size: 12px; color: var(--primary);">${o.username}</td>
                    <td style="font-family: var(--font-mono);">$${o.total_amount.toFixed(2)}</td>
                    <td style="font-weight: 700; color: var(--success);">${o.status}</td>
                    <td style="font-size: 13px; color: var(--text-muted);">${dateStr}</td>
                    <td>
                        <button onclick="readOrderDetails(${o.id})" class="btn btn-secondary" style="padding: 6px 12px; font-size: 11px;">Inspect</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading purchases:", err));
}

// 4. Order Details Modal (IDOR playground - A01 target!)
function readOrderDetails(orderId) {
    fetch(`/api/orders/${orderId}`)
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Pleadings access rejected by WMS core controller.");
        })
        .then(order => {
            document.getElementById("orderDetailNumber").innerText = order.order_number;
            document.getElementById("orderDetailOwner").innerText = order.username;
            document.getElementById("orderDetailStatus").innerText = order.status;
            document.getElementById("orderDetailTotal").innerText = `$${order.total_amount.toFixed(2)}`;

            const tbody = document.getElementById("orderDetailItemsTableBody");
            tbody.innerHTML = '';

            order.items.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="sku-badge" style="display: table-cell;">${item.sku}</td>
                    <td style="font-weight: 700;">${item.name}</td>
                    <td>${item.quantity}</td>
                    <td style="font-family: var(--font-mono);">$${item.price.toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById("orderDetailModal").style.display = 'flex';
        })
        .catch(err => {
            console.error("Order exfiltration failed:", err);
            alert(err.message);
        });
}

function closeOrderDetailModal() {
    document.getElementById("orderDetailModal").style.display = 'none';
}

// Admin add catalog items
function openAddProductModal() {
    document.getElementById("addProductModal").style.display = 'flex';
}

function closeAddProductModal() {
    document.getElementById("addProductModal").style.display = 'none';
}

function handleAddProductSubmit(e) {
    e.preventDefault();

    const payload = {
        sku: document.getElementById("addSku").value.trim(),
        name: document.getElementById("addName").value.trim(),
        description: document.getElementById("addDesc").value.trim(),
        category: document.getElementById("addCategory").value.trim(),
        price: parseFloat(document.getElementById("addPrice").value),
        quantity: parseInt(document.getElementById("addQty").value)
    };

    fetch("/api/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeAddProductModal();
            document.getElementById("addProductForm").reset();
            loadCatalog();
        } else {
            alert("Failed to register catalog item. Access Denied.");
        }
    })
    .catch(err => console.error("Error creating product:", err));
}
