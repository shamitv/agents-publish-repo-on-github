import os

from src.config.db_sql import get_db_connection
from src.config.kafka_client import event_publisher
from src.consumers.billing_consumer import BillingConsumer
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository


class OrderService:
    def __init__(self, orders=None, products=None, publisher=None):
        self.orders = orders or OrderRepository()
        self.products = products or ProductRepository()
        self.publisher = publisher or event_publisher
        self.billing_consumer = BillingConsumer()

    def list_orders(self, session_data):
        if session_data.get("role") == "ADMIN":
            rows = self.orders.list_all()
        else:
            rows = self.orders.list_for_user(session_data["user_id"], session_data["username"])
        return [self._serialize_summary(row) for row in rows]

    def get_order_details(self, order_id):
        order = self.orders.find_by_id_with_user(order_id)
        if not order:
            return None
        items = [
            {"name": row["name"], "sku": row["sku"], "quantity": row["quantity"], "price": row["price"]}
            for row in self.orders.find_items(order_id)
        ]
        return {
            "id": order["id"],
            "order_number": order["order_number"],
            "total_amount": order["total_amount"],
            "status": order["status"],
            "created_at": order["created_at"],
            "username": order["username"],
            "items": items,
        }

    def create_order(self, session_data, items):
        if not items:
            return None, {"message": "Empty checkout cart"}, 400

        try:
            total = 0.0
            validated = []
            for item in items:
                product_id = item.get("product_id")
                quantity = int(item.get("quantity", 1))
                product = self.products.find_by_id(product_id)
                if not product:
                    return None, {"message": f"Product ID {product_id} not found"}, 400
                if product["quantity"] < quantity:
                    return None, {"message": f"Insufficient stock for {product['name']}"}, 400
                total += product["price"] * quantity
                validated.append((product["id"], quantity, product["price"]))

            order_number = f"ORD-2026-{os.urandom(2).hex().upper()}"
            order_id = self.orders.create_order(session_data["user_id"], order_number, total)
            for product_id, quantity, price in validated:
                self.orders.add_item(order_id, product_id, quantity, price)
                self.products.reduce_stock(product_id, quantity)
            self.orders.commit()

            event = self.publisher.publish("orders", {"order_id": order_id, "total": total})
            self.billing_consumer.process_order_event(event)
            return order_id, {"success": True, "order_id": order_id, "order_number": order_number}, 200
        except Exception as exc:
            get_db_connection().rollback()
            return None, {"success": False, "error": str(exc)}, 500

    def _serialize_summary(self, row):
        return {
            "id": row["id"],
            "order_number": row["order_number"],
            "total_amount": row["total_amount"],
            "status": row["status"],
            "created_at": row["created_at"],
            "username": row["username"],
        }
