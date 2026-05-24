document.addEventListener("DOMContentLoaded", () => {
    loadEmployees();
});

function loadEmployees(query = "") {
    let url = "/api/employees";
    if (query) {
        url += "?q=" + encodeURIComponent(query);
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("employeeTableBody");
            tbody.innerHTML = "";
            data.forEach(emp => {
                const tr = document.createElement("tr");
                
                // Determine actions column based on user role (checking if actions exist)
                const hasAdminActions = document.querySelector("th[sec\\:authorize='hasRole(\\'ROLE_HR_ADMIN\\')']") || 
                                       document.getElementById("employeeModal") !== null;

                let actionHtml = "";
                if (hasAdminActions) {
                    actionHtml = `
                        <td>
                            <button class="btn btn-secondary" onclick='openEditModal(${JSON.stringify(emp)})' style="width:auto; padding: 4px 8px; font-size:12px; display:inline-block; margin-right:4px;">Edit</button>
                            <button class="btn btn-secondary" onclick='deleteEmployee(${emp.id})' style="width:auto; padding: 4px 8px; font-size:12px; display:inline-block; background-color:rgba(239,68,68,0.1); color:var(--danger);">Delete</button>
                        </td>
                    `;
                }

                tr.innerHTML = `
                    <td>${emp.id}</td>
                    <td>${emp.firstName} ${emp.lastName}</td>
                    <td>${emp.email}</td>
                    <td>${emp.departmentName}</td>
                    <td><span class="badge ${emp.role === 'HR_ADMIN' ? 'badge-primary' : (emp.role === 'MANAGER' ? 'badge-warning' : 'badge-success')}">${emp.role}</span></td>
                    <td>${emp.maskedSsn || "None"}</td>
                    ${actionHtml}
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Error loading employees", err));
}

function performSearch() {
    const q = document.getElementById("searchInput").value;
    loadEmployees(q);
}

// Modal control
function openCreateModal() {
    document.getElementById("modalTitle").innerText = "Add New Employee";
    document.getElementById("empId").value = "";
    document.getElementById("empFirstName").value = "";
    document.getElementById("empLastName").value = "";
    document.getElementById("empEmail").value = "";
    document.getElementById("empPassword").value = "";
    document.getElementById("passwordGroup").style.display = "block";
    document.getElementById("empSsn").value = "";
    document.getElementById("empSalary").value = "";
    document.getElementById("employeeModal").classList.add("show");
}

function openEditModal(emp) {
    document.getElementById("modalTitle").innerText = "Edit Employee";
    document.getElementById("empId").value = emp.id;
    document.getElementById("empFirstName").value = emp.firstName;
    document.getElementById("empLastName").value = emp.lastName;
    document.getElementById("empEmail").value = emp.email;
    document.getElementById("empPassword").value = "";
    document.getElementById("passwordGroup").style.display = "none";
    document.getElementById("empRole").value = emp.role;
    document.getElementById("empSsn").value = ""; // Masked is returned, so keep blank unless updating
    
    // Set matching department
    const select = document.getElementById("empDept");
    for (let opt of select.options) {
        if (opt.text === emp.departmentName) {
            select.value = opt.value;
            break;
        }
    }
    
    // We need to fetch full details (like raw salary) to pre-populate correctly since DTO might mask or omit details
    fetch(`/api/payroll/${emp.id}`)
        .then(res => res.json())
        .then(payroll => {
            document.getElementById("empSalary").value = payroll.baseSalary;
        })
        .catch(() => {
            document.getElementById("empSalary").value = "50000";
        });

    document.getElementById("employeeModal").classList.add("show");
}

function closeEmployeeModal() {
    document.getElementById("employeeModal").classList.remove("show");
}

function saveEmployee(event) {
    event.preventDefault();
    const id = document.getElementById("empId").value;
    const isEdit = !!id;
    const url = isEdit ? `/api/employees/${id}` : "/api/employees";
    const method = isEdit ? "PUT" : "POST";

    const payload = {
        firstName: document.getElementById("empFirstName").value,
        lastName: document.getElementById("empLastName").value,
        email: document.getElementById("empEmail").value,
        role: document.getElementById("empRole").value,
        departmentId: document.getElementById("empDept").value,
        salary: parseFloat(document.getElementById("empSalary").value)
    };

    const ssn = document.getElementById("empSsn").value;
    if (ssn) {
        payload.ssn = ssn;
    }

    if (!isEdit) {
        payload.password = document.getElementById("empPassword").value;
    }

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (res.ok) {
            closeEmployeeModal();
            loadEmployees();
        } else {
            alert("Error saving employee");
        }
    })
    .catch(err => console.error("Error", err));
}

function deleteEmployee(id) {
    if (confirm("Are you sure you want to delete this employee?")) {
        fetch(`/api/employees/${id}`, { method: "DELETE" })
            .then(res => {
                if (res.ok) {
                    loadEmployees();
                } else {
                    alert("Error deleting employee");
                }
            });
    }
}

function openImportModal() {
    document.getElementById("importModal").classList.add("show");
}

function closeImportModal() {
    document.getElementById("importModal").classList.remove("show");
}

function uploadImportFile(event) {
    event.preventDefault();
    const fileInput = document.getElementById("importFile");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/api/employees/import", {
        method: "POST",
        body: formData
    })
    .then(res => {
        if (res.ok) {
            alert("Employees imported successfully!");
            closeImportModal();
            loadEmployees();
        } else {
            alert("Import failed. Ensure the file contains a valid serialised List<Employee>.");
        }
    })
    .catch(err => console.error("Error importing", err));
}
