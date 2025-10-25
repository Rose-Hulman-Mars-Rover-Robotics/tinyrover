import cv2
import socket
import struct

HOST = ""
PORT = 8089  # TODO: change port if not available, close port when done with it
cap = cv2.VideoCapture(1)  # TODO: select correct camera index instead of hard coding it
# run `lsusb to list devices connected`
# our camera is "Sunplus Innovation Technology Inc."

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(10)
        conn, addr = s.accept()
        break
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print("failed to connect: ")
        print(e)

while True:
    ret, frame = cap.read()
    result, encoded_img = cv2.imencode(".jpg", frame)
    # print(len(encoded_img))
    data = encoded_img.tostring()  # change to `tobytes()`?
    message_size = struct.pack("L", len(data))
    conn.sendall(message_size + data)
