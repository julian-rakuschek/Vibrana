import threading

import redis


class CoordinatorThread(threading.Thread):
    def __init__(self, redis_instance: redis.Redis):
        threading.Thread.__init__(self)
        self.redis = redis_instance
