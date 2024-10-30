import json
import os.path
from pathlib import Path

import flask
import redis

import web.backend.helper.file_processor as parser
from web.backend.settings import chunks_folder, data_folder, READ_ONLY

upload_app = flask.Blueprint("upload", __name__)
r = redis.Redis(host='vibrana_redis' if os.environ.get('DOCKER', "False") == 'True' else 'localhost', port=6379, db=1)

ALLOWED_EXTENSIONS = {'dxd'}


@upload_app.post("datasets/add")
def flask_add_dataset():
    return "Adding a dataset is for now disabled due to implementation changes", 401
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    dataset_name = json.loads(flask.request.data.decode()).get("datasetName", None)
    if dataset_name is None:
        return {"success": False}
    Path(os.path.join(chunks_folder, dataset_name)).mkdir(parents=True, exist_ok=True)
    return {"success": True}


@upload_app.post("<dataset>/upload")
def flask_upload(dataset):
    return "Uploading a dataset is for now disabled due to implementation changes", 401

    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Get and validate the prefix
    prefix = flask.request.form["prefix"]
    if not isinstance(prefix, str):
        return "Invalid input: prefix must be a string.", 400
    if prefix == "":
        prefix = "signal"

    # Get and validate the maxchunksize
    max_sample_size_str = flask.request.form.get("maxchunksize", "100000")
    try:
        maxchunksize = int(max_sample_size_str)
    except ValueError:
        return "Invalid input: maxchunksize must be an integer.", 400

    # Get and validate the maxchunksize
    proj_window_size_str = flask.request.form.get("projectionWindowSize", "2000")
    try:
        projectionWindowSize = int(proj_window_size_str)
    except ValueError:
        return "Invalid input: projectionWindowSize must be an integer.", 400

    # Get and validate the maxchunksize
    cutoff_str = flask.request.form.get("cutoffRatio", "0")
    try:
        cutoff_ratio = float(cutoff_str)
        if not 0 <= cutoff_ratio < 0.5:
            raise ValueError
    except ValueError:
        return "Invalid input: cutoffRatio must be a float between 0 and 0.5.", 400

    # Get and validate the saveParsed
    save_parsed_str = flask.request.form.get("saveParsed", "").lower()
    if save_parsed_str == "true":
        saveParsed = True
    elif save_parsed_str == "false":
        saveParsed = False
    else:
        return "Invalid input: saveParsed must be a boolean (true/false).", 400

    print(prefix, maxchunksize, saveParsed, cutoff_ratio, projectionWindowSize)

    if 'file' not in flask.request.files:
        return "No file found in request", 400
    file = flask.request.files['file']
    if not file:
        return "File upload failed", 400
    if file.filename == "":
        return "Filename must not be empty", 400
    if not allowed_file(file.filename):
        return "This file extension is not allowed", 400
    # filename = secure_filename(file.filename)
    filename = file.filename
    Path(os.path.join(data_folder, "raw")).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(data_folder, "raw", filename)
    with open(filepath, "wb") as f:
        f.write(file.read())
    parser.parse_file(dataset, filename, prefix, maxchunksize, saveParsed, cutoff_ratio, projectionWindowSize, r)
    return "OK", 200


@upload_app.get("<dataset>/<filename>/upload/status")
def flask_get_upload_status(dataset, filename):
    r_key = f"vibrana:{dataset}:{filename}"
    res = r.get(r_key)
    if res is not None:
        return json.loads(res)
    return {}