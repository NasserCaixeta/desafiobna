import os
import sys

# Caminho absoluto da pasta backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app

config_name = os.getenv("FLASK_CONFIG", "default")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(debug=True)
