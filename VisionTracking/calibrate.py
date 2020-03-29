import numpy as np
import cv2
import json

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare expected chessboard object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
# depends on size of chessboard used, most likely 9 by 6 internal verticies
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    _, img = cap.read()
    cv2.imshow('Output',img)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray,(9,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        # Need a 1 to 1 mapping between object points and corner points, in this case object points always same
        objpoints.append(objp)

        # Refines corners to find more exact positions (better than integer)
        cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        # width by height (9 by 6)
        cv2.drawChessboardCorners(img, (9,6), corners,ret)
        cv2.imshow('Output',img)
    
    # help human make sure not too many points so computation doesn't take forever, probably want 10-20 points
    print(len(objpoints))

    # press q to break
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# the magic
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
# mtx contains focal lengths and principal point, dist are distortion coefficients
print(mtx, dist)

cv2.destroyAllWindows()

tot_error = 0
for i in range(len(objpoints)):
    # use our calibration to project standard points with calculated angles, distances to original pictures
    # use this to find how accurate the calibration was
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    tot_error += error

# want a reprojection error less than 1 (px)
print('average error: ', tot_error/len(objpoints))

# third argument of 1 specifices line buffered, don't need to flush manually
f = open('VisionTracking/calibrate_results.txt', 'w', 1)
# write as json objects so readable and usable by other programs
f.write(json.dumps(mtx.tolist()))
f.write(json.dumps(dist.tolist()))
f.close()

