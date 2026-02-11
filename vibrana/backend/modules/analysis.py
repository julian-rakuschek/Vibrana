import flask

from vibrana.backend.helper.database import cluster_all_fingerprints_all_feature_descriptors
from vibrana.backend.helper.validators import validate_subset
import vibrana.backend.helper.database as database

analysis_app = flask.Blueprint("analysis", __name__)

@analysis_app.post("<dataset>/<subset>/cluster")
@validate_subset
def flask_compute_clustering(dataset, subset, path):
    db = flask.current_app.config["DB"]
    cluster_all_fingerprints_all_feature_descriptors(db, dataset, subset)
    database.add_provenance_record(db, dataset, subset)
    return {"success": True}
