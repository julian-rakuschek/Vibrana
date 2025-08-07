import json
import os
from pathlib import Path

import flask
from flask_socketio import SocketIO, join_room, send, leave_room

from web.backend.helper.config import crawl_dataset_folder
from web.backend.modules.database import db_app
from web.backend.modules.analysis import analysis_app
from web.backend.modules.computing import computing_app
import helper.database as database

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = "hi mum"
app.config['DB'] = database.get_db()

app.register_blueprint(db_app, url_prefix="/api/db")
app.register_blueprint(analysis_app, url_prefix="/api/analysis")
app.register_blueprint(computing_app, url_prefix="/api/computing")
socketio = SocketIO(app, cors_allowed_origins="*")

SATIC_FILE_EXTENSIONS = ["js", "css", "html", "png", "jpg", "mp4"]


@app.route("/")
def index_route():
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "build")
    return flask.send_from_directory(dist_path, 'index.html')


@app.route("/api/config")
def flask_get_config():
    return crawl_dataset_folder()


@app.route("/<path:path>")
def static_files(path):
    dist_path = os.path.join(Path(__file__).parents[1], "frontend", "build")
    if str(path).split(".")[-1] in SATIC_FILE_EXTENSIONS:
        return flask.send_from_directory(dist_path, path)
    return flask.send_from_directory(dist_path, 'index.html')


@socketio.on('join')
def on_join(data):
    join_room(data['room'])


@socketio.on('leave')
def on_leave(data):
    leave_room(data['room'])


@socketio.on('share_computation_result')
def handle_share_computation_result(data):
    send(data, to=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
