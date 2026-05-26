from src.config.db_sql import get_db_connection


class OrderRepository:
    def list_for_user(self, user_id, username):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT id, order_number, total_amount, status, created_at, ? as username FROM orders WHERE user_id = ?",
            (username, user_id),
        )
        return cursor.fetchall()

    def list_all(self):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT o.id, o.order_number, o.total_amount, o.status, o.created_at, u.username "
            "FROM orders o JOIN users u ON o.user_id = u.id"
        )
        return cursor.fetchall()

    def find_by_id_with_user(self, order_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT o.id, o.order_number, o.total_amount, o.status, o.created_at, u.username "
            "FROM orders o JOIN users u ON o.user_id = u.id WHERE o.id = ?",
            (order_id,),
        )
        return cursor.fetchone()

    def find_items(self, order_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT oi.quantity, oi.price, p.name, p.sku FROM order_items oi "
            "JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
            (order_id,),
        )
        return cursor.fetchall()

    def create_order(self, user_id, order_number, total):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id, order_number, total_amount, status) VALUES (?, ?, ?, 'PROCESSING')",
            (user_id, order_number, total),
        )
        return cursor.lastrowid

    def add_item(self, order_id, product_id, quantity, price):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, price),
        )

    def commit(self):
        get_db_connection().commit()

    def rollback(self):
        get_db_connection().rollback()
