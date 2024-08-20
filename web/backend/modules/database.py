import json
import os.path
from pathlib import Path

import flask
import numpy as np

db_app = flask.Blueprint("db", __name__)
samples_folder = os.path.join(Path(__file__).parents[3], "data", "samples")

@db_app.get("machines")
def flask_get_machines_list():
    return ["dummy", "dummy2"]

@db_app.get("<machine>/samples")
def flask_get_samples(machine):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    return os.listdir(os.path.join(samples_folder, machine))


@db_app.get("<machine>/samples/<sampleId>/values")
def flask_get_values(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "values.npy"))
    return values.tolist()


@db_app.get("<machine>/samples/<sampleId>/projected")
def flask_get_projection(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    values: np.ndarray = np.load(os.path.join(sample_path, "projected.npy"))
    return values.tolist()


@db_app.get("<machine>/samples/<sampleId>/thumbnail")
def flask_get_sample_thumb(machine, sampleId):
    if not os.path.exists(os.path.join(samples_folder, machine)):
        return "Machine not found", 404
    sample_path = os.path.join(samples_folder, machine, sampleId)
    if not os.path.exists(sample_path):
        return "Sample not found", 404
    return flask.send_file(os.path.join(sample_path, "preview.png"), mimetype='image/png')


# WARNING: NOT THREAD SAFE!!! This will break if multiple users use the application at the same time
# Might switch to proper database in the future, but for prototype this is fine
@db_app.get("<machine>/labels/<sampleId>")
def flask_get_labels(machine, sampleId):
    with open(os.path.join(Path(__file__).parent, "labels.json"), "r") as f:
        labels_json = json.load(f)
    machine_json = labels_json.get(machine, {})
    sample_labels_json = machine_json.get(sampleId, [])
    return sample_labels_json


# WARNING: NOT THREAD SAFE!!! This will break if multiple users use the application at the same time
# Might switch to proper database in the future, but for prototype this is fine
@db_app.post("<machine>/labels/<sampleId>")
def flask_add_label(machine, sampleId):
    data = flask.request.get_json()
    print("Add", data)
    with open(os.path.join(Path(__file__).parent, "labels.json"), "r") as f:
        json_file = json.load(f)
    if machine not in json_file:
        json_file[machine] = {}
    if sampleId not in json_file[machine]:
        json_file[machine][sampleId] = []
    json_file[machine][sampleId].append(data)
    with open(os.path.join(Path(__file__).parent, "labels.json"), "w") as f:
        f.write(json.dumps(json_file, indent=4))
    return "OK", 200


# WARNING: NOT THREAD SAFE!!! This will break if multiple users use the application at the same time
# Might switch to proper database in the future, but for prototype this is fine
@db_app.delete("<machine>/labels/<sampleId>")
def flask_delete_label(machine, sampleId):
    data = flask.request.get_json()
    index = int(data["index"])
    print("Delete", data)
    with open(os.path.join(Path(__file__).parent, "labels.json"), "r") as f:
        json_file = json.load(f)
    if machine not in json_file:
        json_file[machine] = {}
    if sampleId not in json_file[machine]:
        json_file[machine][sampleId] = []
    json_file[machine][sampleId] = [item for item in json_file[machine][sampleId] if index < item["from"] or item["to"] < index]
    with open(os.path.join(Path(__file__).parent, "labels.json"), "w") as f:
        f.write(json.dumps(json_file, indent=4))
    return "OK", 200
