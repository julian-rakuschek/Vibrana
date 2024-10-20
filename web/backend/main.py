import os
from pathlib import Path

import flask
from flask_cors import CORS

from web.backend.modules.database import db_app
from web.backend.modules.analysis import analysis_app

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = "hi mum"
cors = CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(db_app, url_prefix="/api/db")
app.register_blueprint(analysis_app, url_prefix="/api/analysis")

@app.route("/")
def index_route():
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "build")
    return flask.send_from_directory(dist_path, 'index.html')

@app.route("/<path:path>")
def static_files(path):
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "build")
    if "." not in path:
        return flask.send_from_directory(dist_path, 'index.html')
    return flask.send_from_directory(dist_path, path)

if __name__ == '__main__':
    app.run(debug=True)
