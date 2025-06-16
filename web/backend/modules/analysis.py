import io
import json
import os.path
from pathlib import Path

import flask
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from web.backend.helper.clustering import *
from web.backend.helper.validators import validate_chunk_path, validate_subset
from web.backend.modules.database import get_db

analysis_app = flask.Blueprint("analysis", __name__)




@analysis_app.get("<dataset>/<subset>/cluster")
@validate_subset
def flask_get_clustering(dataset, subset, subset_path):
    return compute_clusters(dataset, subset)
