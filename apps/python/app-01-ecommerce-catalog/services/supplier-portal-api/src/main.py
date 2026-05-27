"""Supplier Portal API — Flask Blueprint Factory.

This microservice handles supplier-facing operations including:
- Report generation (Phase 02)
- Supplier management (Phase 03)
"""

from flask import Flask

from .routes.report_routes import report_bp


def create_app() -> Flask:
    """Create and configure the Supplier Portal API application."""
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(report_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002)