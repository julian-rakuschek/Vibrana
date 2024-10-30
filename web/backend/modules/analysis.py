import io
import json
import os.path
from pathlib import Path

import flask
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from web.backend.helper.analysis import *
from web.backend.helper.wrapper import validate_chunk_path, validate_subset
from web.backend.modules.database import get_db

analysis_app = flask.Blueprint("analysis", __name__)


@analysis_app.get("<dataset>/<subset>/<chunk>/mdsEmbedding")
@validate_chunk_path
def flask_get_mds_embedding(dataset, subset, chunk, chunk_path):
    window_size = int(flask.request.args.get("window_size", 2000))
    xl_2 = compute_mds_embedding(chunk_path, window_size)
    return xl_2.tolist()


@analysis_app.route("<dataset>/<subset>/<chunk>/distanceProfile", methods=["GET", "POST"])
@validate_chunk_path
def flask_get_distance_profile(dataset, subset, chunk, chunk_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        distances = compute_distance_profile(chunk_path, data["labels"])
    else:
        labels = list(get_db()["labels"].find({"machine": dataset}))
        distances = compute_distance_profile(chunk_path, labels)
    return distances.tolist()


@analysis_app.route("<dataset>/<subset>/<chunk>/distanceProfile/quantized", methods=["GET", "POST"])
@validate_chunk_path
def flask_get_distance_profile_quantized(dataset, subset, chunk, chunk_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        distances = compute_quantized_distance_profile(dataset, subset, chunk, data["labels"], data["normals"])
    else:
        db = get_db()
        labels = list(db["labels"].find({"dataset": dataset, "subset": subset}))
        normals = db["normals"].find_one({"dataset": dataset, "subset": subset})
        distances = compute_quantized_distance_profile(dataset, subset, chunk, labels, normals)
    return distances


@analysis_app.get("<dataset>/<subset>/<chunk>/distanceProfile/img")
@validate_chunk_path
def flask_get_distance_profile_img(dataset, subset, chunk, chunk_path):
    labels = list(get_db()["labels"].find({"dataset": dataset, "subset": subset}))
    normals = get_db()["normals"].find_one({"dataset": dataset, "subset": subset})
    distances = compute_distance_profile(chunk_path, labels)
    values: np.ndarray = np.load(os.path.join(chunk_path, "values.npy"))
    plt.clf()
    fig, ax = plt.subplots(nrows=2, ncols=1)
    fig.set_size_inches(20, 10)
    ax[0].set_title("Raw Signal")
    ax[0].set_xlim([0, len(values)])
    ax[0].plot(values, color="black")
    ax[1].set_title("Similarities")
    ax[1].set_xlim([0, len(distances)])
    ax[1].plot(distances, color="navy")

    normal_tube = compute_normal_tube(dataset, subset, labels, normals)
    ax[1].axhline(normal_tube[0], color="red")
    ax[1].axhline(normal_tube[1], color="red")
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return flask.Response(output.getvalue(), mimetype='image/png')


@analysis_app.route("<dataset>/<subset>/normal_tube", methods=["GET", "POST"])
@validate_subset
def flask_get_normal_tube(dataset, subset, subset_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        return compute_normal_tube(dataset, subset, data["labels"], data["normals"])
    else:
        db = get_db()
        labels = list(db["labels"].find({"dataset": dataset, "subset": subset}))
        normals = db["normals"].find_one({"dataset": dataset, "subset": subset})
        return compute_normal_tube(dataset, subset, labels, normals)


@analysis_app.route("<dataset>/<subset>/<chunk>/anomaly_metrics", methods=["GET", "POST"])
@validate_chunk_path
def flask_get_anomaly_ratio(dataset, subset, chunk, chunk_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        return flask.jsonify(compute_anomaly_metrics(dataset, subset, chunk, data["labels"], data["normals"]))
    else:
        db = get_db()
        labels = list(db["labels"].find({"dataset": dataset, "subset": subset}))
        normals = db["normals"].find_one({"dataset": dataset, "subset": subset})
        return flask.jsonify(compute_anomaly_metrics(dataset, subset, chunk, labels, normals))


@analysis_app.route("<dataset>/<subset>/anomaly_metrics", methods=["GET", "POST"])
@validate_subset
def flask_get_anomaly_ratios(dataset, subset, subset_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        labels, normals = data["labels"], data["normals"]
    else:
        db = get_db()
        labels = list(db["labels"].find({"dataset": dataset, "subset": subset}))
        normals = db["normals"].find_one({"dataset": dataset, "subset": subset})
    normal_tube = compute_normal_tube(dataset, subset, labels, normals)
    anomaly_sample_metrics = []
    for chunk in os.listdir(subset_path):
        metrics = compute_anomaly_metrics(dataset, subset, chunk, labels, normals, normal_tube)
        if metrics is None:
            continue
        anomaly_sample_metrics.append(metrics)
    anomaly_sample_metrics.sort(key=lambda x: x["ratio"], reverse=True)
    return anomaly_sample_metrics
