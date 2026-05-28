from flask import Blueprint

from src.controllers.bulk_upload_controller import bulk_upload_products


bulk_upload_bp = Blueprint("bulk_upload", __name__, url_prefix="/api/products")


bulk_upload_bp.add_url_rule(
    "/bulk-upload",
    view_func=bulk_upload_products,
    methods=["POST"],
)