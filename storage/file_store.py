# import json
# import os
# import uuid
# import time

# BASE = "data"
# os.makedirs(BASE, exist_ok=True)


# def save_eval(results):
#     eid = str(uuid.uuid4())
#     timestamp = int(time.time())

#     payload = {
#         "timestamp": timestamp,
#         "results": results
#     }

#     path = f"{BASE}/{eid}.json"

#     with open(path, "w") as f:
#         json.dump(payload, f)

#     return f"{eid}.json"


# def load_all():
#     return os.listdir(BASE)


# def load_eval(eid):
#     with open(f"{BASE}/{eid}") as f:
#         return json.load(f)

import json
import os
import uuid
import time

BASE = "data"
os.makedirs(BASE, exist_ok=True)


def save_eval(results):
    eid = str(uuid.uuid4())
    timestamp = int(time.time())

    payload = {
        "timestamp": timestamp,
        "results": results
    }

    with open(f"{BASE}/{eid}.json", "w") as f:
        json.dump(payload, f)

    return f"{eid}.json"


def load_all():
    return os.listdir(BASE)


def load_eval(eid):
    with open(f"{BASE}/{eid}") as f:
        data = json.load(f)

    # 🔥 BACKWARD COMPATIBILITY
    if isinstance(data, list):
        return {
            "timestamp": None,
            "results": data
        }

    return data