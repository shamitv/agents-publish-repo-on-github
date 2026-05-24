 A03: Cross-Site Scripting (XSS) ---
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