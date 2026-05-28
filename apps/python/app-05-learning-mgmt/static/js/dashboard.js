async function api(method, path, body) {
    const opts = { method, headers: { "Content-Type": "application/json" } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(path, opts);
    return res.json();
}

async function loadUser() {
    const data = await api("GET", "/api/auth/me");
    if (data.username) {
        document.getElementById("user-info").textContent = `${data.username} (${data.role})`;
    }
}

async function logout() {
    await api("POST", "/api/auth/logout");
    window.location.href = "/api/health";
}

async function enroll() {
    const courseId = document.getElementById("course-id").value;
    await api("POST", "/api/enrollments", { course_id: parseInt(courseId) });
    alert("Enrolled! (enrollment may not check prerequisites)");
    location.reload();
}

document.addEventListener("DOMContentLoaded", loadUser);

const overrideForm = document.getElementById("override-form");
if (overrideForm) {
    overrideForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(overrideForm);
        const data = await api("POST", "/api/instructor/grades/override", {
            student_id: parseInt(fd.get("student_id")),
            course_id: parseInt(fd.get("course_id")),
            quiz_id: parseInt(fd.get("quiz_id")),
            new_score: parseFloat(fd.get("new_score")),
        });
        alert(data.success ? "Grade overridden!" : "Error: " + data.error);
    });
}
