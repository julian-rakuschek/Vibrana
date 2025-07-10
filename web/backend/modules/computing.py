import json

import flask

from web.backend.data_loaders.redisLoader import RedisLoader
from web.backend.helper.validators import validate_subset
from web.backend.threads.computingThread import ComputingThread

computing_app = flask.Blueprint("computing", __name__)


@computing_app.get("<dataset>/<subset>/get_target_threads")
@validate_subset
def flask_get_target_threads(dataset, subset, path):
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    return str(loader.get_target_threads())


@computing_app.post("<dataset>/<subset>/set_target_threads")
@validate_subset
def flask_set_target_threads(dataset, subset, path):
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    target_threads = json.loads(flask.request.data).get("threads", 0)
    if target_threads < 0:
        return 400, "Threads must be >= 0"
    elif target_threads > 10:
        return 400, "Don't fry your computer please"
    loader.set_target_threads(target_threads)
    return {"success": True}


@computing_app.post("<dataset>/<subset>/single_step")
@validate_subset
def flask_make_single_step(dataset, subset, path):
    sliding_window_size = int(flask.request.args.get("sliding_window_size", 1000))
    slice_size = int(flask.request.args.get("slice_size", 10_000))
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    loader.load_numpy_file(False)
    thread = ComputingThread(loader.r, loader, sliding_window_size, slice_size)
    data = thread.compute_plane()
    return data
