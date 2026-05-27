from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = "reporting-secret-key"

    from src.routes.report_routes import report_bp
    app.register_blueprint(report_bp)

    from src.controllers.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8082, debug=True)