function fetchPayrollSalary() {
    const id = document.getElementById("payrollEmployeeId").value;
    if (!id) return;

    fetch(`/api/payroll/${id}`)
        .then(res => {
            if (res.ok) {
                return res.json();
            } else if (res.status === 404) {
                alert("Employee not found or no payroll record available.");
                throw new Error("404");
            } else {
                alert("Access Denied or System Error.");
                throw new Error("HTTP error " + res.status);
            }
        })
        .then(data => {
            document.getElementById("payrollName").innerText = data.employeeName;
            document.getElementById("payrollDept").innerText = data.departmentName;
            document.getElementById("payrollSalary").innerText = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(data.baseSalary);
            document.getElementById("payrollResult").style.display = "block";
        })
        .catch(err => {
            console.error("Error fetching payroll data", err);
            document.getElementById("payrollResult").style.display = "none";
        });
}
