// -------------------------------------------------------------
// App 02 - Nexus Health Vault Patient Portal Client JavaScript
// -------------------------------------------------------------
let currentUser = null;
let currentView = 'dashboard';
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
            // Set IDOR visualizer default input to current user's patient_id
            document.getElementById("idorPatientIdInput").value = user.patient_id;
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
    // Django standard CSRF bypass is handled via @csrf_exempt in view
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
    if (viewName === 'dashboard') {
        if (currentUser) {
            // Load the current patient's records on boot
            loadRecords(currentUser.patient_id);
        }
    } else if (viewName === 'scheduler') {
        loadAppointments();
    }
}
// 1. Diagnostics Records Vault (A01 horizontal IDOR sandbox!)
function loadRecords(patientId) {
    // allowing other patients' diagnostics/prescriptions to be downloaded without ownership checks.
    fetch(`/api/patients/${patientId}/records`)
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("ACCESS DENIED: Privileged Vault Lockout");
        })
        .then(data => {
            document.getElementById("recordPatientName").innerText = data.full_name;
            document.getElementById("recordBloodBadge").innerText = `BLOOD: ${data.blood_type}`;
            document.getElementById("recordPatientId").innerText = `PATIENT-${String(data.patient_id).padStart(4, '0')}`;
            document.getElementById("recordDob").innerText = data.date_of_birth;
            const tbody = document.getElementById("prescriptionsTableBody");
            tbody.innerHTML = '';
            if (data.prescriptions.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No active clinical prescriptions filed.
                        </td>
                    </tr>
                `;
                return;
            }
            data.prescriptions.forEach(rx => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="font-weight: 700; color: #fff;">${rx.medication_name}</td>
                    <td style="font-family: var(--font-mono); color: var(--secondary);">${rx.dosage}</td>
                    <td style="font-size: 13px; color: var(--text-muted);">${rx.frequency}</td>
                    <td style="font-weight: 600;">${rx.prescribing_doctor}</td>
                    <td style="background: rgba(0, 229, 255, 0.01); line-height: 1.6; font-size: 13px;">${rx.diagnostic_notes || '—'}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("Clinical exfiltration rejected:", err);
            alert(err.message);
        });
}
function triggerIdorRecordFetch() {
    const id = parseInt(document.getElementById("idorPatientIdInput").value);
    if (!isNaN(id)) {
        loadRecords(id);
    }
}
// 2. Appointment Scheduler View
function loadAppointments() {
    fetch("/api/appointments")
        .then(res => res.json())
        .then(appts => {
            const tbody = document.getElementById("appointmentsTableBody");
            tbody.innerHTML = '';
            if (appts.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 32px;">
                            No consultations scheduled.
                        </td>
                    </tr>
                `;
                return;
            }
            appts.forEach(appt => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="font-weight: 700; color: var(--secondary);">${appt.patient_name}</td>
                    <td style="font-weight: 600;">${appt.clinic_department}</td>
                    <td>
                        <div style="font-family: var(--font-mono); color: #fff;">${appt.scheduled_date}</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${appt.scheduled_time}</div>
                    </td>
                    <td style="font-size: 13px; line-height: 1.5; color: var(--text-muted);">${appt.reason_for_visit}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading consultations queue:", err));
}
function handleAppointmentSubmit(e) {
    e.preventDefault();
    const payload = {
        clinic_department: document.getElementById("apptDept").value,
        scheduled_date: document.getElementById("apptDate").value,
        scheduled_time: document.getElementById("apptTime").value.trim(),
        reason_for_visit: document.getElementById("apptReason").value.trim()
    };
    fetch("/api/appointments/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            document.getElementById("appointmentForm").reset();
            loadAppointments();
        } else {
            alert("Failed to submit clinic appointment request.");
        }
    })
    .catch(err => console.error("Error scheduling appointment:", err));
}