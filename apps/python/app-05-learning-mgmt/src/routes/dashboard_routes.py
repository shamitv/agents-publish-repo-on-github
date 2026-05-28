from flask import Blueprint, render_template, session, jsonify


dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/student", methods=["GET"])
def student_dashboard():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    return render_template("dashboard_student.html")


@dashboard_bp.route("/instructor", methods=["GET"])
def instructor_dashboard():
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden"}), 403
    return render_template("dashboard_instructor.html")
