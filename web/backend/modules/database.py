import json
import os.path
from pathlib import Path

import flask
import redis
import numpy as np
import pymongo
from bson import ObjectId, json_util
from pymongo.database import Database
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from werkzeug.utils import secure_filename
import web.backend.helper.file_processor as parser
from web.backend.settings import samples_folder, data_folder, READ_ONLY

db_app = flask.Blueprint("db", __name__)
r = redis.Redis(host="localhost", port=6379, db=1)

ALLOWED_EXTENSIONS = {'dxd'}


def serialize_mongodb(output):
    temp = json.dumps(output, default=json_util.default)
    return json.loads(temp)


def get_db() -> Database:
    conn = pymongo.MongoClient("mongodb://localhost:27017/")
    db: Database = conn["Vibrana"]
    return db


@db_app.get("is_read_only")
def flask_get_ro_status():
    return flask.jsonify(READ_ONLY)


@db_app.get("machines")
def flask_get_machines_list():
    return os.listdir(samples_folder)


@db_app.post("machines/add")
def flask_add_machine():
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    machine_name = json.loads(flask.request.data.decode()).get("machineName", None)
    if machine_name is None:
        return {"success": False}
    Path(os.path.join(samples_folder, machine_name)).mkdir(parents=True, exist_ok=True)
    return {"success": True}


@db_app.post("<machine>/upload")
def flask_upload(machine):
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

    # Get and validate the maxSampleSize
    max_sample_size_str = flask.request.form.get("maxSampleSize", "100000")
    try:
        maxSampleSize = int(max_sample_size_str)
    except ValueError:
        return "Invalid input: maxSampleSize must be an integer.", 400

    # Get and validate the maxSampleSize
    proj_window_size_str = flask.request.form.get("projectionWindowSize", "2000")
    try:
        projectionWindowSize = int(proj_window_size_str)
    except ValueError:
        return "Invalid input: projectionWindowSize must be an integer.", 400

    # Get and validate the maxSampleSize
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

    print(prefix, maxSampleSize, saveParsed, cutoff_ratio, projectionWindowSize)

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
    parser.parse_file(machine, filename, prefix, maxSampleSize, saveParsed, cutoff_ratio, projectionWindowSize, r)
    return "OK", 200


@db_app.get("<machine>/<filename>/upload/status")
def flask_get_upload_status(machine, filename):
    r_key = f"vibrana:{machine}:{filename}"
    res = r.get(r_key)
    if res is not None:
        return json.loads(res)
    return {}


@db_app.get("<machine>/samples")
def flask_get_samples(machine):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return []
    return os.listdir(os.path.join(samples_folder, machine))


@db_app.get("<machine>/samples/<sampleId>/values")
def flask_get_values(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    return values.tolist()


@db_app.get("<machine>/samples/<sampleId>/projected")
def flask_get_projection(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "projected.npy"))
    values = MinMaxScaler().fit_transform(values)
    values = StandardScaler(with_std=False).fit_transform(values)
    return values.tolist()


@db_app.get("<machine>/samples/<sampleId>/freq")
def flask_get_freq(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "freq.npy"))
    values = np.array(values).reshape(-1, 1)
    values = MinMaxScaler().fit_transform(values)
    return values.flatten().tolist()


@db_app.get("<machine>/samples/<sampleId>/thumbnail")
def flask_get_sample_thumb(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    return flask.send_file(os.path.join(sample_path, "preview.png"), mimetype='image/png')


@db_app.get("<machine>/samples/<sampleId>/events")
def flask_get_sample_events(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    if not os.path.exists(os.path.join(sample_path, "events.npy")):
        print(os.path.join(sample_path, "events.npy"), "does not exist")
        return []
    values: np.ndarray = np.load(os.path.join(sample_path, "events.npy"))
    return values.tolist()


@db_app.get("labels/<machine>/<sampleId>")
def flask_get_labels(machine, sampleId):
    res = list(get_db()["labels"].find({"machine": machine, "sampleId": sampleId}))
    return serialize_mongodb(res)


@db_app.post("labels")
def flask_add_label():
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    data = flask.request.get_json()
    db = get_db()["labels"]
    print(data)
    res = list(db.find({
        "machine": data["machine"],
        "sampleId": data["sampleId"],
        "$or": [
            {"$and": [
                {"from": {"$gt": data["from"]}},
                {"from": {"$lt": data["to"]}},
            ]},
            {"$and": [
                {"to": {"$gt": data["from"]}},
                {"to": {"$lt": data["to"]}},
            ]}
        ],
    }))
    for item in res:
        db.delete_one({"_id": item["_id"]})

    data["from"] = min([*res, data], key=lambda x: x['from'])["from"]
    data["to"] = max([*res, data], key=lambda x: x['to'])["to"]
    print(data)
    db.insert_one(data)
    return "OK", 200


@db_app.delete("labels/byId/<labelId>")
def flask_delete_label(labelId):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    get_db()["labels"].delete_one({"_id": ObjectId(labelId)})
    return "OK", 200


@db_app.delete("labels/<machine>/<sampleId>/byPosition/<pos>")
def flask_delete_label_by_pos(machine, sampleId, pos):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    pos = int(pos)
    get_db()["labels"].delete_many({"$and": [{"from": {"$lt": pos}}, {"to": {"$gt": pos}}], "machine": machine, "sampleId": sampleId})
    return "OK", 200


@db_app.get("normals/<machine>")
def flask_get_normals(machine):
    machine_samples = get_db()["normals"].find_one({"machine": machine})
    if not machine_samples:
        return []
    return machine_samples.get("samples", [])


@db_app.post("normals/<machine>/<sampleId>")
def flask_add_normal(machine, sampleId):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    db = get_db()["normals"]
    machine_samples = db.find_one({"machine": machine})
    if not machine_samples:
        db.insert_one({"machine": machine, "samples": [sampleId]})
        return {"success": True}
    db.update_one({"machine": machine}, {"$addToSet": {"samples": sampleId}})
    return {"success": True}


@db_app.delete("normals/<machine>/<sampleId>")
def flask_delete_normal(machine, sampleId):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    db = get_db()["normals"]
    machine_samples = db.find_one({"machine": machine})
    if not machine_samples:
        return {"success": True}
    db.update_one({"machine": machine}, {"$pull": {"samples": sampleId}})
    return {"success": True}


@db_app.post("reset/<machine>")
def flask_reset(machine):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    db = get_db()
    db["labels"].delete_many({"machine": machine})
    db["normals"].delete_many({"machine": machine})
    return {"success": True}
