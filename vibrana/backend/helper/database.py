import json
import os
from argparse import ArgumentError

import numpy as np
import pymongo
from bson import json_util
from pymongo.synchronous.database import Database

from vibrana.algorithms.incdbscan import IncrementalDBSCAN
from vibrana.backend.helper.config import get_config
from vibrana.backend.helper.fluctuationCompute import get_coverage, get_breakpoints
from vibrana.backend.helper.util import flatten_dict, deep_update

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

def store_fingerprint(db: Database, data, dataset, subset):
    db["fingerprints"].insert_one(data)


def get_fingerprints(db: Database, dataset: str, subset: str):
    return list(db["fingerprints"].find({"dataset": dataset, "subset": subset}))


def clear_fingerprints(db: Database, dataset: str, subset: str):
    db["fingerprints"].delete_many({"dataset": dataset, "subset": subset})
    db["provenance"].delete_many({"dataset": dataset, "subset": subset})


# ----------------------------------------------
#              Cluster Management
# ----------------------------------------------

def get_fingerpints_for_sampling(db: Database, dataset: str, subset: str):
    fingerprints = list(db["fingerprints"].find({"dataset": dataset, "subset": subset}, {"_id": 0, "label": 1, "start_index": 1}))
    fingerprints = sorted(fingerprints, key=lambda x: x["start_index"], reverse=False)
    return fingerprints


def get_fingerprints_for_clustering(db: Database, dataset: str, subset: str, feature_descriptor: str):
    fingerprints = list(db["fingerprints"].find({"dataset": dataset, "subset": subset},
                                                {"_id": 1, "label": 1, "feature_descriptors": 1}))
    labels = [f.get("label", {}).get(feature_descriptor, -1) for f in fingerprints]
    if feature_descriptor == "tde":
        feature_descriptors = [f["feature_descriptors"]["tde"]["counts"] for f in fingerprints]
    elif feature_descriptor == "psd":
        feature_descriptors = [f["feature_descriptors"]["psd"]["Pxx_spec"] for f in fingerprints]
    else:
        raise ValueError("unknown feature descriptor")
    ids = [f["_id"] for f in fingerprints]
    return labels, feature_descriptors, ids


def cluster_all_fingerprints(db: Database, dataset: str, subset: str, feature_descriptor: str):
    parameters = get_parameters(db, dataset, subset)[feature_descriptor]
    _, features, ids = get_fingerprints_for_clustering(db, dataset, subset, feature_descriptor)
    dbscan = IncrementalDBSCAN(eps=parameters["eps"], min_pts=parameters["minPoints"], metric="jensenshannon")
    dbscan.insert(features)
    labels = dbscan.get_cluster_labels(features).tolist()
    for _id, label in zip(ids, labels):
        db["fingerprints"].update_one({"_id": _id}, {"$set": {f"label.{feature_descriptor}": label}})
    return labels


def cluster_all_fingerprints_all_feature_descriptors(db: Database, dataset: str, subset: str):
    tde_labels = cluster_all_fingerprints(db, dataset, subset, "tde")
    psd_labels = cluster_all_fingerprints(db, dataset, subset, "psd")
    return {"tde": tde_labels, "psd": psd_labels}


# ----------------------------------------------
#              Parameter Management
# ----------------------------------------------

def update_parameters(db: Database, dataset: str, subset: str, update_dict: dict):
    existing = db["parameters"].find_one({"dataset": dataset, "subset": subset})
    if existing:
        db["parameters"].update_one({"dataset": dataset, "subset": subset}, {"$set": flatten_dict(update_dict)})
    else:
        default_parameters = get_config()["default_parameters"]
        deep_update(default_parameters, update_dict)
        db["parameters"].insert_one({"dataset": dataset, "subset": subset, **default_parameters})


def get_parameters(db: Database, dataset: str, subset: str):
    existing = db["parameters"].find_one({"dataset": dataset, "subset": subset})
    if not existing:
        return conf["default_parameters"]
    return existing


def get_running(db: Database, dataset: str, subset: str):
    params = get_parameters(db, dataset, subset)
    return params.get("sampling", {}).get("running", False)


if __name__ == '__main__':
    db = get_db()
    cluster_all_fingerprints(db, "hydro", "x", "psd")
