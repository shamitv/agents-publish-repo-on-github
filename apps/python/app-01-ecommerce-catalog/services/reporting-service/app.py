import sys
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parent
_PACKAGES = _APP_ROOT.parents[1] / "packages"
sys.path.insert(0, str(_PACKAGES))
sys.path.insert(0, str(_APP_ROOT))

from src.main import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
