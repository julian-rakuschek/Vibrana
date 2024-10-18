import io
import json
import os.path
from pathlib import Path

import flask
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from web.backend.helper.analysis import *
from web.backend.helper.wrapper import validate_sample_path, validate_machine
from web.backend.modules.database import get_db

analysis_app = flask.Blueprint("analysis", __name__)


@analysis_app.get("<machineId>/<sampleId>/mdsEmbedding")
@validate_sample_path
def flask_get_mds_embedding(machineId, sampleId, sample_path):
    window_size = int(flask.request.args.get("window_size", 1000))
    xl_2 = compute_mds_embedding(sample_path, window_size)
    return xl_2.tolist()


@analysis_app.route("<machineId>/<sampleId>/distanceProfile", methods=["GET", "POST"])
@validate_sample_path
def flask_get_distance_profile(machineId, sampleId, sample_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        distances = compute_distance_profile(sample_path, data["labels"])
    else:
        labels = list(get_db()["labels"].find({"machine": machineId}))
        distances = compute_distance_profile(sample_path, labels)
    return distances.tolist()


@analysis_app.route("<machineId>/<sampleId>/distanceProfile/quantized", methods=["GET", "POST"])
@validate_sample_path
def flask_get_distance_profile_quantized(machineId, sampleId, sample_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        distances = compute_quantized_distance_profile(machineId, sampleId, data["labels"], data["normals"])
    else:
        db = get_db()
        labels = list(db["labels"].find({"machine": machineId}))
        normals = db["normals"].find_one({"machine": machineId})
        distances = compute_quantized_distance_profile(machineId, sampleId, labels, normals)
    return distances


@analysis_app.get("<machineId>/<sampleId>/distanceProfile/img")
@validate_sample_path
def flask_get_distance_profile_img(machineId, sampleId, sample_path):
    labels = list(get_db()["labels"].find({"machine": machineId}))
    distances = compute_distance_profile(sample_path, labels)
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


@analysis_app.route("<machineId>/normal_tube", methods=["GET", "POST"])
@validate_machine
def flask_get_normal_tube(machineId, machine_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        return compute_normal_tube(machineId, data["labels"], data["normals"])
    else:
        db = get_db()
        labels = list(db["labels"].find({"machine": machineId}))
        normals = db["normals"].find_one({"machine": machineId})
        return compute_normal_tube(machineId, labels, normals)


@analysis_app.route("<machineId>/anomaly_metrics/<sampleId>", methods=["GET", "POST"])
@validate_sample_path
def flask_get_anomaly_ratio(machineId, sampleId, sample_path):
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        return flask.jsonify(compute_anomaly_metrics(machineId, sampleId, data["labels"], data["normals"]))
    else:
        db = get_db()
        labels = list(db["labels"].find({"machine": machineId}))
        normals = db["normals"].find_one({"machine": machineId})
        return flask.jsonify(compute_anomaly_metrics(machineId, sampleId, labels, normals))


@analysis_app.route("<machineId>/anomaly_metrics", methods=["GET", "POST"])
@validate_machine
def flask_get_anomaly_ratios(machineId, machine_path):
    samples = os.listdir(os.path.join(samples_folder, machineId))
    if flask.request.method == "POST":
        data = json.loads(flask.request.data)
        labels, normals = data["labels"], data["normals"]
    else:
        db = get_db()
        labels = list(db["labels"].find({"machine": machineId}))
        normals = db["normals"].find_one({"machine": machineId})
    normal_tube = compute_normal_tube(machineId, labels, normals)
    anomaly_sample_metrics = []
    for sampleId in samples:
        metrics = compute_anomaly_metrics(machineId, sampleId, labels, normals, normal_tube)
        if metrics is None:
            continue
        anomaly_sample_metrics.append(metrics)
    anomaly_sample_metrics.sort(key=lambda x: x["ratio"], reverse=True)
    return anomaly_sample_metrics
