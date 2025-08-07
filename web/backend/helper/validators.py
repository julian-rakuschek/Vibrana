import json
from functools import wraps
import os
from pathlib import Path

from flask import jsonify

from web.backend.helper.config import crawl_dataset_folder
from web.backend.settings import chunks_folder

datasets = crawl_dataset_folder()


def validate_subset(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        dataset = kwargs.get('dataset')
        subset = kwargs.get('subset')
        if dataset not in datasets:
            return jsonify({"error": "Dataset not found in config file"}), 404
        if subset not in datasets[dataset]["subsets"]:
            return jsonify({"error": "Subset not found in dataset"}), 404
        file_path = datasets[dataset]["subsets"][subset]["file"]
        absolute_file_path = os.path.join(Path(__file__).parents[3], "data", file_path)
        return f(path=absolute_file_path, *args, **kwargs)
    return decorated_function


def validate_chunk_path(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        dataset = kwargs.get('dataset')
        subset = kwargs.get('subset')
        chunk = kwargs.get('chunk')
        chunk_path = os.path.join(chunks_folder, dataset, subset, chunk)
        if not os.path.exists(chunk_path):
            return jsonify({"error": "chunk not found"}), 404
        return f(chunk_path=chunk_path, *args, **kwargs)

    return decorated_function
