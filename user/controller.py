from enum import Enum
import pygame
import requests
import sys


controllers = []
activeController = None

# TODO: change values to adjust how controls feel after more field testing
driveStrength = 30
maxDriveStrength = 90
driveStrengthIncrement = 5
turnStrength = 20
maxTurnStrength = 60
turnStrengthIncrement = 3

adjustDriveStrength = 0
adjustTurnStrength = 0

leftStickMotion = [0.0, 0.0]
rightStickMotion = [0.0, 0.0]
rightTrigger = 0.0
leftTrigger = 0.0
btnA = False
btnB = False
btnX = False
btnY = False
btnLB = False
btnRB = False

leftSpeed = 90
rightSpeed = 90


class PyGameBtn(Enum):
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    LEFTTHUMB = 8
    RIGHTTHUMB = 9
    XBOX = 10
    SHARE = 11
    DPAD = 17


def main():
    pygame.init()
    pygame.joystick.init()

    while True:
        if activeController is not None:
            getControllerInput()
            ignoreInputsSmallerThan(0.01)
            normalizeTriggerValues()
            setWheelSpeedsBasedOnControllerInput()
            sendCommandToWheels()
        else:
            updateJoysticks()
        pygame.time.wait(100)


def printConnectedControllers():
    if len(controllers) > 0:
        print("Connected controllers:")
        for controller in controllers:
            print("- " + str(controller.get_name()))
    else:
        print("No controller connected")


def ignoreInputsSmallerThan(magnitude):
    global leftStickMotion, rightStickMotion, rightTrigger, leftTrigger

    for i in range(len(leftStickMotion)):
        if abs(leftStickMotion[i]) < magnitude:
            leftStickMotion[i] = 0.0

    for i in range(len(rightStickMotion)):
        if abs(rightStickMotion[i]) < magnitude:
            rightStickMotion[i] = 0.0

    if abs(rightTrigger) < magnitude:
        rightTrigger = 0.0

    if abs(leftTrigger) < magnitude:
        leftTrigger = 0.0


def handleButtonRelease(event):
    global btnA, btnB, btnX, btnY, btnLB, btnRB
    match event.button:
        case PyGameBtn.A.value:
            btnA = False
        case PyGameBtn.B.value:
            btnB = False
        case PyGameBtn.X.value:
            btnX = False
        case PyGameBtn.Y.value:
            btnY = False
        case PyGameBtn.LB.value:
            btnLB = False
        case PyGameBtn.RB.value:
            btnRB = False
        case (
            PyGameBtn.BACK.value,
            PyGameBtn.START.value,
            PyGameBtn.XBOX.value,
            PyGameBtn.LEFTTHUMB.value,
            PyGameBtn.RIGHTTHUMB.value,
        ):
            print(str(event.button) + "released (not mapped to a function)")


def handleButtonPress(event):
    global btnA, btnB, btnX, btnY, btnLB, btnRB
    match event.button:
        case PyGameBtn.A.value:
            btnA = True
        case PyGameBtn.B.value:
            btnB = True
        case PyGameBtn.X.value:
            btnX = True
        case PyGameBtn.Y.value:
            btnY = True
        case PyGameBtn.LB.value:
            btnLB = True
        case PyGameBtn.RB.value:
            btnRB = True
        case PyGameBtn.XBOX.value:
            handleQuit(event)
        case (
            PyGameBtn.BACK.value,
            PyGameBtn.START.value,
            PyGameBtn.LEFTTHUMB.value,
            PyGameBtn.RIGHTTHUMB.value,
        ):
            print(str(event.button) + "pressed (not mapped to a function)")


def normalizeTriggerValues():
    global rightTrigger, leftTrigger
    leftTrigger = (leftTrigger + 1) / 2
    rightTrigger = (rightTrigger + 1) / 2


def updateJoysticks():
    global controllers, activeController
    controllers = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    if len(controllers) > 0:
        activeController = controllers[0]
    else:
        activeController = None
    printConnectedControllers()


def handleQuit(event):
    global leftSpeed, rightSpeed

    leftSpeed = 90
    rightSpeed = 90

    sendCommandToWheels()

    pygame.quit()
    sys.exit()


def getPygameEventInputs():
    for event in pygame.event.get():
        match event.type:
            case pygame.JOYBUTTONDOWN:
                handleButtonPress(event)
            case pygame.JOYBUTTONUP:
                handleButtonRelease(event)
            case pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED:
                updateJoysticks(event)
            case pygame.QUIT:
                handleQuit(event)


def getAnalogInputs():
    if activeController is not None:
        global leftStickMotion, rightStickMotion, leftTrigger, rightTrigger
        leftStickMotion[0] = activeController.get_axis(0)
        leftStickMotion[1] = activeController.get_axis(1)

        rightStickMotion[0] = activeController.get_axis(2)
        rightStickMotion[1] = activeController.get_axis(3)

        leftTrigger = activeController.get_axis(4)
        rightTrigger = activeController.get_axis(5)


def getDpadInput():
    if activeController is not None:
        global driveStrength, turnStrength, adjustDriveStrength, adjustTurnStrength

        dpadX, dpadY = activeController.get_hat(0)
        prevAdjustDriveStrength = adjustDriveStrength
        prevAdjustTurnStrength = adjustTurnStrength
        adjustDriveStrength = dpadY
        adjustTurnStrength = dpadX

        if prevAdjustDriveStrength == 0 and adjustDriveStrength == 1:
            newDriveStrength = driveStrength + driveStrengthIncrement
            if newDriveStrength < maxDriveStrength:
                driveStrength = newDriveStrength
        elif prevAdjustDriveStrength == 0 and adjustDriveStrength == -1:
            newDriveStrength = driveStrength - driveStrengthIncrement
            if newDriveStrength > 0:
                driveStrength = newDriveStrength

        if prevAdjustTurnStrength == 0 and adjustTurnStrength == 1:
            newTurnStrength = turnStrength + turnStrengthIncrement
            if newTurnStrength < maxTurnStrength:
                turnStrength = newTurnStrength
        elif prevAdjustTurnStrength == 0 and adjustTurnStrength == -1:
            newTurnStrength = turnStrength - turnStrengthIncrement
            if newTurnStrength > 0:
                turnStrength = newTurnStrength


def getControllerInput():
    if activeController is None:
        return
    getPygameEventInputs()
    getAnalogInputs()
    getDpadInput()


def setWheelSpeedsBasedOnControllerInput():
    global leftSpeed, rightSpeed

    if rightTrigger > 0:
        baseSpeed = 90 + (rightTrigger * driveStrength)
        leftSpeed = baseSpeed + (leftStickMotion[0] * turnStrength)
        rightSpeed = baseSpeed - (leftStickMotion[0] * turnStrength)
        if leftStickMotion[0] < 0:
            leftSpeed += 1
    elif leftTrigger > 0:
        baseSpeed = 90 - (leftTrigger * driveStrength)
        leftSpeed = baseSpeed - (leftStickMotion[0] * turnStrength)
        rightSpeed = baseSpeed + (leftStickMotion[0] * turnStrength)
    else:
        leftSpeed = 90 + (leftStickMotion[0] * turnStrength * 1.2)
        rightSpeed = 90 - (leftStickMotion[0] * turnStrength * 1.2)
        if leftStickMotion[0] < 0:
            leftSpeed += 1

    leftSpeed = min(max(int(leftSpeed), 0), 180)
    rightSpeed = min(max(int(rightSpeed), 0), 180)


def sendCommandToWheels():
    print("sending " + str(leftSpeed) + ", " + str(rightSpeed) + "...")

    try:
        requests.get(
            url="http://192.168.0.12:8080/wheel_command_both",
            timeout=4,
            json={"left": leftSpeed, "right": rightSpeed},
            headers={"Connection": "close"},
        )
        print("sent " + str(leftSpeed) + ", " + str(rightSpeed))
    except Exception as e:
        print("failed to send " + str(leftSpeed) + ", " + str(rightSpeed))
        print(e)


if __name__ == "__main__":
    main()
