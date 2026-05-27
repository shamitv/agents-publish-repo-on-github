import csv
import io

from flask import jsonify, request, session

from src.services.product_service import ProductService


product_service = ProductService()


def bulk_upload_products():
    if "user_id" not in session or session.get("role") != "ADMIN":
        return jsonify({"message": "Forbidden: Administrator role required"}), 403

    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "error": "No file provided"}), 400

    # Read CSV and create products in bulk
    stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)

    created = []
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        try:
            product_data = {
                "sku": row["sku"],
                "name": row["name"],
                "description": row.get("description", ""),
                "category": row.get("category", ""),
                "price": float(row["price"]),
                "quantity": int(row["quantity"]),
            }
            product_id = product_service.create_product(product_data)
            created.append({"row": row_idx, "product_id": product_id, "sku": product_data["sku"]})
        except Exception as exc:
            errors.append({"row": row_idx, "error": str(exc)})

    return jsonify({
        "success": True,
        "created_count": len(created),
        "error_count": len(errors),
        "created": created,
        "errors": errors,
    })