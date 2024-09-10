import json
import os.path
from pathlib import Path

import flask
import numpy as np
import pymongo
from bson import ObjectId, json_util
from pymongo.database import Database
from sklearn.preprocessing import MinMaxScaler, StandardScaler

db_app = flask.Blueprint("db", __name__)
samples_folder = os.path.join(Path(__file__).parents[3], "data", "samples")

def serialize_mongodb(output):
    temp = json.dumps(output, default=json_util.default)
    return json.loads(temp)

def get_db() -> Database:
    conn = pymongo.MongoClient("mongodb://localhost:27017/")
    db: Database = conn["Vibrana"]
    return db

@db_app.get("machines")
def flask_get_machines_list():
    return ["dummy", "dummy2"]

@db_app.get("<machine>/samples")
def flask_get_samples(machine):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
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
    get_db()["labels"].delete_one({"_id": ObjectId(labelId)})
    return "OK", 200

@db_app.delete("labels/byPosition/<pos>")
def flask_delete_label_by_pos(pos):
    pos = int(pos)
    get_db()["labels"].delete_many({"$and": [{"from": {"$lt": pos}}, {"to": {"$gt": pos}}]})
    return "OK", 200