import flask

from vibrana.backend.helper.clustering import compute_clusters_inc_dbscan
from vibrana.backend.helper.validators import validate_subset

analysis_app = flask.Blueprint("analysis", __name__)

@analysis_app.post("<dataset>/<subset>/cluster")
@validate_subset
def flask_compute_clustering(dataset, subset, path):
    db = flask.current_app.config["DB"]
    feature_descriptor = "tde"
    compute_clusters_inc_dbscan(db, dataset, subset, feature_descriptor)
    return {"success": True}
