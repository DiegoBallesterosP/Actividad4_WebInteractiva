"""Run locally with `python app.py`; in production gunicorn serves `app:server`."""

import os

from mortality import create_app

app = create_app()
server = app.server

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 8050)))
