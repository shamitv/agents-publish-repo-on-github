from src.config.db_sql import get_db_connection


class ProductRepository:
    def list_all(self):
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT id, sku, name, description, category, price, quantity FROM products")
        return cursor.fetchall(), "SELECT * FROM products"

    def unsafe_search(self, query_text):
        cursor = get_db_connection().cursor()
        query = (
            "SELECT id, sku, name, description, category, price, quantity FROM products "
            f"WHERE name LIKE '%{query_text}%' OR description LIKE '%{query_text}%'"
        )
        cursor.execute(query)
        return cursor.fetchall(), query

    def find_by_id(self, product_id):
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT id, price, quantity, name FROM products WHERE id = ?", (product_id,))
        return cursor.fetchone()

    def create(self, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (sku, name, description, category, price, quantity, supplier_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                data["sku"],
                data["name"],
                data.get("description", ""),
                data.get("category", "General"),
                float(data.get("price", 0.0)),
                int(data.get("quantity", 0)),
                data.get("supplier_id", None),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def list_by_supplier(self, supplier_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT id, sku, name, description, category, price, quantity FROM products WHERE supplier_id = ?",
            (supplier_id,),
        )
        return cursor.fetchall()

    def reduce_stock(self, product_id, quantity):
        cursor = get_db_connection().cursor()
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
