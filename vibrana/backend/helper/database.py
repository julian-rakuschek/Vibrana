import copy
import json
import os
from argparse import ArgumentError
from pathlib import Path

import numpy as np
import pymongo
from bson import json_util
from pymongo.synchronous.database import Database

from vibrana.algorithms.incdbscan import IncrementalDBSCAN
from vibrana.backend.data_loaders.diskLoader import DiskLoader
from vibrana.backend.data_loaders.redisLoader import RedisLoader
from vibrana.backend.helper.config import get_config
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
#              Signal Management
# ----------------------------------------------

def get_loader(loader_type, path, dataset, subset):
    if loader_type == "memory":
        loader = RedisLoader(path, dataset, subset)
        loader.load_numpy_file()
    elif loader_type == "disk":
        loader = DiskLoader(path, dataset, subset)
    else:
        raise Exception("Unknown loader type")
    return loader

def get_length(dataset, subset):
    conf_file = os.path.join(Path(__file__).parents[3], "data", "prepared-signals", dataset, subset, "time.json")
    with open(conf_file) as f:
        f_json = json.load(f)
        return f_json["total_sample_points"]

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
    fingerprints = list(db["fingerprints"].find({"dataset": dataset, "subset": subset}, {"_id": 0, "label": 1, "start_index": 1, "slice_length": 1}))
    fingerprints = sorted(fingerprints, key=lambda x: x["start_index"], reverse=False)
    return fingerprints


def get_fingerprints_for_clustering(db: Database, dataset: str, subset: str, feature_descriptor: str):
    fingerprints = list(db["fingerprints"].find({"dataset": dataset, "subset": subset},
                                                {"_id": 1, "label": 1, "feature_descriptors": 1}))
    labels = [f.get("label", {}).get(feature_descriptor, -1) for f in fingerprints]
    if feature_descriptor == "tde":
        feature_descriptors = [f["feature_descriptors"]["tde"]["counts"] for f in fingerprints]
    elif feature_descriptor == "fft":
        feature_descriptors = [f["feature_descriptors"]["fft"]["magnitudes"] for f in fingerprints]
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
    fft_labels = cluster_all_fingerprints(db, dataset, subset, "fft")
    return {"tde": tde_labels, "fft": fft_labels}


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


# ----------------------------------------------
#              Coverage
# ----------------------------------------------


def get_coverage(db: Database, dataset: str, subset: str):
    fps = get_fingerpints_for_sampling(db, dataset, subset)
    signal_length = get_length(dataset, subset)
    covered_data_points = 0
    if len(fps) == 0:
        return covered_data_points, signal_length
    current_fp = None
    for fp in fps:
        fp['end_index'] = fp['start_index'] + fp['slice_length'] - 1
        if current_fp is None:
            current_fp = copy.deepcopy(fp)
            continue
        if fp["start_index"] <= current_fp["end_index"]:
            current_fp["slice_length"] = fp["end_index"] - current_fp["start_index"] + 1
        else:
            covered_data_points += current_fp["slice_length"]
            current_fp = copy.deepcopy(fp)
    covered_data_points += current_fp["slice_length"]
    return covered_data_points, signal_length



if __name__ == '__main__':
    db = get_db()
    cluster_all_fingerprints(db, "hydro", "x", "fft")
