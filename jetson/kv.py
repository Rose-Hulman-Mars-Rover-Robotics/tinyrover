from flask import Flask, request
import numpy as np
import math
import time
from flask import send_from_directory
from flask_cors import CORS, cross_origin
from kv_api import local, server, port

app = Flask(__name__)
state = {}
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
default_value = {"v": "no value"}

@app.route("/data", methods=["GET", "POST", "PUT"])
@cross_origin()
def data():
    data = request.get_json()
    if request.method == "PUT":
        k = data["k"]
        v = data["v"]
        state[k] = v
        return "ok", 200
    else:
        k = data["k"]
        if k in state:
            v = state[k]
            return {"v": v}, 200
        else:
            return default_value, 200


rate = 0.2
v = [1.0, 0.0, 0.0, 0.0]


@app.route("/brown", methods=["GET", "PUT", "POST"])
@cross_origin()
def brownian():
    v[0] -= rate * np.random.randn()
    v[1] -= rate * np.random.randn()
    v[2] -= rate * np.random.randn()
    v[3] -= rate * np.random.randn()
    magnitude = math.dist(v, [0, 0, 0, 0])
    v[0] /= magnitude
    v[1] /= magnitude
    v[2] /= magnitude
    v[3] /= magnitude
    return v


@app.route("/brownsleep", methods=["GET", "PUT", "POST"])
@cross_origin()
def browniansleep():
    v[0] -= rate * np.random.randn()
    v[1] -= rate * np.random.randn()
    v[2] -= rate * np.random.randn()
    v[3] -= rate * np.random.randn()
    magnitude = math.dist(v, [0, 0, 0, 0])
    v[0] /= magnitude
    v[1] /= magnitude
    v[2] /= magnitude
    v[3] /= magnitude
    time.sleep(0.25)
    return v


@app.route("/frontend/<path:path>")
@cross_origin()
def send_report(path):
    return send_from_directory("frontend", path)


@app.route("/")
@cross_origin()
def slash():
    return send_from_directory("frontend", "kv.html")


@app.route("/everything", methods=["GET", "PUT", "POST"])
@cross_origin()
def everything():
    return state, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, threaded=False)
    print(f"local running on http://{local}:{port}/")
    print(f"server running on http://{server}:{port}/")
