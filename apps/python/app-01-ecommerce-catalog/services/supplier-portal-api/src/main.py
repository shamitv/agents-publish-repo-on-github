from flask import Flask, jsonify

from .routes.report_routes import report_bp
from .routes.auth_routes import auth_bp
from .routes.portal_routes import portal_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "supplier-portal-secret"
    app.register_blueprint(report_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(portal_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "service": "supplier-portal-api"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002)