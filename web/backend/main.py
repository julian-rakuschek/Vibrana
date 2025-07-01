import os
from pathlib import Path

import flask

from web.backend.modules.database import db_app
from web.backend.modules.analysis import analysis_app
from web.backend.modules.computing import computing_app

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = "hi mum"

app.register_blueprint(db_app, url_prefix="/api/db")
app.register_blueprint(analysis_app, url_prefix="/api/analysis")
app.register_blueprint(computing_app, url_prefix="/api/computing")

SATIC_FILE_EXTENSIONS = ["js", "css", "html", "png", "jpg", "mp4"]

@app.route("/")
def index_route():
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "build")
    return flask.send_from_directory(dist_path, 'index.html')


@app.route("/<path:path>")
def static_files(path):
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "build")
    if str(path).split(".")[-1] in SATIC_FILE_EXTENSIONS:
        return flask.send_from_directory(dist_path, path)
    return flask.send_from_directory(dist_path, 'index.html')


if __name__ == '__main__':
    app.run(debug=True)
