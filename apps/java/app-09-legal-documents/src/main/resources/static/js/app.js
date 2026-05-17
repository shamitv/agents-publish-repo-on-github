// -------------------------------------------------------------
// App 09 - Apex Counsel SPA Frontend Client Logic
// -------------------------------------------------------------

let currentUser = null;
let currentView = 'dashboard';
let selectedCaseId = null;

document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication();
});

// Verify active session profile
function checkAuthentication() {
    fetch("/api/users/me")
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Unauthenticated");
        })
        .then(user => {
            currentUser = user;
            document.getElementById("currentUserLabel").innerText = user.username;
            document.getElementById("currentUserRoleLabel").innerText = `Role: ${user.role}`;

            // Attorneys or administrators can establish case portfolios
            if (user.role === 'ATTORNEY' || user.role === 'ADMIN') {
                document.getElementById("addCaseBtn").style.display = 'inline-flex';
            } else {
                document.getElementById("addCaseBtn").style.display = 'none';
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
        console.error("Login request failed:", err);
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
    if (viewName === 'dashboard') {
        loadDashboard();
    } else if (viewName === 'cases') {
        loadCases();
    }
}

// 1. Dashboard View
function loadDashboard() {
    fetch("/api/cases")
        .then(res => res.json())
        .then(cases => {
            const active = cases.filter(c => c.status === 'ACTIVE').length;
            const closed = cases.filter(c => c.status === 'CLOSED').length;
            
            document.getElementById("statActiveCases").innerText = active;
            document.getElementById("statClosedCases").innerText = closed;

            const tbody = document.getElementById("dashboardCasesTableBody");
            tbody.innerHTML = '';

            if (cases.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No assigned cases registered.
                        </td>
                    </tr>
                `;
                return;
            }

            cases.forEach(c => {
                const tr = document.createElement("tr");
                const badgeClass = c.status === 'ACTIVE' ? 'badge-active' : 'badge-closed';
                const createdStr = c.createdAt ? c.createdAt.substring(0, 10) : "-";
                
                tr.innerHTML = `
                    <td style="font-weight: 600; color: #fff;">${c.title}</td>
                    <td style="font-family: var(--font-serif); font-size: 13px; color: var(--primary);">${c.clientOwner}</td>
                    <td><span class="badge ${badgeClass}">${c.status}</span></td>
                    <td style="font-size: 13px; color: var(--text-muted);">${createdStr}</td>
                    <td>
                        <button onclick="jumpToCase(${c.id})" class="btn btn-secondary" style="padding: 6px 12px; font-size: 11px;">Explore</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading dashboard data:", err));
}

function jumpToCase(id) {
    showView('cases');
    selectCase(id);
}

// 2. Cases View
function loadCases() {
    fetch("/api/cases")
        .then(res => res.json())
        .then(cases => {
            const tbody = document.getElementById("casesQueueTableBody");
            tbody.innerHTML = '';

            cases.forEach(c => {
                const tr = document.createElement("tr");
                tr.style.cursor = 'pointer';
                tr.onclick = () => selectCase(c.id);
                
                tr.innerHTML = `
                    <td style="font-weight: 600;">${c.title}</td>
                    <td style="font-family: var(--font-serif); font-size: 12px; color: var(--primary);">${c.clientOwner}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading cases lists:", err));
}

function selectCase(id) {
    selectedCaseId = id;

    fetch("/api/cases")
        .then(res => res.json())
        .then(cases => {
            const c = cases.find(item => item.id === id);
            if (!c) return;

            document.getElementById("caseDetailTitle").innerText = c.title;
            document.getElementById("caseDetailClient").innerText = `Client Portfolio: ${c.clientOwner}`;
            document.getElementById("caseDetailDesc").innerText = c.description || "No description provided.";

            const badge = document.getElementById("caseDetailStatusBadge");
            badge.innerText = c.status;
            badge.className = 'badge';
            if (c.status === 'ACTIVE') badge.classList.add('badge-active');
            else badge.classList.add('badge-closed');

            // Load case documents vault
            return fetch(`/api/cases/${id}/documents`);
        })
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Access denied to parent case folder");
        })
        .then(docs => {
            const tbody = document.getElementById("caseDocumentsTableBody");
            tbody.innerHTML = '';

            if (docs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 24px;">
                            No legal filings submitted under this case.
                        </td>
                    </tr>
                `;
                return;
            }

            docs.forEach(doc => {
                const createdStr = doc.createdAt ? doc.createdAt.substring(0, 16).replace("T", " ") : "-";
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>
                        <div style="font-weight: 600; color: #fff;">${doc.title}</div>
                        <div style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); margin-top: 2px;">${doc.filename}</div>
                    </td>
                    <td style="font-family: var(--font-serif); font-size: 12px; color: var(--primary);">${doc.uploadedBy}</td>
                    <td style="font-size: 12px; color: var(--text-muted);">${createdStr}</td>
                    <td>
                        <button onclick="readDocument(${doc.id})" class="btn" style="padding: 6px 12px; font-size: 11px;">Decrypt & Read</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            document.getElementById("caseDetailsPanel").style.display = 'flex';
        })
        .catch(err => {
            console.error("Failed to select case:", err);
            alert("Error: " + err.message);
        });
}

// 3. Document Reader (Plaintext display - A02 & Missing Auth check A01)
function readDocument(docId) {
    // VULNERABILITY A01: horizontal IDOR bypass target.
    // Fetches individual document details strictly by document ID without any validation checking if
    // the currently logged in user matches the document's parent case owner.
    fetch(`/api/documents/${docId}`)
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Pleadings access rejected by vault controller.");
        })
        .then(doc => {
            document.getElementById("docReaderTitle").innerText = doc.title;
            document.getElementById("docReaderFilename").innerText = doc.filename;
            document.getElementById("docReaderAuthor").innerText = doc.uploadedBy;
            
            // Render unencrypted text directly onto paper reader (A02 target)
            document.getElementById("docPlaintextContent").innerText = doc.fileContentPlaintext;

            // Toggle view to document reader
            document.querySelectorAll(".spa-view").forEach(view => {
                view.style.display = 'none';
            });
            document.getElementById("view-document-reader").style.display = 'block';
        })
        .catch(err => {
            console.error("Vault exfiltration failed:", err);
            alert(err.message);
        });
}

// Add Case Submission
function openAddCaseModal() {
    document.getElementById("addCaseModal").style.display = 'flex';
}

function closeAddCaseModal() {
    document.getElementById("addCaseModal").style.display = 'none';
}

function handleAddCaseSubmit(e) {
    e.preventDefault();

    const payload = {
        title: document.getElementById("addCaseTitle").value.trim(),
        clientOwner: document.getElementById("addCaseOwner").value.trim(),
        description: document.getElementById("addCaseDesc").value.trim()
    };

    fetch("/api/cases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeAddCaseModal();
            document.getElementById("addCaseForm").reset();
            loadCases();
        } else {
            alert("Failed to establish case portfolio. Access Denied.");
        }
    })
    .catch(err => console.error("Error creating case portfolio:", err));
}

// Add Document Submission
function openAddDocModal() {
    if (!selectedCaseId) return;
    document.getElementById("addDocModal").style.display = 'flex';
}

function closeAddDocModal() {
    document.getElementById("addDocModal").style.display = 'none';
}

function handleAddDocSubmit(e) {
    e.preventDefault();

    const payload = {
        caseId: selectedCaseId,
        title: document.getElementById("addDocTitle").value.trim(),
        filename: document.getElementById("addDocFilename").value.trim(),
        fileContentPlaintext: document.getElementById("addDocContent").value.trim()
    };

    fetch("/api/documents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeAddDocModal();
            document.getElementById("addDocForm").reset();
            selectCase(selectedCaseId);
        } else {
            alert("Failed to file document under case portfolio.");
        }
    })
    .catch(err => console.error("Error filing document:", err));
}

// 4. Log4j Custom Payload Event Dispatcher (Visualizer for A06 Log4Shell component)
function dispatchAuditEvent(e) {
    e.preventDefault();

    const headerName = document.getElementById("auditHeader").value;
    const payload = document.getElementById("auditPayload").value;
    const consoleFeed = document.getElementById("auditConsoleFeed");

    consoleFeed.innerText = `Dispatching Event Package...\nHeader: ${headerName}\nPayload: ${payload}\nHTTP Method: GET /api/documents/1\n\n`;

    const headers = {};
    headers[headerName] = payload;

    // Send requests to doc download endpoint (contains the vulnerable Log4j call)
    fetch("/api/documents/1", {
        headers: headers
    })
    .then(res => {
        const timeStr = new Date().toLocaleTimeString();
        consoleFeed.innerText += `[${timeStr}] TELEMETRY RESPONSE: ${res.status} ${res.statusText}\n`;
        if (res.ok) {
            consoleFeed.innerText += `Event dispatched successfully to Log4j logger stream.\nCheck server terminal log feeds for JNDI trigger parameters.`;
        } else {
            consoleFeed.innerText += `Failed to verify log dispatcher stream. Unauthenticated request.`;
        }
    })
    .catch(err => {
        consoleFeed.innerText += `Audit Connection Error: ${err.message}`;
    });
}
