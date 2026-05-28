from src.config.db_sql import get_db_cursor


class UserRepository:
    def find_by_credentials(self, username, password):
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password))
            return cur.fetchone()

    def find_by_id(self, user_id):
        with get_db_cursor() as cur:
            cur.execute("SELECT id, username, role, email FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()
