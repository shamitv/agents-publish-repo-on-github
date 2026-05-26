from src.config.db_sql import get_db_connection
from src.main import create_app


app = create_app()
db_conn = get_db_connection()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085, debug=True)
