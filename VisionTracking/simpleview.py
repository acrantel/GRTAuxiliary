import numpy as np
import cv2
import json

# basic config reader, treats first word as key, everything else as value strings
def read_config(config_file):
    options = {}
    # start reading from top of file every time
    config_file.seek(0)
    for l in config_file.readlines():
        s = l.split(' ')
        # combine back any spaces that were split up
        # also using slice notation avoids index out of range errors
        options[s[0]] = ' '.join(s[1:])
    return options

config = open('VisionTracking/config.txt', 'r')
c = read_config(config)

# load camera matrix, distortion coeffs - they will be stored as a json object
camera = np.array(json.loads(c['camera_mtx']))
print(camera)

dist = np.array(json.loads(c['dist_coeffs']))
print(dist)

cap = cv2.VideoCapture(0)
cv2.namedWindow('Output', cv2.WINDOW_NORMAL)

while (cap.isOpened()):
    _, frame = cap.read()
    
    # undistort image according to camera calibration
    undistort = cv2.undistort(frame, camera, dist)

    cv2.imshow('Output', undistort)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
