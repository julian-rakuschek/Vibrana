import os

import pymongo
from pymongo.database import Database

url = "mongodb://localhost:27017/"
if os.environ.get('DOCKER', "False") == 'True':
    url = "mongodb://vibrana_mongodb:27017/"
conn = pymongo.MongoClient(url)
conn.drop_database('VibranaDB')
db: Database = conn['VibranaDB']
db.create_collection('fingerprints')
