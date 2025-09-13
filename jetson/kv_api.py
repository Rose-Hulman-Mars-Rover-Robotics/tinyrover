import requests

default_value = {"v": "no value"}

def send_kv(k, v, location="local"):
    if location == "local":
        r = requests.put("http://127.0.0.1:5001/data", json={"k": k, "v": v})
    else:
        r = requests.put("http://192.168.0.12:5001/data", json={"k": k, "v": v})


def grab_kv(k):
    r = requests.get("http://127.0.0.1:5001/data", json={"k": k})
    return r.json()


def grab_brown():
    r = requests.get("http://127.0.0.1:5001/brown")
    return r.json()
