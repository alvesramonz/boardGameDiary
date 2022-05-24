from werkzeug.local import LocalProxy
from app import create_app

from settings.db import get_db

db = LocalProxy(get_db)

if __name__ == "__main__":
    app = create_app()

    app.run(port=8085)