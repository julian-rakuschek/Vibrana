import datetime
import json
import os
import threading
import time
from pathlib import Path

import redis
import socketio

from web.backend.data_loaders.redisLoader import RedisLoader
from web.backend.threads.computingThread import ComputingThread
import web.backend.helper.database as database

class CoordinatorThread(threading.Thread):
    def __init__(self, max_threads):
        threading.Thread.__init__(self)
        self.max_threads = max_threads

        redis_host = "localhost"
        if os.environ.get('DOCKER', "False") == 'True':
            redis_host = "anoscout_redis"

        self.r = redis.Redis(host=redis_host, port=6379, db=1)
        self.db = database.get_db()
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')
        time.sleep(1)

        with open(os.path.join(Path(__file__).parents[1], "datasets.json")) as f:
            self.datasets = json.load(f)
        self.loaders = {}
        self.threads = {}
        for dataset_name, dataset_object in self.datasets.items():
            self.loaders[dataset_name] = {}
            self.threads[dataset_name] = {}
            for subset_name, subset_object in dataset_object["subsets"].items():
                loader = RedisLoader(subset_object["file"], dataset_name, subset_name)
                threads = [ComputingThread(self.db, self.r, loader, subset_object["sliding_window_size"], subset_object["slice_size"], self.sio) for _ in range(max_threads)]
                for t in threads:
                    t.start()
                self.loaders[dataset_name][subset_name] = loader
                self.threads[dataset_name][subset_name] = threads
        print("Coordinator initialized!")

    def run(self):
        while True:
            # print(datetime.datetime.now().isoformat())
            for dataset_name, dataset_object in self.datasets.items():
                for subset_name, subset_object in dataset_object["subsets"].items():
                    target_threads = database.get_target_threads(self.db, dataset_name, subset_name)
                    if target_threads is None:
                        target_threads = 0
                    # print(dataset_name, subset_name, target_threads)
                    for i, t in enumerate(self.threads[dataset_name][subset_name]):
                        t.set_active(i < target_threads)
            time.sleep(0.5)


if __name__ == '__main__':
    coordinator = CoordinatorThread(10)
    coordinator.start()

