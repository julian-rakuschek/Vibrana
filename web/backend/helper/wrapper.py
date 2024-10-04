from functools import wraps
import os
from pathlib import Path

from flask import jsonify

from web.backend.settings import samples_folder


def validate_machine(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        machine = kwargs.get('machineId')
        machine_path = os.path.join(samples_folder, machine)
        if not os.path.exists(machine_path):
            return jsonify({"error": "Machine not found"}), 404
        return f(machine_path=machine_path, *args, **kwargs)

    return decorated_function

def validate_sample_path(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        machine = kwargs.get('machineId')
        sampleId = kwargs.get('sampleId')
        machine_path = os.path.join(samples_folder, machine)
        if not os.path.exists(machine_path):
            return jsonify({"error": "Machine not found"}), 404
        sample_path = os.path.join(machine_path, sampleId)
        if not os.path.exists(sample_path):
            return jsonify({"error": "Sample not found"}), 404
        return f(sample_path=sample_path, *args, **kwargs)

    return decorated_function
