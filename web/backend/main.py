import os
from pathlib import Path

import flask
from flask_cors import CORS

from modules.database import db_app

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = "hi mum"
cors = CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(db_app, url_prefix="/api/db")

@app.route("/")
@app.route("/<path:path>")
def flask_main(path=None):
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "dist")
    if path is not None and os.path.exists(os.path.join(dist_path, path)):
        dist_path = os.path.join(dist_path, path)
        return flask.send_file(dist_path)
    return flask.send_from_directory(dist_path, "index.html")


if __name__ == '__main__':
    app.run(debug=True)
