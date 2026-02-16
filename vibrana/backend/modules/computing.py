import json

import flask

from vibrana.backend.data_loaders.redisLoader import RedisLoader
from vibrana.backend.helper.validators import validate_subset
from vibrana.backend.threads.computingThread import ComputingThread
import vibrana.backend.helper.database as database

computing_app = flask.Blueprint("computing", __name__)


@computing_app.get("<dataset>/<subset>/status")
@validate_subset
def flask_get_computing_status(dataset, subset, path):
    db = flask.current_app.config["DB"]
    status = database.get_running(db, dataset, subset)
    return flask.jsonify(status)


@computing_app.post("<dataset>/<subset>/activate")
@validate_subset
def flask_activate_computation(dataset, subset, path):
    db = flask.current_app.config["DB"]
    database.update_parameters(db, dataset, subset, {"sampling.running": True})
    return {"success": True}


@computing_app.post("<dataset>/<subset>/pause")
@validate_subset
def flask_pause_computation(dataset, subset, path):
    db = flask.current_app.config["DB"]
    database.update_parameters(db, dataset, subset, {"sampling.running": False})
    return {"success": True}


@computing_app.post("<dataset>/<subset>/single_step")
@validate_subset
def flask_make_single_step(dataset, subset, path):
    def insert_fingerprint(dataset, subset, data):
        database.store_fingerprint(db, data, dataset, subset)
        labels = database.cluster_all_fingerprints_all_feature_descriptors(db, dataset, subset)
        database.add_provenance_record(db, dataset, subset)
        return labels

    db = flask.current_app.config["DB"]
    loader = RedisLoader(path, dataset, subset)
    loader.load_numpy_file(False)
    thread = ComputingThread(db, loader.r, loader, insert_fingerprint)
    data = thread.process_slice()
    return data
