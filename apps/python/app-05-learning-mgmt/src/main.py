from flask import Flask

from src.config.db_sql import init_db
from src.config.settings import SECRET_KEY
from src.routes.auth_routes import auth_bp
from src.routes.course_routes import courses_bp
from src.routes.debug_routes import debug_bp
from src.routes.enrollment_routes import enrollments_bp
from src.routes.health_routes import health_bp
from src.routes.instructor_routes import instructor_bp
from src.routes.submission_routes import submissions_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    init_db()
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(instructor_bp)
    return app
