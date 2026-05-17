// -------------------------------------------------------------
// App 04 - Sovereign Realty Terminus Client JavaScript
// -------------------------------------------------------------

let currentUser = null;
let currentView = 'board';

document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication();
});

// Verify active identity session
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
    if (viewName === 'board') {
        loadProperties();
    } else if (viewName === 'messages') {
        loadMessages();
    }
}

// 1. Property Board
function loadProperties() {
    fetch("/api/properties")
        .then(res => res.json())
        .then(props => {
            const grid = document.getElementById("listingsGrid");
            grid.innerHTML = '';

            props.forEach(p => {
                const card = document.createElement("div");
                card.className = "listing-card";
                
                // Fallback visual backgrounds representing real estate
                let mockBgColor = "#1f2235";
                if (p.category === 'Apartment') mockBgColor = "linear-gradient(45deg, #1b1612, #3c2f21)";
                else if (p.category === 'Loft') mockBgColor = "linear-gradient(45deg, #0f1015, #222638)";
                else if (p.category === 'House') mockBgColor = "linear-gradient(45deg, #091a18, #18332c)";
                else mockBgColor = "linear-gradient(45deg, #26111e, #1a0b14)";

                card.innerHTML = `
                    <div>
                        <div class="image-block" style="background: ${mockBgColor};">
                            <span class="price-badge">$${p.price.toLocaleString()}</span>
                        </div>
                        <div class="details">
                            <div>
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                                    <span class="form-label" style="color: var(--primary); font-size:10px;">${p.category}</span>
                                    <span style="font-size:11px; font-family:var(--font-mono); color: var(--text-muted);">ID: ${p.id}</span>
                                </div>
                                <h3 class="title">${p.title}</h3>
                                <div class="location" style="margin-top: 8px;">📍 ${p.location}</div>
                                <p style="font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-top: 12px;">${p.description}</p>
                            </div>
                        </div>
                    </div>
                    <div style="padding: 0 24px 24px 24px;">
                        <button onclick="openContactModal(${p.id}, '${p.title.replace(/'/g, "\\'")}')" class="btn" style="width: 100%;">
                            Contact Agent
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => console.error("Failed to load listings:", err));
}

// 2. SSRF Media Downloader (A10 Sandbox visualizer!)
function triggerSsrfImport() {
    const url = document.getElementById("ssrfUrlInput").value.trim();
    const feed = document.getElementById("ssrfConsoleFeed");

    if (!url) return;

    feed.innerText = `[SSRF PIPELINE CONNECTING] - Probing remote target:\nGET ${url}...`;

    fetch("/api/properties/import-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            feed.innerHTML = `
<span style="color: var(--success); font-weight:700;">[SSRF FETCH SUCCESSFUL - 200 OK]</span>
• Resolved content length: ${data.bytes_fetched} bytes
• Response content-type: ${data.content_type || 'unspecified'}
• Connection state: established
            `;
        } else {
            feed.innerHTML = `
<span style="color: var(--danger); font-weight:700;">[SSRF TARGET TIMEOUT / REJECTED]</span>
• Connection error detail:
${data.error}
            `;
        }
    })
    .catch(err => {
        feed.innerHTML = `<span style="color: var(--danger);">Connection exception: ${err.message}</span>`;
    });
}

// 3. Subprocess command runner (A03 Sandbox visualizer!)
function triggerSubprocessAnalyze() {
    const filename = document.getElementById("osCommandInput").value.trim();
    const feed = document.getElementById("osConsoleFeed");

    if (!filename) return;

    feed.innerText = `[OS SUBPROCESS POPEN EXECUTION] - Launching echo shell command...`;

    fetch("/api/properties/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: filename })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            feed.innerHTML = `
<span style="color: var(--success); font-weight:700;">[SUBPROCESS COMPLETE - EXIT CODE 0]</span>
• Command dispatched: <code style="color: var(--secondary);">${data.cmd_executed}</code>

• Shell stdout stream output:
${data.output || '(empty output stream)'}
            `;
        } else {
            feed.innerHTML = `<span style="color: var(--danger);">[SHELL EXCEPTION REJECTED]:\n${data.error}</span>`;
        }
    })
    .catch(err => {
        feed.innerHTML = `<span style="color: var(--danger);">Connection error: ${err.message}</span>`;
    });
}

// 4. Listing Agent Messages View
function loadMessages() {
    fetch("/api/messages")
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("ACCESS FORBIDDEN: Listing Agent license signature required.");
        })
        .then(msgs => {
            const tbody = document.getElementById("messagesTableBody");
            tbody.innerHTML = '';

            if (msgs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No messages routes found.
                        </td>
                    </tr>
                `;
                return;
            }

            msgs.forEach(m => {
                const tr = document.createElement("tr");
                const dateStr = m.created_at ? m.created_at.substring(0, 16).replace("T", " ") : "-";

                tr.innerHTML = `
                    <td style="font-family: var(--font-luxury); font-size:12px; color: var(--primary);">${m.property_title}</td>
                    <td style="font-weight: 700; color:#fff;">${m.client_name}</td>
                    <td style="font-family: var(--font-mono);">${m.client_phone}</td>
                    <td style="font-size: 13px; line-height:1.5; color: var(--text-muted);">${m.message_content}</td>
                    <td style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted);">${dateStr}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("Messages lookup failed:", err);
            const tbody = document.getElementById("messagesTableBody");
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: var(--danger); font-family:var(--font-mono); font-weight:700; padding: 32px;">
                        [ROUTING EXCEPTION ERROR]: ${err.message.toUpperCase()}
                    </td>
                </tr>
            `;
        });
}

// Add listings modals
function openAddPropertyModal() {
    document.getElementById("addPropertyModal").style.display = 'flex';
}

function closeAddPropertyModal() {
    document.getElementById("addPropertyModal").style.display = 'none';
}

function handleAddPropertySubmit(e) {
    e.preventDefault();

    const payload = {
        title: document.getElementById("addTitle").value.trim(),
        category: document.getElementById("addCategory").value,
        price: parseFloat(document.getElementById("addPrice").value),
        location: document.getElementById("addLocation").value.trim(),
        description: document.getElementById("addDesc").value.trim()
    };

    fetch("/api/properties", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeAddPropertyModal();
            document.getElementById("addPropertyForm").reset();
            loadProperties();
        } else {
            alert("Failed to create property. Sign-in required.");
        }
    })
    .catch(err => console.error("Error adding property:", err));
}

// Contact Agent Modals
function openContactModal(propId, title) {
    document.getElementById("contactPropertyId").value = propId;
    document.getElementById("contactForm").reset();
    document.getElementById("contactMsg").value = `Hello, I would like to schedule a virtual coordinate tour of ${title}. Please send availability logs.`;
    document.getElementById("contactModal").style.display = 'flex';
}

function closeContactModal() {
    document.getElementById("contactModal").style.display = 'none';
}

function handleContactSubmit(e) {
    e.preventDefault();

    const payload = {
        property_id: parseInt(document.getElementById("contactPropertyId").value),
        client_name: document.getElementById("contactName").value.trim(),
        client_phone: document.getElementById("contactPhone").value.trim(),
        message_content: document.getElementById("contactMsg").value.trim()
    };

    fetch("/api/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeContactModal();
            alert("Message routed successfully to the Listing Agent! Callback scheduled.");
        } else {
            alert("Failed to route message.");
        }
    })
    .catch(err => console.error("Contact submit error:", err));
}
