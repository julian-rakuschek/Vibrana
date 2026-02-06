import json

import flask

from vibrana.backend.data_loaders.redisLoader import RedisLoader
from vibrana.backend.helper.validators import validate_subset
import vibrana.backend.helper.database as database

db_app = flask.Blueprint("db", __name__)


@db_app.get("<dataset>/<subset>/slice")
@validate_subset
def flask_get_slice(dataset, subset, path):
    start_index = flask.request.args.get("start_index", 0)
    end_index = flask.request.args.get("end_index", -1)

    loader = RedisLoader(path, dataset, subset)
    loader.load_numpy_file()
    return loader.get_slice(start_index, end_index, as_numpy=False)


@db_app.get("<dataset>/<subset>/timestamps")
@validate_subset
def flask_get_timestamps(dataset, subset, path):
    start_index = int(flask.request.args.get("start_index", 0))
    end_index = int(flask.request.args.get("end_index", -1))
    amount = int(flask.request.args.get("amount", 1000))

    loader = RedisLoader(path, dataset, subset)
    loader.load_numpy_file()
    return loader.get_timestamp_subsample(start_index, end_index, as_numpy=False, amount=amount)


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