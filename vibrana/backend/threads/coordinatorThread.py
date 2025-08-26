import os
import threading
import time

import redis
import socketio

from web.backend.data_loaders.redisLoader import RedisLoader
from web.backend.helper.config import crawl_dataset_folder
from web.backend.threads.computingThread import ComputingThread
import web.backend.helper.database as database


class CoordinatorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        redis_host = "localhost"
        if os.environ.get('DOCKER', "False") == 'True':
            redis_host = "anoscout_redis"

        self.r = redis.Redis(host=redis_host, port=6379, db=1)
        self.db = database.get_db()
        print("Connecting to socket ...")
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')
        time.sleep(1)
        print("Connected to socket")

        self.datasets = crawl_dataset_folder()
        self.loaders = {}
        self.threads = {}
        self.locks = {}
        print("Initiating threads:")
        for dataset_name, dataset_object in self.datasets.items():
            if dataset_object["dataset_type"] != "stream":
                continue
            self.loaders[dataset_name] = {}
            self.threads[dataset_name] = {}
            self.locks[dataset_name] = {}
            for subset_name, subset_object in dataset_object["subsets"].items():
                print(dataset_name, subset_name)
                loader = RedisLoader(subset_object["file"], dataset_name, subset_name)
                thread = ComputingThread(self.db, self.r, loader, self.insert_fingerprint, self.sio)
                thread.start()
                self.loaders[dataset_name][subset_name] = loader
                self.threads[dataset_name][subset_name] = thread
                self.locks[dataset_name][subset_name] = threading.Lock()
        print("Coordinator initialized!")

    def insert_fingerprint(self, dataset, subset, data):
        self.locks[dataset][subset].acquire()
        data = database.store_fingerprint(self.db, data, dataset, subset)
        self.locks[dataset][subset].release()
        return data

    def run(self):
        while True:
            for dataset_name, dataset_object in self.datasets.items():
                if dataset_object["dataset_type"] != "stream":
                    continue
                for subset_name, subset_object in dataset_object["subsets"].items():
                    is_running = database.get_running(self.db, dataset_name, subset_name)
                    self.threads[dataset_name][subset_name].set_active(is_running)
            time.sleep(0.5)


if __name__ == '__main__':
    coordinator = CoordinatorThread()
    coordinator.start()

