import os.path
from pathlib import Path

import flask
import numpy as np

db_app = flask.Blueprint("db", __name__)

@db_app.get("dummy_values")
def flask_get_dummy_values():
    values: np.ndarray = np.load(os.path.join(Path(__file__).parent, "values.npy"))
    return values.tolist()

@db_app.get("dummy_projected")
def flask_get_dummy_projection():
    values: np.ndarray = np.load(os.path.join(Path(__file__).parent, "projected.npy"))
    return values.tolist()