from pathlib import Path

from flask import Flask

from src.config.settings import SECRET_KEY
from src.config.db_sql import init_db
from src.routes.auth_routes import auth_bp
from src.routes.bulk_upload_routes import bulk_upload_bp
from src.routes.health_routes import health_bp
from src.routes.lifecycle_routes import lifecycle_bp
from src.routes.order_routes import orders_bp
from src.routes.page_routes import pages_bp
from src.routes.product_routes import products_bp
from src.routes.user_routes import users_bp


def create_app():
    app_root = Path(__file__).resolve().parents[1]
    app = Flask(__name__, static_folder=str(app_root / "static"), static_url_path="")
    app.secret_key = SECRET_KEY

    init_db()
    app.register_blueprint(pages_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(lifecycle_bp)
    app.register_blueprint(bulk_upload_bp)
    return app
