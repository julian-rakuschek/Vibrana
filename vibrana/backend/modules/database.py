import json
import os
from pathlib import Path

import flask

from vibrana.backend.data_loaders.diskLoader import DiskLoader
from vibrana.backend.data_loaders.redisLoader import RedisLoader
from vibrana.backend.helper.validators import validate_subset
import vibrana.backend.helper.database as database

db_app = flask.Blueprint("db", __name__)


@db_app.get("<dataset>/<subset>/slice")
@validate_subset
def flask_get_slice(dataset, subset, path):
    start_index = flask.request.args.get("start_index", 0)
    end_index = flask.request.args.get("end_index", -1)
    conf = flask.current_app.config["datasets"][dataset]
    loader = database.get_loader(conf["loader"], path, dataset, subset)
    return loader.get_slice(start_index, end_index, as_numpy=False)


@db_app.get("<dataset>/<subset>/time")
@validate_subset
def flask_get_time(dataset, subset, path):
    time_file = os.path.join(Path(path).parents[0], "time.json")
    with open(time_file, "r") as f:
        time = json.load(f)
    return time


@db_app.get("<dataset>/<subset>/fingerprints")
@validate_subset
def flask_get_fingerprints(dataset, subset, path):
    db = flask.current_app.config["DB"]
    return database.serialize_mongodb(database.get_fingerprints(db, dataset, subset))


@db_app.post("<dataset>/<subset>/clear")
@validate_subset
def flask_clear_dataset(dataset, subset, path):
    db = flask.current_app.config["DB"]
    database.clear_fingerprints(db, dataset, subset)
    return "OK", 200


@db_app.post("<dataset>/<subset>/parameters")
@validate_subset
def flask_clear_store_parameters(dataset, subset, path):
    db = flask.current_app.config["DB"]
    parameters = json.loads(flask.request.data)
    database.update_parameters(db, dataset, subset, parameters)
    return "OK", 200


@db_app.get("<dataset>/<subset>/parameters")
@validate_subset
def flask_clear_get_parameters(dataset, subset, path):
    db = flask.current_app.config["DB"]
    return database.serialize_mongodb(database.get_parameters(db, dataset, subset))


@db_app.post("<dataset>/<subset>/intervals")
@validate_subset
def flask_clear_store_intervals(dataset, subset, path):
    db = flask.current_app.config["DB"]
    intervals = json.loads(flask.request.data)
    current_params = database.get_parameters(db, dataset, subset)
    current_params["sampling"]["intervals"] = intervals
    database.update_parameters(db, dataset, subset, current_params)
    return "OK", 200


@db_app.get("<dataset>/<subset>/intervals")
@validate_subset
def flask_clear_get_intervals(dataset, subset, path):
    db = flask.current_app.config["DB"]
    current_params = database.get_parameters(db, dataset, subset)
    intervals = current_params.get("sampling", {}).get("intervals", [])
    return database.serialize_mongodb(intervals)

@db_app.get("<dataset>/<subset>/coverage")
@validate_subset
def flask_get_coverage(dataset, subset, path):
    db = flask.current_app.config["DB"]
    coverage = database.get_coverage(db, dataset, subset)
    ratio = coverage[1] / coverage[0]
    return flask.jsonify(ratio)