// -------------------------------------------------------------
// App 08 - Apex WMS SPA Frontend Client Logic
// -------------------------------------------------------------

let currentUser = null;
let currentView = 'dashboard';
let selectedOrderId = null;

document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication();
});

// Check active session
function checkAuthentication() {
    fetch("/api/users/me")
        .then(res => {
            if (res.ok) {
                return res.json();
            }
            throw new Error("Unauthenticated");
        })
        .then(user => {
            currentUser = user;
            document.getElementById("currentUserLabel").innerText = user.username;
            document.getElementById("currentUserRoleLabel").innerText = `Role: ${user.role}`;
            
            // Adjust supervisor+ features
            if (user.role === 'SUPERVISOR' || user.role === 'ADMIN') {
                document.getElementById("addInventoryBtn").style.display = 'inline-flex';
            } else {
                document.getElementById("addInventoryBtn").style.display = 'none';
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

    // Call standard Spring Security login processing
    const formData = new URLSearchParams();
    formData.append("username", user);
    formData.append("password", pass);

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData.toString()
    })
    .then(res => {
        if (res.status === 200) {
            checkAuthentication();
        } else {
            errBlock.style.display = 'block';
        }
    })
    .catch(err => {
        console.error("Login failure:", err);
        errBlock.style.display = 'block';
    });
}

function handleLogout() {
    fetch("/logout", { method: "POST" })
        .then(() => {
            currentUser = null;
            document.getElementById("appLayout").style.display = 'none';
            document.getElementById("authPortal").style.display = 'flex';
        })
        .catch(err => console.error("Logout failed:", err));
}

// Client-side router
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
    if (viewName === 'dashboard') {
        loadDashboard();
    } else if (viewName === 'inventory') {
        loadInventory();
    } else if (viewName === 'orders') {
        loadOrders();
    } else if (viewName === 'shipping') {
        loadShippingFormSetup();
    }
}

// 1. Dashboard Logic
function loadDashboard() {
    fetch("/api/dashboard/stats")
        .then(res => res.json())
        .then(stats => {
            document.getElementById("statTotalItems").innerText = stats.totalItems;
            document.getElementById("statLowStockCount").innerText = stats.lowStockCount;
            document.getElementById("statPendingOrders").innerText = stats.pendingOrdersCount;

            const tbody = document.getElementById("lowStockTableBody");
            tbody.innerHTML = '';

            if (stats.lowStockItems.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            All catalog items satisfy threshold levels.
                        </td>
                    </tr>
                `;
                return;
            }

            stats.lowStockItems.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="part-code">${item.sku}</td>
                    <td>${item.name}</td>
                    <td><span class="location-badge">Aisle ${item.aisle}</span></td>
                    <td style="color: var(--warning); font-weight: 700;">${item.quantity}</td>
                    <td>${item.minQuantity}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading dashboard:", err));
}

// 2. Inventory Logic
function loadInventory() {
    fetch("/api/inventory")
        .then(res => res.json())
        .then(items => {
            const tbody = document.getElementById("inventoryTableBody");
            tbody.innerHTML = '';

            items.forEach(item => {
                const isLow = item.quantity < item.minQuantity;
                const restockedStr = item.lastRestocked ? item.lastRestocked.replace("T", " ").substring(0, 16) : "-";
                
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="part-code">${item.sku}</td>
                    <td>${item.name}</td>
                    <td><span class="location-badge">Aisle ${item.aisle}-${item.shelf}-${item.bin}</span></td>
                    <td>${item.weightKg} kg</td>
                    <td>$${item.unitPrice.toFixed(2)}</td>
                    <td style="font-weight: 700; ${isLow ? 'color: var(--warning);' : 'color: var(--success);'}">${item.quantity}</td>
                    <td>${item.minQuantity}</td>
                    <td style="font-size: 12px; color: var(--text-muted);">${restockedStr}</td>
                    <td>
                        <button onclick="adjustInventoryQty(${item.id}, ${item.quantity + 10})" class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;">+10 Stock</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading inventory:", err));
}

function adjustInventoryQty(id, newQty) {
    fetch(`/api/inventory/${id}`)
        .then(res => res.json())
        .then(item => {
            item.quantity = newQty;
            return fetch(`/api/inventory/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(item)
            });
        })
        .then(res => {
            if (res.ok) {
                loadInventory();
            } else {
                alert("Failed to adjust inventory. Supervisor role required.");
            }
        })
        .catch(err => console.error("Error adjusting stock:", err));
}

function openAddInventoryModal() {
    document.getElementById("addInventoryModal").style.display = 'flex';
}

function closeAddInventoryModal() {
    document.getElementById("addInventoryModal").style.display = 'none';
}

function handleAddInventorySubmit(e) {
    e.preventDefault();

    const payload = {
        sku: document.getElementById("addSku").value.trim(),
        name: document.getElementById("addName").value.trim(),
        description: document.getElementById("addDesc").value.trim(),
        quantity: parseInt(document.getElementById("addQty").value),
        minQuantity: parseInt(document.getElementById("addMinQty").value),
        aisle: document.getElementById("addAisle").value.trim(),
        shelf: document.getElementById("addShelf").value.trim(),
        bin: document.getElementById("addBin").value.trim()
    };

    fetch("/api/inventory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeAddInventoryModal();
            document.getElementById("addInventoryForm").reset();
            loadInventory();
        } else {
            res.text().then(text => alert("Failed to add catalog item: " + text));
        }
    })
    .catch(err => console.error("Error saving inventory item:", err));
}

// 3. Orders Logic
function loadOrders() {
    fetch("/api/orders")
        .then(res => res.json())
        .then(orders => {
            const tbody = document.getElementById("ordersQueueTableBody");
            tbody.innerHTML = '';

            orders.forEach(order => {
                const tr = document.createElement("tr");
                tr.style.cursor = 'pointer';
                tr.onclick = () => selectOrder(order.id);

                let badgeClass = 'badge-pending';
                if (order.status === 'PICKING') badgeClass = 'badge-picking';
                else if (order.status === 'PACKED') badgeClass = 'badge-packed';
                else if (order.status === 'SHIPPED') badgeClass = 'badge-shipped';

                tr.innerHTML = `
                    <td class="part-code">${order.orderNumber}</td>
                    <td>${order.customerName}</td>
                    <td><span class="badge ${badgeClass}">${order.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading orders:", err));
}

function selectOrder(id) {
    selectedOrderId = id;

    // Load order meta
    fetch(`/api/orders/${id}`)
        .then(res => res.json())
        .then(order => {
            document.getElementById("orderDetailNumber").innerText = order.orderNumber;
            document.getElementById("orderDetailCustomer").innerText = order.customerName;
            document.getElementById("orderDetailAddress").innerText = order.customerAddress;

            const badge = document.getElementById("orderDetailStatusBadge");
            badge.innerText = order.status;
            badge.className = 'badge';
            if (order.status === 'PENDING') badge.classList.add('badge-pending');
            else if (order.status === 'PICKING') badge.classList.add('badge-picking');
            else if (order.status === 'PACKED') badge.classList.add('badge-packed');
            else if (order.status === 'SHIPPED') badge.classList.add('badge-shipped');

            // Render buttons block depending on status
            const actions = document.getElementById("orderFulfillmentActions");
            actions.innerHTML = '';

            if (order.status === 'PENDING') {
                actions.innerHTML = `<button onclick="transitionOrder(${order.id}, 'PICKING')" class="btn">🚀 Start Picking</button>`;
            } else if (order.status === 'PICKING') {
                actions.innerHTML = `<button onclick="transitionOrder(${order.id}, 'PACKED')" class="btn">📦 Pack Order Items</button>`;
            } else if (order.status === 'PACKED') {
                actions.innerHTML = `
                    <span style="color: var(--text-muted); font-size: 13px; align-self: center;">Ready for dispatch. Generate label in Shipping Station!</span>
                    <button onclick="transitionOrder(${order.id}, 'SHIPPED')" class="btn">✈ Dispatch Order</button>
                `;
            } else if (order.status === 'SHIPPED') {
                actions.innerHTML = `<span style="color: var(--success); font-weight: 600; font-size: 14px;">✓ Order Completely Dispatched</span>`;
            }

            // Load items
            return fetch(`/api/orders/${id}/items`);
        })
        .then(res => res.json())
        .then(items => {
            const tbody = document.getElementById("orderItemsTableBody");
            tbody.innerHTML = '';

            items.forEach(oi => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>
                        <div style="font-weight: 600;">${oi.inventoryItem.name}</div>
                        <div class="part-code" style="font-size: 11px; margin-top: 2px;">${oi.inventoryItem.sku} — Aisle ${oi.inventoryItem.aisle}</div>
                    </td>
                    <td class="part-code">${oi.quantity}</td>
                    <td>
                        <span style="font-size: 12px; font-weight: 600; ${oi.picked ? 'color: var(--success);' : 'color: var(--warning);'}">
                            ${oi.picked ? '✓ READY' : '● QUEUED'}
                        </span>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById("orderDetailsCard").style.display = 'flex';
        })
        .catch(err => console.error("Error loading order details:", err));
}

function transitionOrder(id, nextStatus) {
    fetch(`/api/orders/${id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus })
    })
    .then(res => {
        if (res.ok) {
            loadOrders();
            selectOrder(id);
        } else {
            res.text().then(text => alert("Failed to transition status: " + text));
        }
    })
    .catch(err => console.error("Error transitioning order:", err));
}

function generatePickList() {
    if (!selectedOrderId) return;
    
    fetch(`/api/orders/${selectedOrderId}/picklist`)
        .then(res => res.json())
        .then(picks => {
            let str = `⚡ OP PICK LIST FOR ORDER [ID: ${selectedOrderId}] ⚡\n\n`;
            str += `Aisle traversal directions:\n`;
            picks.forEach(p => {
                str += `➔ [${p.locationCode}] | SKU: ${p.sku} | Qty: ${p.quantity} | Item: ${p.itemName}\n`;
            });
            alert(str);
        })
        .catch(err => console.error("Error generating picklist:", err));
}

// 4. Employees Logic
function triggerEmployeeSearch() {
    const q = document.getElementById("employeeSearchInput").value.trim();
    const tbody = document.getElementById("employeesTableBody");

    tbody.innerHTML = `
        <tr>
            <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px;">
                Searching database directory...
            </td>
        </tr>
    `;

    fetch(`/api/employees/search?q=${encodeURIComponent(q)}`)
        .then(res => res.json())
        .then(employees => {
            tbody.innerHTML = '';
            
            if (employees.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No personnel matched search criteria.
                        </td>
                    </tr>
                `;
                return;
            }

            employees.forEach(emp => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="part-code">${emp.uid}</td>
                    <td style="font-weight: 600;">${emp.cn}</td>
                    <td>${emp.sn}</td>
                    <td style="font-family: var(--font-mono); font-size: 13px;">${emp.mail}</td>
                    <td><span class="location-badge">${emp.title}</span></td>
                    <td>${emp.departmentNumber}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("LDAP search failure:", err);
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; color: var(--warning); padding: 32px; font-weight: 600;">
                        Directory Lookup Failure or Query Exception.
                    </td>
                </tr>
            `;
        });
}

// 5. Shipping Station Logic
function loadShippingFormSetup() {
    // Populate active orders dropdown list
    fetch("/api/orders")
        .then(res => res.json())
        .then(orders => {
            const dropdown = document.getElementById("labelOrderId");
            dropdown.innerHTML = '';

            orders.forEach(order => {
                const opt = document.createElement("option");
                opt.value = order.id;
                opt.innerText = `${order.orderNumber} (${order.customerName} - ${order.status})`;
                dropdown.appendChild(opt);
            });
        })
        .catch(err => console.error("Error setting up shipping dropdown:", err));
}

function triggerLabelDownload(e) {
    e.preventDefault();

    const orderId = document.getElementById("labelOrderId").value;
    const carrier = document.getElementById("labelCarrier").value.trim();
    const tracking = document.getElementById("labelTracking").value.trim();
    const url = document.getElementById("labelUrl").value.trim();
    const preview = document.getElementById("labelPreviewHolder");

    preview.innerHTML = `<span style="color: var(--primary);">Downloading label from carrier network...</span>`;

    const payload = {
        orderId: parseInt(orderId),
        carrier: carrier,
        trackingNumber: tracking,
        carrierLabelUrl: url
    };

    fetch("/api/shipping/label", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            return res.blob();
        }
        throw new Error("Label download rejected");
    })
    .then(blob => {
        // Convert blob binary bytes to a data URL for preview rendering
        const objectURL = URL.createObjectURL(blob);
        
        // Check if the result resembles an image (SSRF output visualizer)
        preview.innerHTML = `
            <div style="text-align: center; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 16px;">
                <span style="color: var(--success); font-weight: 600; font-size: 13px; margin-bottom: 12px; display: block;">✓ Label Downloaded (${blob.size} bytes)</span>
                <!-- Render download details -->
                <div style="background: #111; color: var(--font-mono); font-family: var(--font-mono); font-size: 11px; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color); text-align: left; width: 100%; max-height: 180px; overflow-y: auto;">
                    <strong>CARRIER DATA DECODE:</strong><br>
                    Status: 200 OK<br>
                    Payload size: ${blob.size} bytes<br>
                    Header: application/octet-stream<br><br>
                    Click printable button to exfiltrate / view content.
                </div>
                <a href="${objectURL}" target="_blank" class="btn" style="margin-top: 16px; padding: 8px 16px; font-size: 12px;">Print Registered Label</a>
            </div>
        `;
    })
    .catch(err => {
        console.error("SSRF Downloader error:", err);
        preview.innerHTML = `
            <span style="color: var(--warning); font-weight: 600; font-size: 13px;">
                Error: Connection Refused or Failed to Retrieve URL Resources.
            </span>
        `;
    });
}
