import flask
import numpy as np

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
        return labels

    db = flask.current_app.config["DB"]
    conf = flask.current_app.config["datasets"][dataset]
    loader = database.get_loader(conf["loader"], path, dataset, subset)
    thread = ComputingThread(db, loader, insert_fingerprint)
    data = thread.process_slice()
    return data

@computing_app.post("<dataset>/<subset>/projection")
@validate_subset
def flask_projection(dataset, subset, path):
    conf = flask.current_app.config["datasets"][dataset]
    loader = database.get_loader(conf["loader"], path, dataset, subset)
    fp = flask.request.get_json()
    if fp is None:
        return flask.jsonify({"error": "Expected fingerprint JSON payload"}), 400

    try:
        start_index = int(fp["start_index"])
        slice_length = int(fp["slice_length"])
        sliding_window_size = int(fp["sliding_window_size"])
        v1 = np.asarray(fp["v1"], dtype=float)
        v2 = np.asarray(fp["v2"], dtype=float)
    except (KeyError, TypeError, ValueError) as exc:
        return flask.jsonify({"error": f"Invalid fingerprint payload: {exc}"}), 400

    projection_length = slice_length - sliding_window_size
    if projection_length <= 0:
        return flask.jsonify([])

    signal = loader.get_slice(
        start_index,
        start_index + slice_length - 1,
        as_numpy=True,
    )
    signal = np.asarray(signal, dtype=float)

    projected = []
    v1_window = v1[:sliding_window_size]
    v2_window = v2[:sliding_window_size]
    for i in range(projection_length):
        window = signal[i:i + sliding_window_size]
        x = float(np.dot(window, v1_window[:len(window)]))
        y = float(np.dot(window, v2_window[:len(window)]))
        projected.append([x, y])

    return flask.jsonify(projected)
