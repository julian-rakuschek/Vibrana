from functools import wraps
import os
from pathlib import Path

from flask import jsonify

from web.backend.settings import chunks_folder


def validate_subset(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        dataset = kwargs.get('dataset')
        subset = kwargs.get('subset')
        subset_path = os.path.join(chunks_folder, dataset, subset)
        if not os.path.exists(subset_path):
            return jsonify({"error": "subset not found"}), 404
        return f(subset_path=subset_path, *args, **kwargs)

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
