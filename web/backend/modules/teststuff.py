import requests

test = requests.post("http://localhost:5000/api/db/labels/dummy", json={"from": 400, "to": 800})
test = requests.post("http://localhost:5000/api/db/labels/dummy", json={"from": 900, "to": 1800})
test = requests.delete("http://localhost:5000/api/db/labels/dummy", json={"index": 901})