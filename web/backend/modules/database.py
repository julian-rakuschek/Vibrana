import json

import flask

from web.backend.data_loaders.redisLoader import RedisLoader
from web.backend.helper.validators import validate_subset

db_app = flask.Blueprint("db", __name__)


@db_app.get("<dataset>/<subset>/slice")
@validate_subset
def flask_get_slice(dataset, subset, path):
    start_index = flask.request.args.get("start_index", 0)
    end_index = flask.request.args.get("end_index", -1)

    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    loader.load_numpy_file()
    return loader.get_slice(start_index, end_index, as_numpy=False)


@db_app.get("<dataset>/<subset>/vectors")
@validate_subset
def flask_get_vectors(dataset, subset, path):
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    loader.load_numpy_file()
    return loader.retrieve_hyperplane_vectors(exclude_vector_data=False)

@db_app.get("<dataset>/<subset>/vector")
@validate_subset
def flask_get_vector(dataset, subset, path):
    start_index = flask.request.args.get("start_index", None)
    slice_size = flask.request.args.get("slice_size", None)
    if slice_size is None or start_index is None:
        return "Slice size and start index must both be defined", 400

    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    loader.load_numpy_file()
    return loader.retrieve_hyperplane_vectors(int(start_index), int(slice_size))


@db_app.post("<dataset>/<subset>/clear")
@validate_subset
def flask_clear_dataset(dataset, subset, path):
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    loader.clear(only_vectors=True)
    return "OK", 200


@db_app.post("<dataset>/<subset>/weights")
@validate_subset
def flask_clear_store_weights(dataset, subset, path):
    weights = json.loads(flask.request.data)
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    loader.store_weights(weights)
    return "OK", 200


@db_app.get("<dataset>/<subset>/weights")
@validate_subset
def flask_clear_get_weights(dataset, subset, path):
    loader = RedisLoader(path, f"vibrana:{dataset}:{subset}")
    return loader.get_weights()
