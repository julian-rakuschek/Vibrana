import json
import os.path
from pathlib import Path

import flask
import numpy as np
import pymongo
from bson import ObjectId, json_util
from pymongo.database import Database
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from web.backend.helper.validators import validate_subset, validate_chunk_path
from web.backend.settings import chunks_folder, READ_ONLY

db_app = flask.Blueprint("db", __name__)


def serialize_mongodb(output):
    temp = json.dumps(output, default=json_util.default)
    return json.loads(temp)


def get_db() -> Database:
    mongo_url = f"mongodb://{'vibrana_mongodb' if os.environ.get('DOCKER', "False") == 'True' else 'localhost'}:27017/"
    conn = pymongo.MongoClient(mongo_url)
    db: Database = conn["Vibrana"]
    return db


