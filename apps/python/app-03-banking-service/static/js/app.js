// -------------------------------------------------------------
// App 03 - Sovereign Wealth Management Client JavaScript
// -------------------------------------------------------------

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
            document.getElementById("currentUserRoleLabel").innerText = `ROLE: ${user.role}`;

            document.getElementById("authPortal").style.display = 'none';
            document.getElementById("appLayout").style.display = 'flex';
            
            loadBalance();
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
        loadBalance();
        loadLedger();
    }
}

// Balance retrieval
function loadBalance() {
    fetch("/api/accounts/balance")
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Ledger balance lookup failed");
        })
        .then(data => {
            document.getElementById("ledgerBalanceVal").innerText = `$${data.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
            document.getElementById("ledgerAccountNum").innerText = data.account_number;
            document.getElementById("ledgerRoutingNum").innerText = data.routing_number;
            document.getElementById("ledgerClientName").innerText = data.full_name;
        })
        .catch(err => console.error("Balance fetch error:", err));
}

function loadLedger(customFilterStr = '') {
    const consoleFeed = document.getElementById("nosqlConsoleFeed");
    let url = "/api/transactions";
    
    if (customFilterStr) {
        url += `?filter=${encodeURIComponent(customFilterStr)}`;
    }

    fetch(url)
        .then(res => {
            if (res.ok) return res.json();
            return res.json().then(err => { throw new Error(err.detail || "Query Failed") });
        })
        .then(data => {
            consoleFeed.innerHTML = `[NoSQL QUERY PIPELINE OK] - Status: 200 OK\nExecuting In-Memory Mongo Collection lookup:\nfind(${data.debug_nosql_query})`;
            
            const tbody = document.getElementById("ledgerTableBody");
            tbody.innerHTML = '';

            if (data.transactions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No matching ledger entries found.
                        </td>
                    </tr>
                `;
                return;
            }

            data.transactions.forEach(t => {
                const tr = document.createElement("tr");
                const isDebit = t.sender === currentUser.username;
                const flowIcon = isDebit ? "🔴 DEBIT OUT" : "🟢 CREDIT IN";
                const badgeClass = isDebit ? "badge-debit" : "badge-credit";
                const displayAmt = isDebit ? `-$${t.amount.toFixed(2)}` : `+$${t.amount.toFixed(2)}`;

                tr.innerHTML = `
                    <td><span class="badge ${badgeClass}">${flowIcon}</span></td>
                    <td style="font-family: var(--font-mono); color: #fff;">${t.sender}</td>
                    <td style="font-family: var(--font-mono);">${t.receiver}</td>
                    <td style="font-family: var(--font-mono); font-weight: 700; color: ${isDebit ? 'var(--danger)' : 'var(--secondary)'};">${displayAmt}</td>
                    <td><span class="badge badge-info" style="font-weight:600;">${t.category}</span></td>
                    <td style="font-size: 13px; color: var(--text-muted);">${t.description}</td>
                    <td style="font-size: 12px; font-family: var(--font-mono); color: var(--text-muted);">${t.timestamp}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("NoSQL execution rejected:", err);
            consoleFeed.innerHTML = `<span style="color: var(--danger);">[NoSQL EXCEPTION REJECTED]:\n${err.message}</span>`;
        });
}

function triggerNoSqlFilterSearch() {
    const filterText = document.getElementById("nosqlFilterInput").value.trim();
    loadLedger(filterText);
}

function handleTransferSubmit(e) {
    e.preventDefault();

    const payload = {
        recipient_account: document.getElementById("wireRecipient").value.trim(),
        amount: parseFloat(document.getElementById("wireAmount").value),
        description: document.getElementById("wireDesc").value.trim(),
        category: document.getElementById("wireCategory").value
    };

    fetch("/api/transfers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) return res.json();
        return res.json().then(err => { throw new Error(err.detail || "Wire transfer rejected") });
    })
    .then(data => {
        document.getElementById("transferForm").reset();
        alert("Wire Transfer dispatched successfully! Available Balance adjusted.");
        loadBalance();
    })
    .catch(err => {
        console.error("Wire transfer failed:", err);
        alert(err.message);
    });
}

function triggerAutomatedStressWMS() {
    const stressOutput = document.getElementById("rateLimitStressOutput");
    stressOutput.innerHTML = `<span style="color: var(--primary);">INITIALIZING BATCH FLOOD STRESS TESTS...\nLaunching 10 concurrent requests to account number 10008273 ($5.00 each)</span>`;

    const payload = {
        recipient_account: "10008273", // Bob's Account
        amount: 5.00,
        description: "Automated Rate Limit Stress Verification Test",
        category: "Utilities"
    };

    // Execute 10 POST transfers in parallel using Promise.all()!
    const requests = [];
    const startTime = performance.now();

    for (let i = 0; i < 10; i++) {
        requests.push(
            fetch("/api/transfers", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }).then(res => ({ ok: res.ok, status: res.status }))
        );
    }

    Promise.all(requests)
        .then(results => {
            const duration = (performance.now() - startTime).toFixed(1);
            const successfulCount = results.filter(r => r.ok).length;
            const failedCount = results.length - successfulCount;

            stressOutput.innerHTML = `
[RATE-LIMIT STRESS COMPLETE] - Time elapsed: ${duration}ms
• Dispatched requests: 10
• Successful credit adjustments: <span style="color: var(--secondary); font-weight:700;">${successfulCount}</span>
• Blocked rate limit exceptions: <span style="color: ${failedCount > 0 ? 'var(--danger)' : 'var(--text-muted)'}; font-weight:700;">${failedCount}</span>

${failedCount === 0 
    ? "⚠️ ANALYSIS WARNING: 0 requests were rate limited! Automated script succeeded. Account balance depleted rapidly." 
    : "✅ ANALYSIS CONFIRMED: Throttler correctly locked out script execution."}
            `;
            loadBalance();
        })
        .catch(err => {
            stressOutput.innerHTML = `<span style="color: var(--danger);">STRESS PIPELINE FAILURE:\n${err.message}</span>`;
        });
}
