// -------------------------------------------------------------
// App 11 - Neon Analytics Client JavaScript
// -------------------------------------------------------------

// --- OWASP VULNERABILITY A05: Security Misconfiguration ---
// Sensitive internal reporting API key is hardcoded directly in the client bundle!
const INTERNAL_REPORTING_API_KEY = "sk_live_neon_984123491024_auth";

let currentUser = null;
let currentView = 'dashboard';

document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication();
});

function checkAuthentication() {
    fetch("/api/auth/me")
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Unauthenticated");
        })
        .then(user => {
            currentUser = user;
            document.getElementById("currentUserLabel").innerText = user.username;

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

function showView(viewName) {
    currentView = viewName;

    document.querySelectorAll(".sidebar .nav-link").forEach(link => {
        link.classList.remove("active");
    });
    const activeLink = document.getElementById(`nav-${viewName}`);
    if (activeLink) activeLink.classList.add("active");

    document.querySelectorAll(".spa-view").forEach(view => {
        view.style.display = 'none';
    });
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) targetView.style.display = 'block';

    if (viewName === 'dashboard') {
        loadWidgets();
    }
}

// 1. Dashboard View (A03 XSS target)
function loadWidgets() {
    fetch("/api/widgets")
        .then(res => res.json())
        .then(widgets => {
            const grid = document.getElementById("widgetsGrid");
            grid.innerHTML = '';

            widgets.forEach(w => {
                const card = document.createElement("div");
                card.className = "widget-card";
                
                // --- OWASP VULNERABILITY A03: Cross-Site Scripting (XSS) ---
                // The widget title is injected directly into the DOM using innerHTML
                // without any sanitization or encoding.
                card.innerHTML = `
                    <div class="title">${w.title}</div>
                    <div class="value">${w.value}</div>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => console.error("Failed to load widgets:", err));
}

function handleAddWidget(e) {
    e.preventDefault();
    const title = document.getElementById("widgetTitle").value;
    const value = document.getElementById("widgetValue").value;

    fetch("/api/widgets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, type: 'metric', value })
    })
    .then(res => {
        if (res.ok) {
            document.getElementById("widgetTitle").value = '';
            document.getElementById("widgetValue").value = '';
            loadWidgets();
        }
    })
    .catch(err => console.error("Failed to add widget:", err));
}

// 2. URL Preview (A10 SSRF visualizer)
function triggerSsrfPreview() {
    const url = document.getElementById("ssrfUrlInput").value.trim();
    const feed = document.getElementById("ssrfConsoleFeed");

    if (!url) return;

    feed.innerText = `[NETWORK] Initiating fetch for target:\n${url}...`;

    fetch("/api/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            feed.innerHTML = `
<span style="color: var(--success); font-weight:700;">[200 OK] FETCH SUCCESSFUL</span>
• Status Code: ${data.status_code}
• Content-Type: ${data.content_type || 'Unknown'}

<span style="color: var(--primary);">--- PAYLOAD PREVIEW ---</span>
${data.data_preview}
            `;
        } else {
            feed.innerHTML = `
<span style="color: var(--danger); font-weight:700;">[ERROR] FETCH REJECTED</span>
• Reason: ${data.error}
            `;
        }
    })
    .catch(err => {
        feed.innerHTML = `<span style="color: var(--danger);">Connection exception: ${err.message}</span>`;
    });
}
