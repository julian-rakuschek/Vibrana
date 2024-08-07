import json
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

# WARNING: NOT THREAD SAFE!!! This will break if multiple users use the application at the same time
# Might switch to proper database in the future, but for prototype this is fine
@db_app.get("labels/<series>")
def flask_get_labels(series):
    with open(os.path.join(Path(__file__).parent, "labels.json"), "r") as f:
        return json.load(f).get(series, [])


# WARNING: NOT THREAD SAFE!!! This will break if multiple users use the application at the same time
# Might switch to proper database in the future, but for prototype this is fine
@db_app.post("labels/<series>")
def flask_add_label(series):
    data = flask.request.get_json()
    print("Add", data)
    with open(os.path.join(Path(__file__).parent, "labels.json"), "r") as f:
        json_file = json.load(f)
    if series not in json_file:
        json_file[series] = []
    json_file[series].append(data)
    with open(os.path.join(Path(__file__).parent, "labels.json"), "w") as f:
        f.write(json.dumps(json_file, indent=4))
    return "OK", 200


# WARNING: NOT THREAD SAFE!!! This will break if multiple users use the application at the same time
# Might switch to proper database in the future, but for prototype this is fine
@db_app.delete("labels/<series>")
def flask_delete_label(series):
    data = flask.request.get_json()
    index = int(data["index"])
    print("Delete", data)
    with open(os.path.join(Path(__file__).parent, "labels.json"), "r") as f:
        json_file = json.load(f)
    if series not in json_file:
        json_file[series] = []
    print(json_file[series])
    json_file[series] = [item for item in json_file[series] if index < item["from"] or item["to"] < index]
    print(json_file[series])
    with open(os.path.join(Path(__file__).parent, "labels.json"), "w") as f:
        f.write(json.dumps(json_file, indent=4))
    return "OK", 200
