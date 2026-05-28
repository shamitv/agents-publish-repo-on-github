import os

from flask import Flask

from src.config.db_sql import init_db, wait_for_db
from src.config.db_mongo import init_mongo
from src.config.settings import SECRET_KEY
from src.routes.auth_routes import auth_bp
from src.routes.course_routes import courses_bp
from src.routes.debug_routes import debug_bp
from src.routes.enrollment_routes import enrollments_bp
from src.routes.health_routes import health_bp
from src.routes.instructor_routes import instructor_bp
from src.routes.submission_routes import submissions_bp
from src.routes.dashboard_routes import dashboard_bp
from src.routes.import_routes import import_bp
from src.config.routes.internal import internal_bp


def create_app():
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    app = Flask(__name__, template_folder=template_dir)
    app.secret_key = SECRET_KEY
    wait_for_db()
    init_db()
    init_mongo()
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(internal_bp)
    app.register_blueprint(import_bp)
    return app
