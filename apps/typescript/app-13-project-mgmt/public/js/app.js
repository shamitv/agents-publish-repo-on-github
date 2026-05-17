// -------------------------------------------------------------
// App 13 - CollabSpace Client JavaScript
// -------------------------------------------------------------

let currentUser = null;
let currentView = 'dashboard';
let activeBoardId = null;

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
            document.getElementById("currentOrgLabel").innerText = user.orgId;

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
        loadOrgBoards();
    }
}

function loadOrgBoards() {
    fetch("/api/boards")
        .then(res => res.json())
        .then(boards => {
            const grid = document.getElementById("boardsGrid");
            grid.innerHTML = '';

            boards.forEach(b => {
                const card = document.createElement("div");
                card.className = "board-card";
                card.onclick = () => loadBoard(b.id);
                card.innerHTML = `
                    <div class="board-title">${b.title}</div>
                    <div>
                        <span class="badge">Org ${b.orgId}</span>
                        <span class="badge" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">${b.visibility}</span>
                    </div>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => console.error("Failed to load boards:", err));
}

// OWASP A01 Target: Insecure Direct Object Reference (IDOR)
function loadBoard(boardId) {
    if (!boardId) return;
    
    fetch(`/api/boards/${boardId}`)
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("Board access denied or not found");
        })
        .then(data => {
            activeBoardId = data.board.id;
            document.getElementById("activeBoardTitle").innerText = data.board.title;
            document.getElementById("boardVisibilitySelect").value = data.board.visibility;
            
            renderTasks(data.tasks);
            showView('board');
        })
        .catch(err => alert(err.message));
}

function renderTasks(tasks) {
    const list = document.getElementById("tasksList");
    list.innerHTML = '';

    if (tasks.length === 0) {
        list.innerHTML = `<div style="text-align:center; padding: 24px; color: var(--text-muted); font-size: 13px;">No tasks on this board yet.</div>`;
        return;
    }

    tasks.forEach(t => {
        const card = document.createElement("div");
        card.className = "task-card";
        
        // OWASP A03: Cross-Site Scripting (XSS)
        // Task description is rendered using innerHTML without sanitization
        card.innerHTML = `
            <div class="title">${t.title}</div>
            <div class="desc">${t.description}</div>
        `;
        list.appendChild(card);
    });
}

function handleCreateTask(e) {
    e.preventDefault();
    const title = document.getElementById("taskTitle").value.trim();
    const description = document.getElementById("taskDesc").value;

    fetch(`/api/boards/${activeBoardId}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description })
    })
    .then(res => {
        if (res.ok) {
            document.getElementById("taskTitle").value = '';
            document.getElementById("taskDesc").value = '';
            loadBoard(activeBoardId); // Refresh tasks
        }
    })
    .catch(err => console.error("Failed to add task:", err));
}

// OWASP A09 Target: Security Logging Failure
function updateBoardVisibility() {
    const newVisibility = document.getElementById("boardVisibilitySelect").value;
    
    fetch(`/api/boards/${activeBoardId}/permissions`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ visibility: newVisibility })
    })
    .then(res => {
        if (res.ok) {
            console.log("Permissions updated (Unlogged action)");
        } else {
            alert("Permission update failed. You must be a MANAGER.");
            loadBoard(activeBoardId); // Reset select box
        }
    })
    .catch(err => console.error("Update failed:", err));
}
