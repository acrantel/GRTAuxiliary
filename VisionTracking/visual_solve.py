import cv2
import numpy as np
import json

# basic config reader, treats first word as key, everything else as value strings
def read_config(config_file):
    options = {}
    for l in config_file.readlines():
        # allow for comments that start with #
        if l[0] != '#':
            s = l.split(' ')
            # combine back any spaces that were split up
            # also using slice notation avoids index out of range errors
            options[s[0]] = ' '.join(s[1:])
    return options

config = open('VisionTracking/config.txt', 'r')
c = read_config(config)

# area of vision tape target in inches
vision_tape_area = float(c['vision_tape_area'])
# width and height of the bounding box that contains the vision tape in inches
bounding_box_width = float(c['bounding_box_width'])
bounding_box_height = float(c['bounding_box_height'])
bounding_box_area = bounding_box_width * bounding_box_height
# coverage is a metric based on how much space the object takes up inside its bounding box
coverage_area = vision_tape_area / bounding_box_area
# aspect ratio of the bounding box
bounding_aspect = bounding_box_width / bounding_box_height

# width and height of the trapezoid (half a hexagon) that encloses the vision tape
hex_width = float(c['hex_width'])
hex_height = float(c['hex_height'])
# aspect ratio of the trapezoid
hex_ratio = hex_width / hex_height
# find area of hexagon from horizontal width, then divide by 2 to find trapezoid area
hex_area = 3/2 * np.sqrt(3) * (hex_width/2)**2 / 2
# solidity is a metric based on how much space the object takes up inside the surrounding convex polygons
solidity_expect = vision_tape_area / hex_area

# all metrics all scaled to a scale of 100 and down (100 - metric*100) to make it easier for human to change it 
# each one corresponds to respective metric
min_area = int(c['min_area'])
min_coverage = int(c['min_coverage'])
min_solidity = int(c['min_solidity'])
min_aspect = int(c['min_aspect'])
min_hex_ratio = int(c['min_hex_ratio'])


### NOT NECCESARY FOR SOLVEPNP - KEPT IN CASE NEED TO USE BASIC GEOMETRY IN FUTURE

kHorizontalFOVDeg = float(c['kHorizontalFOVDeg'])
kVerticalFOVDeg = float(c['kVerticalFOVDeg'])

kTargetHeightIn = float(c['kTargetHeightIn'])  # middle of hex height
kCameraHeightIn = float(c['kCameraHeightIn'])
kCameraPitchDeg = float(c['kCameraPitchDeg'])

### 

# load camera matrix, distortion coeffs - they will be stored as a json object
camera_matrix = np.array(json.loads(c['camera_mtx']))
dist_coeffs = np.array(json.loads(c['dist_coeffs']))

# the points of the target on a completely flat 2D surface, with center being center of hex
# all units in inches
obj_points = []
obj_points.append([-19.631, 0, 0]) # top left
obj_points.append([-9.816, -17, 0]) # bottom left
obj_points.append([9.816, -17, 0]) # bottom right
obj_points.append([19.631, 0, 0]) # top right

obj_points = np.array(obj_points, np.float32)

# angle in degrees
def law_of_cosines(a=None, b=None, c=None, opp_angle=None):
    if opp_angle is None:
        return np.degrees(np.arccos((c**2 - a**2 - b**2)/(-2*a*b)))
    else:
        opp_angle = np.radians(opp_angle)
        return np.sqrt(a**2 + b**2 - 2*a*b*np.cos(opp_angle))

def nothing(x): pass

cv2.namedWindow("Output", cv2.WINDOW_NORMAL)

cv2.createTrackbar('H_min', 'Output', 0, 255, nothing)
cv2.createTrackbar('H_max', 'Output', 255, 255, nothing)
cv2.createTrackbar('S_min', 'Output', 0, 255, nothing)
cv2.createTrackbar('S_max', 'Output', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Output', 0, 255, nothing)
cv2.createTrackbar('V_max', 'Output', 255, 255, nothing)

# cap = cv2.VideoCapture(0)
    
# if not cap.isOpened():
#     print("Error opening stream")

def valid_hex_contour(cnt):
    area = cv2.contourArea(cnt)

    #print(area)
    if area < min_area:
        return (0,0,0)

    # print("past area")

    rect = cv2.minAreaRect(cnt)
    box = np.int0(cv2.boxPoints(rect))
    rect_area = cv2.contourArea(box)

    diff_coverage = 100 - 100 * abs(area/rect_area - coverage_area)

    # width = max(rect[1])
    # height = min(rect[1])
    # diff_aspect = 100 - 100*abs(width/height - bounding_aspect)

    if diff_coverage < min_coverage:
        return (0,0,0)

    print("past cov")

    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    solidity = float(area)/hull_area
    diff_solidity = 100 - 100 * abs(solidity - solidity_expect)

    hull = list(map(lambda x: x[0], cv2.convexHull(cnt).tolist()))
    while len(hull) > 4:
        min_dist = [10000, 0]
        for i, p in enumerate(hull):
            x0, y0 = p
            x1, y1 = hull[i-1]
            x2, y2 = hull[(i+1) % len(hull)]
            d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.hypot((y2-y1), (x2-x1))
            if min_dist[0] > d:
                min_dist = [d, p]
        hull.remove(min_dist[1])

    hull = sorted(hull, key=lambda x: x[0])
    top = (hull[0], hull[3])
    bot = (hull[1], hull[2])
    dist_top = np.hypot(top[0][0]-top[1][0], top[0][1]-top[1][1])
    dist_bot = np.hypot(bot[0][0]-bot[1][0], bot[0][1]-bot[1][1])
    diff_hex_ratio = 100 - 100*(hex_ratio - dist_top/dist_bot)

    if diff_hex_ratio < min_hex_ratio or diff_solidity < min_solidity:
        return (0,0,0)

    total_diff = (diff_hex_ratio + diff_coverage) / 2

    epsilon = 0.005*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)

    return (total_diff, hull, approx)

def get_box(frame):
    distance = 0
    azimuth = 0
    pitch = 0
    yaw = 0
    roll = 0

    # undist = cv2.undistort(frame, cameraMatrix, dist_coeffs)
    # cv2.imshow("undist", undist)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_green =np.array([cv2.getTrackbarPos("H_min", "Output"), cv2.getTrackbarPos(
        "S_min", "Output"), cv2.getTrackbarPos("V_min", "Output")])
    upper_green =np.array([cv2.getTrackbarPos("H_max", "Output"), cv2.getTrackbarPos(
        "S_max", "Output"), cv2.getTrackbarPos("V_max", "Output")])
    #print(lower_green)

    mask = cv2.inRange(hsv, lower_green, upper_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)

    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
  
    # blur = cv2.medianBlur(imgray, 7)
    structure_element = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    #cv2.imshow("test", cv2.erode(imgray, erodeElement))
    #dilateElement = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    morphed = cv2.dilate(cv2.erode(imgray, structure_element), structure_element)

    ret, thresh = cv2.threshold(morphed, 64, 255, 0)

    contours, hierarchy =cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    best_hull = 0
    best_diff = 0
    best_approx = 0

    for cnt in contours:
        print(valid_hex_contour(cnt))
        total_diff, hull, approx = valid_hex_contour(cnt)
        if total_diff > best_diff:
            best_hull = hull
            best_diff = total_diff
            best_approx = approx
            # test = minmax(cnt.squeeze(), 0, 1, -1, 1) # -- min x
            # cv2.drawMarker(res, tuple(test), (0, 128, 255), thickness=3)
            # test = minmax(cnt.squeeze(), 0, 1, 1, -1) # -- max x
            # cv2.drawMarker(res, tuple(test), (0, 128, 255), thickness=3)
            # test = minmax(cnt.squeeze(), 1, 0, -1, -1) # -- min y
            # cv2.drawMarker(res, tuple(test), (0, 128, 255), thickness=3)
            # test = minmax(cnt.squeeze(), 1, 0, 1, 1) # -- max y
            # cv2.drawMarker(res, tuple(test), (0, 128, 255), thickness=3)


            leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
            # rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
            # bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
            # cv2.drawMarker(res, bottommost, (0, 128, 255), thickness=2)
            #cv2.drawMarker(res, leftmost, (0, 128, 255), thickness=2)
            
            # y_scale = -(2 * (leftmost[1] / frame.shape[0]) - 1)
            # cv2.putText(res, str(y_scale), tuple(leftmost), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,128,255))
            # cv2.drawMarker(res, rightmost, (0, 128, 255), thickness=2)
            area = cv2.contourArea(cnt)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            

    if best_hull != 0:
        pts1 = np.array(best_hull, np.float32)
        left, right = pts1[0], pts1[3]
        #print(left, right)
        
        print(best_hull, best_diff, best_approx)
        cv2.drawContours(res, [best_approx], -1, (0,255,125), 3)
        y_scale = -(2 * (left[1] / frame.shape[0]) - 1)
        print(y_scale)
        cv2.putText(res, str(y_scale), tuple(left), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,128,255))
        d1 =(kTargetHeightIn - kCameraHeightIn) / np.tan(
            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
        print(d1)

        y_scale = -(2 * (right[1] / frame.shape[0]) - 1)
        d2 =(kTargetHeightIn - kCameraHeightIn) / np.tan(
            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
        print(d2)

        angle1 = law_of_cosines(a=max([d1,d2]), b=40, c=min([d1,d2]))
        cd = law_of_cosines(a=max([d1,d2]),b=20,opp_angle=angle1)
        #print(angle1, cd)

        final = law_of_cosines(a=cd, b=20, c=max([d1,d2]))
        #print(final)

        x = cd * np.cos(np.radians(final))
        y = cd * np.sin(np.radians(final))
        if d2 < d1: x *= -1
        print("ONLY MATH", x,y)

        #test = []
        for p in pts1:
            cv2.drawMarker(res, tuple(p), (0, 255, 0), thickness=2)
            
            # y_scale = -(2 * (p[1] / frame.shape[0]) - 1)
            # distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(
            #     np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
            # #print(distance, p)
            # test.append(distance)

        # d1,d2 = test[0], test[3]
        # print(d1,d2)
        # test_ans = np.degrees(np.arccos((40**2-d1**2-d2**2)/(-2*d1*d2)))
        # print(test_ans)

        # print(pts1, obj_points)

        retval, revec, tvec, inliers = cv2.solvePnPRansac(obj_points, pts1, camera_matrix, dist_coeffs)
        #print(tvec[0][0], tvec[1][0], tvec[2][0])
        print("FANCY PNP", np.degrees(revec[0][0]), np.degrees(revec[1][0]), np.degrees(revec[2][0]))

        x, y = [(pts1[0][0] + pts1[3][0])/2, (pts1[0][1] + pts1[3][1])/2]
        pts2 = np.array([[0, 0], [100, 170], [300, 170], [400, 0]], np.float32)

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(frame, matrix, (400,170))
        cv2.imshow("warped", warped)
        yaw = np.arctan2(matrix[0][1],matrix[1][1])
        pitch = np.arcsin(matrix[2][1])
        roll = np.arctan2(matrix[2][0],matrix[2][2])

        x_scale = 2 * (x / frame.shape[1]) - 1
        y_scale = -(2 * (y / frame.shape[0]) - 1)

        azimuth = x_scale * kHorizontalFOVDeg / 2.0
        distance =(kTargetHeightIn - kCameraHeightIn) / np.tan(
            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

        #print("PERSPECTIVE TRANSFORM", np.degrees(yaw), np.degrees(pitch), np.degrees(roll))

        print("ONLY WORKING THING", azimuth, distance)

        #print(pts1)

    cv2.imshow('Output', res)
    #cv2.imshow('Output2', frame)
    #cv2.imshow("blur", blur)
    #print(np.degrees(yaw), np.degrees(pitch), np.degrees(roll))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return "done"
    # print("after wait")
    # return (distance, azimuth)

#im = cv2.imread("grt/BlueGoal-060in-Center.jpg")
cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("Error opening stream")
while True:
    #print(get_box(im))
    _, frame = cap.read()
    o = get_box(frame)
    if o == "done": break

f = open("VisionTracking/range_output", "w")
f.write(str([cv2.getTrackbarPos("H_min", "Output"), cv2.getTrackbarPos("S_min", "Output"), cv2.getTrackbarPos("V_min", "Output")]) + "\n")
f.write(str([cv2.getTrackbarPos("H_max", "Output"), cv2.getTrackbarPos("S_max", "Output"), cv2.getTrackbarPos("V_max", "Output")]))
f.flush()
f.close()