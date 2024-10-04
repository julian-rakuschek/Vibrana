import io
import os.path
from pathlib import Path

import flask
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from web.backend.helper.analysis import compute_mds_embedding, compute_distance_profile, compute_normal_tube, count_anomaly_intervals, compute_anomaly_metrics
from web.backend.helper.wrapper import validate_sample_path, validate_machine
from web.backend.modules.database import get_db

analysis_app = flask.Blueprint("analysis", __name__)
samples_folder = os.path.join(Path(__file__).parents[3], "data", "samples")


@analysis_app.get("<machineId>/<sampleId>/mdsEmbedding")
@validate_sample_path
def flask_get_mds_embedding(machineId, sampleId, sample_path):
    window_size = int(flask.request.args.get("window_size", 1000))
    xl_2 = compute_mds_embedding(sample_path, window_size)
    return xl_2.tolist()


@analysis_app.get("<machineId>/<sampleId>/distanceProfile")
@validate_sample_path
def flask_get_distance_profile(machineId, sampleId, sample_path):
    distances = compute_distance_profile(get_db(), machineId, sample_path)
    return distances.tolist()


@analysis_app.get("<machineId>/<sampleId>/distanceProfile/img")
@validate_sample_path
def flask_get_distance_profile_img(machineId, sampleId, sample_path):
    distances = compute_distance_profile(get_db(), machineId, sample_path)
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    plt.clf()
    fig, ax = plt.subplots(nrows=2, ncols=1)
    fig.set_size_inches(20, 10)
    ax[0].set_title("Raw Signal")
    ax[0].set_xlim([0, len(values)])
    ax[0].plot(values, color="black")
    ax[1].set_title("Similarities")
    ax[1].set_xlim([0, len(distances)])
    ax[1].plot(distances, color="navy")
    normal_tube = compute_normal_tube(get_db(), machineId)
    ax[1].axhline(normal_tube[0], color="red")
    ax[1].axhline(normal_tube[1], color="red")
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return flask.Response(output.getvalue(), mimetype='image/png')


@analysis_app.get("<machineId>/normal_tube")
@validate_machine
def flask_get_normal_tube(machineId, machine_path):
    return compute_normal_tube(get_db(), machineId)


@analysis_app.get("<machineId>/anomaly_metrics/<sampleId>")
@validate_sample_path
def flask_get_anomaly_ratio(machineId, sampleId, sample_path):
    return flask.jsonify(compute_anomaly_metrics(get_db(), machineId, sampleId))


@analysis_app.get("<machineId>/anomaly_metrics")
@validate_machine
def flask_get_anomaly_ratios(machineId, machine_path):
    samples = os.listdir(os.path.join(samples_folder, machineId))
    db = get_db()
    normals = compute_normal_tube(db, machineId)
    anomaly_sample_metrics = []
    for sampleId in samples:
        anomaly_sample_metrics.append(compute_anomaly_metrics(db, machineId, sampleId, normals))
    anomaly_sample_metrics.sort(key=lambda x: x["ratio"], reverse=True)
    return anomaly_sample_metrics
