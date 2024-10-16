import json
import time

import redis

r = redis.Redis(host="localhost", port=6379, db=1)


def parse_file(machine, filename, prefix, maxSampleSize, saveParsed):
    r_key = f"vibrana:{machine}:{filename}"
    status = {
        "dwparse": {"status": "processing"},
        "split": {"status": "waiting for Dewesoft parsing to complete", "items": {}}
    }
    r.set(r_key, json.dumps(status))
    time.sleep(0.5)
    status["dwparse"]["status"] = "done"
    status["split"]["status"] = "processing"
    r.set(r_key, json.dumps(status))
    for i in range(4):
        item_name = f"{prefix}-{str(i).zfill(4)}"
        status["split"]["items"][item_name] = "splitting"
        r.set(r_key, json.dumps(status))
        time.sleep(1)
        status["split"]["items"][item_name] = "projecting"
        r.set(r_key, json.dumps(status))
        time.sleep(1)
        status["split"]["items"][item_name] = "frequency"
        r.set(r_key, json.dumps(status))
        time.sleep(1)
        status["split"]["items"][item_name] = "done"
        r.set(r_key, json.dumps(status))