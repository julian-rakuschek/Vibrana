import os
import threading
import time

import socketio

from vibrana.backend.data_loaders.redisLoader import RedisLoader, get_redis
from vibrana.backend.helper.config import crawl_dataset_folder
from vibrana.backend.threads.computingThread import ComputingThread
import vibrana.backend.helper.database as database


class CoordinatorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.r = get_redis()
        self.db = database.get_db()
        print("Connecting to socket ...")
        self.sio = socketio.Client()
        if os.environ.get('DOCKER', "False") == 'True':
            self.sio.connect('http://vibrana_app:5000')
        else:
            self.sio.connect('http://localhost:5000')
        time.sleep(1)
        print("Connected to socket")

        self.datasets = crawl_dataset_folder()
        self.loaders = {}
        self.threads = {}
        self.locks = {}
        print("Initiating threads:")
        for dataset_name, dataset_object in self.datasets.items():
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
        database.store_fingerprint(self.db, data, dataset, subset)
        labels = database.cluster_all_fingerprints_all_feature_descriptors(self.db, dataset, subset)
        self.locks[dataset][subset].release()
        return labels

    def run(self):
        while True:
            for dataset_name, dataset_object in self.datasets.items():
                for subset_name, subset_object in dataset_object["subsets"].items():
                    is_running = database.get_running(self.db, dataset_name, subset_name)
                    self.threads[dataset_name][subset_name].set_active(is_running)
            time.sleep(0.5)


if __name__ == '__main__':
    coordinator = CoordinatorThread()
    coordinator.start()

