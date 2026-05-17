document.addEventListener("DOMContentLoaded", () => {
    loadLeaveRequests();
});

let currentUserRole = "EMPLOYEE";

function loadLeaveRequests() {
    fetch("/api/leave/requests")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("leaveRequestsBody");
            tbody.innerHTML = "";
            
            // Detect user role based on layout (simple check)
            const roleEl = document.querySelector(".user-role");
            if (roleEl) {
                currentUserRole = roleEl.innerText;
            }

            data.forEach(req => {
                const tr = document.createElement("tr");
                const name = req.employee.firstName + " " + req.employee.lastName;
                
                let actions = "-";
                if (req.status === "PENDING" && (currentUserRole === "MANAGER" || currentUserRole === "HR_ADMIN")) {
                    actions = `
                        <button class="btn" onclick="updateLeaveStatus(${req.id}, 'APPROVED')" style="width:auto; padding: 4px 8px; font-size:12px; display:inline-block; margin-right:4px; background-color:rgba(16,185,129,0.1); color:var(--success);">Approve</button>
                        <button class="btn btn-secondary" onclick="updateLeaveStatus(${req.id}, 'REJECTED')" style="width:auto; padding: 4px 8px; font-size:12px; display:inline-block; background-color:rgba(239,68,68,0.1); color:var(--danger);">Reject</button>
                    `;
                }

                tr.innerHTML = `
                    <td>${req.id}</td>
                    <td>${name}</td>
                    <td>${req.leaveType}</td>
                    <td>${req.startDate}</td>
                    <td>${req.endDate}</td>
                    <td><span class="badge ${req.status === 'APPROVED' ? 'badge-success' : (req.status === 'REJECTED' ? 'badge-danger' : 'badge-warning')}">${req.status}</span></td>
                    <td>${actions}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading leave requests", err));
}

function openRequestModal() {
    document.getElementById("requestModal").classList.add("show");
}

function closeRequestModal() {
    document.getElementById("requestModal").classList.remove("show");
}

function submitLeave(event) {
    event.preventDefault();
    const payload = {
        leaveType: document.getElementById("leaveType").value,
        startDate: document.getElementById("startDate").value,
        endDate: document.getElementById("endDate").value
    };

    fetch("/api/leave/requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeRequestModal();
            loadLeaveRequests();
        } else {
            alert("Error submitting request");
        }
    })
    .catch(err => console.error("Error submitting request", err));
}

function updateLeaveStatus(id, status) {
    fetch(`/api/leave/requests/${id}/approve`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: status })
    })
    .then(res => {
        if (res.ok) {
            loadLeaveRequests();
        } else {
            alert("Error updating leave request status");
        }
    })
    .catch(err => console.error("Error updating status", err));
}
