from enum import Enum
from math import sqrt, floor, degrees, cos, pi, sin, atan2, radians
import requests
import signal
import sys
import cv2
import numpy as np
import time

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

    # Ratio used to spiral around the destination point
    RATIO = (1 + sqrt(5)) / 2
    # Size of the aruco markers in cm
    MARKER_SIZE = 20

    # Camera matrix and distortion coefficients, these values need to be calibrated
    # TODO: Replace these with calibrated matrices
    CAM = np.zeros(3, dtype=np.float32)
    DIST = np.zeros(1)

    searching = True

    # Set up the aruco camera
    # This code is copied from aruco.py, we should probably make this some kind of module
    cap = cv2.VideoCapture(0)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Check if we can see the aruco marker
    r = requests.get(
        "http://127.0.0.1:5001/data", timeout=3, json={"k": "scuffed_yaw"}
    )
    yaw = float(r.json()["v"])
    yaw *= 180.0 / 3.14159265

    for i in range(4):
        r = requests.get(
            "http://192.168.0.12:8081/turn", json={"target": (yaw + 90 * (i + 1)) % 360}
        )
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ids, _ = detector.detectMarkers(gray)

        if ids:
            searching = False
            break

    """
    This will draw out the spiral associated with the given ratio searching for at each 
    point. This could be improved through by having the aruco detection run while the 
    rover is moving, for example running a command that just makes a spiral pattern and 
    running wheel command stop once we detect an aruco marker. Implementing a way for the 
    rover to trace out bezier curves could also make the spiral look more natural as well.
    """
    n = 0
    while searching:
        n += 1

        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ids, _ = detector.detectMarkers(gray)

        if ids:
            searching = False
            break

        # This code should be changed to use the wheel encoders to drive a designated
        # distance forward whenever we get them
        r = requests.get(
            "http://127.0.0.1:8080/wheel_command_both",
            timeout=0.0000000000001,  # Hacky way to not wait for a response
            json={"left": 135, "right": 135},
        )
        time.sleep(floor(RATIO ** n))
        r = requests.get("http://127.0.0.1:8080/wheel_command_stop")

        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ids, _ = detector.detectMarkers(gray)

        if ids:
            searching = False
            break

        r = requests.get(
            "http://127.0.0.1:5001/data", timeout=3, json={"k": "scuffed_yaw"}
        )
        yaw = float(r.json()["v"])
        yaw *= 180.0 / 3.14159265

        r = requests.get(
            "http://192.168.0.12:8081/turn", json={"target": (yaw + 90) % 360}
        )

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    """
    Gets the distance to the aruco marker. tvec will contain 3 values representing the x (right),
    y (down), and z (forward) distance in centimeters from the center of the camera
    """
    _, _, tvec = cv2.solvePnP(
        np.array(
            [
                [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
                [MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
                [MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
                [-MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
            ],
            dtype=np.float32
        ),
        corners[0],
        CAM,
        DIST
    )

    # Rotate to face the marker
    r = requests.get(
        "http://127.0.0.1:5001/data", timeout=3, json={"k": "scuffed_yaw"}
    )
    yaw = degrees(float(r.json()["v"]))
    r = requests.get(
        "http://192.168.0.12:8081/turn", json={"target": (yaw - degrees(atan2(tvec[0], tvec[2]))) % 360}
    )

    _, _, tvec = cv2.solvePnP(
        np.array(
            [
                [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
                [MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
                [MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
                [-MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
            ],
            dtype=np.float32
        ),
        corners[0],
        CAM,
        DIST
    )

    r = requests.get(
        "http://127.0.0.1:5001/data", timeout=3, json={"k": "scuffed_yaw"}
    )
    yaw = float(r.json()["v"])
    r = requests.get("http://127.0.0.1:5001/data", timeout=3, json={"k": "gps"})
    loc = r.json()["v"]

    # TODO: Replace this with a call going tvec[2] cm forward once we get encoders
    # Centimeter per degree
    cm = (1 / ((2 * pi / 360) * 6378.137)) / 10
    # Assumes that 0 yaw is north, will stop around 1.5 meters away from target
    r = requests.get(
        "http://192.168.0.12:8081/directpath",
        json={
            "lat": loc[0] + (tvec[2] * sin(yaw) / cm) - (sin(yaw) / abs(sin(yaw))) * 0.000010125,
            "long": loc[1] + (tvec[2] * cos(yaw) / (cm * cos(radians(loc[0])))) - (cos(yaw) / abs(cos(yaw))) * 0.00001
        },
    )

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