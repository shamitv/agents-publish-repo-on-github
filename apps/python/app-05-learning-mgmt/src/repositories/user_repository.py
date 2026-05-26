from src.config.db_sql import get_db_connection


class UserRepository:
    def find_by_credentials(self, username, password):
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password))
        return cursor.fetchone()

    def find_by_id(self, user_id):
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT id, username, role, email FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
