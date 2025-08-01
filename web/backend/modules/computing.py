import json

import flask

from web.backend.data_loaders.redisLoader import RedisLoader
from web.backend.helper.validators import validate_subset
from web.backend.threads.computingThread import ComputingThread
import web.backend.helper.database as database

computing_app = flask.Blueprint("computing", __name__)


@computing_app.get("<dataset>/<subset>/status")
@validate_subset
def flask_get_computing_status(dataset, subset, path):
    db = flask.current_app.config["DB"]
    status = database.get_parameters(db, dataset, subset).get("running", False)
    return flask.jsonify(status)


@computing_app.post("<dataset>/<subset>/activate")
@validate_subset
def flask_activate_computation(dataset, subset, path):
    db = flask.current_app.config["DB"]
    database.update_parameters(db, dataset, subset, {"running": True})
    return {"success": True}


@computing_app.post("<dataset>/<subset>/pause")
@validate_subset
def flask_pause_computation(dataset, subset, path):
    db = flask.current_app.config["DB"]
    database.update_parameters(db, dataset, subset, {"running": False})
    return {"success": True}


@computing_app.post("<dataset>/<subset>/single_step")
@validate_subset
def flask_make_single_step(dataset, subset, path):
    db = flask.current_app.config["DB"]
    sliding_window_size = int(flask.request.args.get("sliding_window_size", 1000))
    slice_size = int(flask.request.args.get("slice_size", 10_000))
    loader = RedisLoader(path, dataset, subset)
    loader.load_numpy_file(False)
    insert_func = lambda dataset, subset, data: database.store_fingerprint(db, data, dataset, subset)
    thread = ComputingThread(db, loader.r, loader, sliding_window_size, slice_size, insert_func)
    data = thread.compute_plane()
    return data
