import requests

local = "127.0.0.1"
server = "192.168.0.12"
port = "5001"


def send_kv(k, v, location="local"):
    ip = local if location == "local" else server
    route = f"http://{ip}:{port}/data"
    requests.put(route, json={"k": k, "v": v})


def grab_kv(k):
    r = requests.get(f"http://{local}:{port}/data", json={"k": k})
    return r.json()


def grab_brown():
    r = requests.get(f"http://{local}:{port}/brown")
    return r.json()
