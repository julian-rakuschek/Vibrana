import flask

from web.backend.helper.clustering import *
from web.backend.helper.validators import validate_subset

analysis_app = flask.Blueprint("analysis", __name__)

@analysis_app.get("<dataset>/<subset>/cluster")
@validate_subset
def flask_get_clustering(dataset, subset, subset_path):
    return compute_clusters(dataset, subset)
