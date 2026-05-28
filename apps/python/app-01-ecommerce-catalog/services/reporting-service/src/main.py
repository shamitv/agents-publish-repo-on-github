from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)
    app.secret_key = "reporting-secret-key"

    from src.routes.report_routes import report_bp
    app.register_blueprint(report_bp)

    from src.routes.job_routes import job_bp
    app.register_blueprint(job_bp)

    from src.routes.download_routes import download_bp
    app.register_blueprint(download_bp)

    from src.routes.audit_routes import audit_bp
    app.register_blueprint(audit_bp)

    from src.routes.webhook_routes import webhook_bp
    app.register_blueprint(webhook_bp)

    from src.controllers.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "service": "reporting-service"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8082, debug=True)