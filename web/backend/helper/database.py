import datetime
import json
import os

import numpy as np
import pymongo
from bson import json_util
from pymongo.synchronous.database import Database

from algorithms.incdbscan import IncrementalDBSCAN
from web.backend.helper.config import get_config

conf = get_config()


def serialize_mongodb(output):
    temp = json.dumps(output, default=json_util.default)
    return json.loads(temp)


def get_db() -> Database:
    url = conf["mongo"]["url"]
    if os.environ.get('DOCKER', "False") == 'True':
        url = conf["mongo"]["docker_url"]
    conn = pymongo.MongoClient(url)
    db: Database = conn[conf["mongo"]["db"]]
    return db


# ----------------------------------------------
#              Fingerprint Management
# ----------------------------------------------

def store_fingerprint(db: Database, data):
    db["fingerprints"].insert_one(data)


def get_fingerprints(db: Database, dataset: str, subset: str):
    return list(db["fingerprints"].find({"dataset": dataset, "subset": subset}))


def get_fingerprints_for_clustering(db: Database, dataset: str, subset: str):
    fingerprints = list(db["fingerprints"].find({"dataset": dataset, "subset": subset}, {"_id": 1, "label": 1, "feature_descriptors": 1}))
    labels = [f.get("label", -1) for f in fingerprints]
    feature_descriptors = [f["feature_descriptors"]["radii_distribution"]["counts"] for f in fingerprints]
    ids = [f["_id"] for f in fingerprints]
    return labels, feature_descriptors, ids


def cluster_all_fingerprints(db: Database, dataset: str, subset: str):
    parameters = get_parameters(db, dataset, subset)
    _, features, ids = get_fingerprints_for_clustering(db, dataset, subset)
    dbscan = IncrementalDBSCAN(eps=parameters["eps"], min_pts=parameters["minPoints"], metric="jensenshannon")
    dbscan.insert(features)
    labels = dbscan.get_cluster_labels(features)
    for _id, label in zip(ids, labels):
        db["fingerprints"].update_one({"_id": _id}, {"$set": {"label": label}})


def clear_fingerprints(db: Database, dataset: str, subset: str):
    db["fingerprints"].delete_many({"dataset": dataset, "subset": subset})


# ----------------------------------------------
#              Parameter Management
# ----------------------------------------------

def update_parameters(db: Database, dataset: str, subset: str, update_dict: dict):
    existing = db["parameters"].find_one({"dataset": dataset, "subset": subset})
    if existing:
        db["parameters"].update_one({"dataset": dataset, "subset": subset}, {"$set": update_dict})
    else:
        default_params = {**conf["default_parameters"], **update_dict}
        db["parameters"].insert_one({"dataset": dataset, "subset": subset, **default_params})


def get_parameters(db: Database, dataset: str, subset: str):
    existing = db["parameters"].find_one({"dataset": dataset, "subset": subset})
    if not existing:
        return conf["default_parameters"]
    return existing


def get_target_threads(db: Database, dataset: str, subset: str):
    params = get_parameters(db, dataset, subset)
    return params["threads"]


if __name__ == '__main__':
    db = get_db()
    cluster_all_fingerprints(db, "hydro", "x")
