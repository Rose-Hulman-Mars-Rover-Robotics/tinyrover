from enum import Enum
from math import sqrt
import requests
import signal
import sys

#What the rover is looking for
class Modes(Enum):
    GNSS = 0
    AR = 1
    OBJECT = 2

#We only need to store one set of information since we can change the code in between targets
#TODO: Have this store all locations so we don't need to manually change things
mode = Modes.GNSS
coordinate = (0, 0)
item = "mallet" #The object to look for, for Modes.OBJECT
#Places we can return to
checkpoints = []

def abort(signum, frame):
    if len(checkpoints) == 0:
        sys.exit()

    r = requests.get("http://127.0.0.1:5001/data", timeout=3, json={"k": "gps"})
    location = r.json()["v"]

    closest = checkpoints[0]
    for i in range(1, len(checkpoints)):
        if sqrt((checkpoints[i][0] - location[0]) ** 2 + (checkpoints[i][1] - location[1]) ** 2) < sqrt((closest[0] - location[0]) ** 2 + (closest[1] - location[1]) ** 2):
            closest = checkpoints[i]

    r = requests.get(
        "http://192.168.0.12:8081/directpath",
        json={"lat": closest[0], "long": closest[1]},
    )
    sys.exit()

def autonomous_gnss():
    r = requests.get(
        "http://192.168.0.12:8081/directpath",
        json={"lat": coordinate[0], "long": coordinate[1]},
    )
    #TODO: Make sure this waits until it arrives before running the following code

    print("DESTINATION REACHED")
    #TODO: Change light to flashing green

def autonomous_ar():
    r = requests.get(
        "http://192.168.0.12:8081/directpath",
        json={"lat": coordinate[0], "long": coordinate[1]},
    )

    #TODO: Rotate in growing circle to find post

    #TODO: Drive to post

    print("DESTINATION REACHED")
    #TODO: Change light to flashing green

def autonomous_object():
    r = requests.get(
        "http://192.168.0.12:8081/directpath",
        json={"lat": coordinate[0], "long": coordinate[1]},
    )

    #TODO: Search for object

    #TODO: Show camera view with object highlighted
    print("DESTINATION REACHED")
    # TODO: Change light to flashing green

if __name__ == '__main__':
    signal.signal(signal.SIGINT, abort)

    #TODO: Set light to red

    match mode:
        case Modes.GNSS:
            autonomous_gnss()
        case Modes.AR:
            autonomous_ar()
        case Modes.OBJECT:
            autonomous_object()