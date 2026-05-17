// -------------------------------------------------------------
// App 12 - Aether Wallet Client JavaScript
// -------------------------------------------------------------

let currentUser = null;
let currentView = 'dashboard';
let currentWallet = null;

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
        if (res.status === 201 || res.status === 200) {
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
        loadDashboard();
    }
}

function loadDashboard() {
    fetch("/api/wallet")
        .then(res => res.json())
        .then(wallet => {
            currentWallet = wallet;
            document.getElementById("walletBalance").innerText = wallet.balance.toFixed(4);
            document.getElementById("walletAddress").innerText = wallet.address;
            
            // OWASP A02: Plaintext private key exposed!
            document.getElementById("walletPrivateKey").innerText = wallet.privateKey;
            
            loadTransactions();
        })
        .catch(err => console.error("Failed to load wallet:", err));
}

function loadTransactions() {
    fetch("/api/wallet/transactions")
        .then(res => res.json())
        .then(txs => {
            const tbody = document.getElementById("txTableBody");
            tbody.innerHTML = '';

            if (txs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No transactions found.</td></tr>`;
                return;
            }

            txs.forEach(t => {
                const isOut = t.sender === currentWallet.address;
                const typeHtml = isOut ? `<span class="badge badge-out">SENT</span>` : `<span class="badge badge-in">RECEIVED</span>`;
                const otherParty = isOut ? t.receiver : t.sender;
                
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${typeHtml}</td>
                    <td>${otherParty}</td>
                    <td style="color: ${isOut ? 'var(--danger)' : 'var(--success)'};">${isOut ? '-' : '+'}${t.amount.toFixed(4)}</td>
                    <td>${new Date(t.timestamp).toLocaleString()}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Failed to load transactions:", err));
}

function handleTransfer(e) {
    e.preventDefault();
    const recipientAddress = document.getElementById("transferRecipient").value.trim();
    const amount = parseFloat(document.getElementById("transferAmount").value);

    // OWASP A04/A07: Immediate execution without confirmation or MFA!
    fetch("/api/wallet/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipientAddress, amount })
    })
    .then(async res => {
        if (res.status === 201 || res.status === 200) {
            alert("Transfer executed successfully!");
            document.getElementById("transferRecipient").value = '';
            document.getElementById("transferAmount").value = '';
            showView('dashboard');
        } else {
            const err = await res.json();
            alert(`Transfer failed: ${err.message}`);
        }
    })
    .catch(err => console.error("Transfer failed:", err));
}
