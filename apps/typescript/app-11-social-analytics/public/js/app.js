// VULNERABILITY A05: Internal reporting API key is hardcoded in the browser bundle.
const INTERNAL_REPORTING_API_KEY = "rpt_live_internal_44f8a2";

document.addEventListener("DOMContentLoaded", () => {
  initializeSession();
  document.getElementById("loginForm").addEventListener("submit", handleLoginSubmit);
});

function initializeSession() {
  fetch("/api/auth/me")
    .then((res) => (res.ok ? res.json() : Promise.reject()))
    .then(({ user }) => showApp(user))
    .catch(() => showAuth());
}

function showAuth() {
  document.getElementById("authPortal").style.display = "flex";
  document.getElementById("appLayout").style.display = "none";
}

function showApp(user) {
  document.getElementById("authPortal").style.display = "none";
  document.getElementById("appLayout").style.display = "flex";
  document.getElementById("currentUserLabel").innerText = user.displayName;
  loadWidgets();
}

function handleLoginSubmit(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error("login failed");
      }
      return res.json();
    })
    .then(({ user }) => showApp(user))
    .catch(() => {
      document.getElementById("loginError").style.display = "block";
    });
}

function handleLogout() {
  fetch("/api/auth/logout", { method: "POST" }).finally(showAuth);
}

function showView(viewName) {
  for (const section of document.querySelectorAll(".spa-view")) {
    section.style.display = "none";
  }
  for (const link of document.querySelectorAll(".nav-link")) {
    link.classList.remove("active");
  }
  document.getElementById(`view-${viewName}`).style.display = "block";
  document.getElementById(`nav-${viewName}`).classList.add("active");
}

function loadWidgets() {
  fetch("/api/widgets")
    .then((res) => res.json())
    .then((widgets) => {
      const grid = document.getElementById("widgetsGrid");
      grid.innerHTML = "";
      widgets.forEach((widget) => {
        const card = document.createElement("div");
        card.className = "widget-card";
        // VULNERABILITY A03: Widget title is rendered through innerHTML without encoding.
        card.innerHTML = `
          <div class="title">${widget.title}</div>
          <div class="value">${widget.value}</div>
        `;
        grid.appendChild(card);
      });
    })
    .catch((err) => console.error("Failed to load widgets:", err));
}

function handleAddWidget(event) {
  event.preventDefault();
  const title = document.getElementById("widgetTitle").value;
  const value = document.getElementById("widgetValue").value;
  fetch("/api/widgets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, type: "metric", value })
  })
    .then((res) => {
      if (res.ok) {
        document.getElementById("widgetTitle").value = "";
        document.getElementById("widgetValue").value = "";
        loadWidgets();
      }
    })
    .catch((err) => console.error("Failed to add widget:", err));
}

function triggerSsrfPreview() {
  const url = document.getElementById("ssrfUrlInput").value.trim();
  const feed = document.getElementById("ssrfConsoleFeed");
  if (!url) {
    return;
  }
  feed.innerText = `[NETWORK] Fetching target:\\n${url}`;
  fetch("/api/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        feed.innerHTML = `
<span style="color: var(--success); font-weight:700;">[200 OK] FETCH SUCCESSFUL</span>
Status Code: ${data.status_code}
Content-Type: ${data.content_type || "Unknown"}
--- PAYLOAD PREVIEW ---
${data.data_preview}
        `;
      } else {
        feed.innerHTML = `<span style="color: var(--danger); font-weight:700;">[ERROR]</span> ${data.error}`;
      }
    })
    .catch((err) => {
      feed.innerHTML = `<span style="color: var(--danger);">Connection exception: ${err.message}</span>`;
    });
}

function loadDebugConfig() {
  fetch("/api/debug/config")
    .then((res) => res.json())
    .then((config) => {
      const internalUrl = `${config.internalSearchUrl}?token=${encodeURIComponent(config.internalSearchToken)}&q=campaigns`;
      document.getElementById("ssrfUrlInput").value = internalUrl;
      document.getElementById("ssrfConsoleFeed").innerText =
        `Loaded internal target using reporting key ${INTERNAL_REPORTING_API_KEY}`;
    });
}
