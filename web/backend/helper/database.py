import json
import os

import pymongo
from bson import json_util
from pymongo.synchronous.database import Database


def serialize_mongodb(output):
    temp = json.dumps(output, default=json_util.default)
    return json.loads(temp)


def get_db() -> Database:
    url = "mongodb://localhost:27017/"
    if os.environ.get('DOCKER', "False") == 'True':
        url = "mongodb://anoscout_mongodb:27017/"
    conn = pymongo.MongoClient(url)
    db: Database = conn["VibranaDB"]
    return db

# ----------------------------------------------
#              Fingerprint Management
# ----------------------------------------------

