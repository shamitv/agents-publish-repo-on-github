import sys
from pathlib import Path

# Ensure monorepo packages and src are importable
_APP_ROOT = Path(__file__).resolve().parent
_PACKAGES = _APP_ROOT.parents[1] / "packages"
sys.path.insert(0, str(_PACKAGES))
sys.path.insert(0, str(_APP_ROOT))

from src.main import create_app
from src.config.db_sql import get_db_connection


app = create_app()
db_conn = get_db_connection()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)