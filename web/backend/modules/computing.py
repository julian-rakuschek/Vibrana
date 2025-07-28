import json

import flask

from web.backend.data_loaders.redisLoader import RedisLoader
from web.backend.helper.validators import validate_subset
from web.backend.threads.computingThread import ComputingThread
import web.backend.helper.database as database

computing_app = flask.Blueprint("computing", __name__)


@computing_app.get("<dataset>/<subset>/get_target_threads")
@validate_subset
def flask_get_target_threads(dataset, subset, path):
    db = flask.current_app.config["DB"]
    return str(database.get_parameters(db, dataset, subset)["threads"])


@computing_app.post("<dataset>/<subset>/set_target_threads")
@validate_subset
def flask_set_target_threads(dataset, subset, path):
    db = flask.current_app.config["DB"]
    target_threads = json.loads(flask.request.data).get("threads", 0)
    if target_threads < 0:
        return 400, "Threads must be >= 0"
    elif target_threads > 10:
        return 400, "Don't fry your computer please"
    database.update_parameters(db, dataset, subset, {"threads": target_threads})
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
