import json
import os.path
from pathlib import Path

import flask
import numpy as np
import pymongo
from bson import ObjectId, json_util
from pymongo.database import Database
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from web.backend.helper.wrapper import validate_subset, validate_chunk_path
from web.backend.settings import chunks_folder, READ_ONLY

db_app = flask.Blueprint("db", __name__)


def serialize_mongodb(output):
    temp = json.dumps(output, default=json_util.default)
    return json.loads(temp)


def get_db() -> Database:
    mongo_url = f"mongodb://{'vibrana_mongodb' if os.environ.get('DOCKER', "False") == 'True' else 'localhost'}:27017/"
    conn = pymongo.MongoClient(mongo_url)
    db: Database = conn["Vibrana"]
    return db


@db_app.get("is_read_only")
def flask_get_ro_status():
    return flask.jsonify(READ_ONLY)


@db_app.get("datasets")
def flask_get_datasets_list():
    with open(str(os.path.join(Path(__file__).parents[1], "datasets.json")), "r", encoding="utf-8") as f:
        return json.load(f)


@db_app.get("<dataset>/<subset>/chunks")
@validate_subset
def flask_get_chunks(dataset, subset, subset_path):
    if not os.path.exists(subset_path):
        return []
    return os.listdir(subset_path)


@db_app.get("<dataset>/<subset>/<chunk>/values")
@validate_chunk_path
def flask_get_values(dataset, subset, chunk, chunk_path):
    values: np.ndarray = np.load(os.path.join(chunk_path, "values.npy"))
    return values.tolist()


@db_app.get("<dataset>/<subset>/<chunk>/projected")
@validate_chunk_path
def flask_get_projection(dataset, subset, chunk, chunk_path):
    values: np.ndarray = np.load(os.path.join(chunk_path, "projected.npy"))
    values = MinMaxScaler().fit_transform(values)
    values = StandardScaler(with_std=False).fit_transform(values)
    return values.tolist()


@db_app.get("<dataset>/<subset>/<chunk>/freq")
@validate_chunk_path
def flask_get_freq(dataset, subset, chunk, chunk_path):
    if not os.path.exists(os.path.join(chunk_path, "freq.npy")):
        return []
    values: np.ndarray = np.load(os.path.join(chunk_path, "freq.npy"))
    values = np.array(values).reshape(-1, 1)
    values = MinMaxScaler().fit_transform(values)
    return values.flatten().tolist()


@db_app.get("<dataset>/<subset>/<chunk>/thumbnail")
@validate_chunk_path
def flask_get_sample_thumb(dataset, subset, chunk, chunk_path):
    if not os.path.exists(os.path.join(chunk_path, "preview.png")):
        return "Preview not available", 404
    return flask.send_file(os.path.join(chunk_path, "preview.png"), mimetype='image/png')


@db_app.get("<dataset>/<subset>/<chunk>/projected_thumbnail")
@validate_chunk_path
def flask_get_sample_thumb_projected(dataset, subset, chunk, chunk_path):
    if not os.path.exists(os.path.join(chunk_path, "preview_projected.png")):
        return "Projected Thumbnail not available", 404
    return flask.send_file(os.path.join(chunk_path, "preview_projected.png"), mimetype='image/png')


@db_app.get("<dataset>/<subset>/<chunk>/spectrogram")
@validate_chunk_path
def flask_get_sample_thumb_spectro(dataset, subset, chunk, chunk_path):
    if not os.path.exists(os.path.join(chunk_path, "spectro.png")):
        return "Spectrogram not available", 404
    return flask.send_file(os.path.join(chunk_path, "spectro.png"), mimetype='image/png')


@db_app.get("<dataset>/<subset>/<chunk>/events")
@validate_chunk_path
def flask_get_sample_events(dataset, subset, chunk, chunk_path):
    if not os.path.exists(os.path.join(chunk_path, "events.npy")):
        return []
    values: np.ndarray = np.load(os.path.join(chunk_path, "events.npy"))
    return values.tolist()


@db_app.get("<dataset>/<subset>/<chunk>/labels")
def flask_get_labels(dataset, subset, chunk):
    res = list(get_db()["labels"].find({"dataset": dataset, "subset": subset, "chunk": chunk}))
    return serialize_mongodb(res)

@db_app.get("<dataset>/<subset>/labels/count")
def flask_get_labels_count(dataset, subset):
    pipeline = [
        {"$match": {"dataset": dataset, "subset": subset}},
        {"$group": {"_id": "$chunk", "count": {"$sum": 1}}}
    ]
    res = list(get_db()["labels"].aggregate(pipeline))
    return serialize_mongodb(res)



@db_app.post("labels")
def flask_add_label():
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    data = flask.request.get_json()
    db = get_db()["labels"]
    res = list(db.find({
        "dataset": data["dataset"],
        "subset": data["subset"],
        "chunk": data["chunk"],
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
    db.insert_one(data)
    return "OK", 200


@db_app.delete("labels/byId/<labelId>")
def flask_delete_label(labelId):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    get_db()["labels"].delete_one({"_id": ObjectId(labelId)})
    return "OK", 200


@db_app.delete("<dataset>/<subset>/<chunk>/labels/<pos>")
def flask_delete_label_by_pos(dataset, subset, chunk, pos):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    pos = int(pos)
    get_db()["labels"].delete_many({"$and": [{"from": {"$lt": pos}}, {"to": {"$gt": pos}}], "dataset": dataset, "subset": subset, "chunk": chunk})
    return "OK", 200


@db_app.get("<dataset>/<subset>/normals")
def flask_get_normals(dataset, subset):
    dataset_chunks = get_db()["normals"].find_one({"dataset": dataset, "subset": subset})
    if not dataset_chunks:
        return []
    return dataset_chunks.get("chunks", [])


@db_app.post("<dataset>/<subset>/<chunk>/normals")
def flask_add_normal(dataset, subset, chunk):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    db = get_db()["normals"]
    dataset_chunks = db.find_one({"dataset": dataset, "subset": subset})
    if not dataset_chunks:
        db.insert_one({"dataset": dataset, "subset": subset, "chunks": [chunk]})
        return {"success": True}
    existing_chunks = dataset_chunks.get("chunks", [])
    if chunk in existing_chunks:
        db.update_one({"dataset": dataset, "subset": subset}, {"$pull": {"chunks": chunk}})
    else:
        db.update_one({"dataset": dataset, "subset": subset}, {"$addToSet": {"chunks": chunk}})
    return {"success": True}


@db_app.post("<dataset>/<subset>/reset")
def flask_reset(dataset, subset):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    db = get_db()
    db["labels"].delete_many({"dataset": dataset, "subset": subset})
    db["normals"].delete_many({"dataset": dataset, "subset": subset})
    return {"success": True}


@db_app.post("<dataset>/<subset>/<chunk>/reset")
def flask_reset_chunk(dataset, subset, chunk):
    if READ_ONLY:
        return "The system is in read-only mode, changes are not allowed", 401
    db = get_db()
    db["labels"].delete_many({"dataset": dataset, "subset": subset, "chunk": chunk})
    return {"success": True}
