import flask

from web.backend.helper.clustering import compute_clusters_inc_dbscan
from web.backend.helper.validators import validate_subset

analysis_app = flask.Blueprint("analysis", __name__)

@analysis_app.post("<dataset>/<subset>/cluster")
@validate_subset
def flask_compute_clustering(dataset, subset, path):
    db = flask.current_app.config["DB"]
    compute_clusters_inc_dbscan(db, dataset, subset)
    return {"success": True}
