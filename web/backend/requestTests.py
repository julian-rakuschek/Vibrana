import requests
import redis

res = requests.request("POST", "http://127.0.0.1:5000/api/computing/hydro/x/set_target_threads", json={"threads": 1})
print(res)

res = requests.request("GET", "http://127.0.0.1:5000/api/computing/hydro/x/get_target_threads")
print(res)


