import cv2
import numpy as np
import socket

HOST = ''
PORT = 1337        # Port to listen on (non-privileged ports are > 1023)

vision_tape_area = 110.85
bounding_box = (40, 17)
bounding_box_area = bounding_box[0] * bounding_box[1]
coverage_area = vision_tape_area / bounding_box_area

hex_dim = (39.261, 19.360)
hex_ratio = hex_dim[0] / hex_dim[1]
hex_area = 3/2 * np.sqrt(3) * (hex_dim[0]/2)**2 / 2
solidity_expect = vision_tape_area / hex_area

max_diff_allow = 80
min_area = 100
min_coverage = 90
min_solidity = 90
min_hex_ratio = 70

kHorizontalFOVDeg = 62.8
kVerticalFOVDeg = 37.9

kTargetHeightIn = 8*12 + 2.25  # middle of hex height
kCameraHeightIn = 24
kCameraPitchDeg = 25

lower_green = np.array([0,0,250])
upper_green = np.array([30,10,255])

def law_of_cosines(a=None, b=None, c=None, opp_angle=None):
    if opp_angle is None:
        return np.degrees(np.arccos((c**2 - a**2 - b**2)/(-2*a*b)))
    else:
        opp_angle = np.radians(opp_angle)
        return np.sqrt(a**2 + b**2 - 2*a*b*np.cos(opp_angle))

cap = cv2.VideoCapture(0)

if not cap.isOpened(): 
    print("Error opening stream")

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while(cap.isOpened()):
                    distance = 0
                    azimuth = 0
                    x_rel = 0
                    y_rel = 0

                    _, frame = cap.read()

                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    mask = cv2.inRange(hsv, lower_green, upper_green)
                    res = cv2.bitwise_and(frame, frame, mask=mask)

                    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
                    
                    structure_element = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
                    morphed = cv2.dilate(cv2.erode(imgray, structure_element), structure_element)
                    ret, thresh = cv2.threshold(morphed, 64, 255, 0)

                    contours, hierarchy = cv2.findContours(
                        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]

                    best_hull = 0
                    best_diff = 0

                    for cnt in contours:
                        area = cv2.contourArea(cnt)
                        print(area)

                        if area < min_area:
                            continue

                        rect = cv2.minAreaRect(cnt)
                        box = np.int0(cv2.boxPoints(rect))
                        rect_area = cv2.contourArea(box)

                        diff_coverage = 100 - 100 * abs(area/rect_area - coverage_area)
                        
                        if diff_coverage < min_coverage:
                            continue

                        hull = cv2.convexHull(cnt)
                        hull_area = cv2.contourArea(hull)
                        solidity = float(area)/hull_area
                        diff_solidity = 100 - 100 * abs(solidity - solidity_expect)

                        hull = list(map(lambda x: x[0], hull.tolist()))

                        while len(hull) > 4:
                            min_dist = [10000,0]
                            for i,p in enumerate(hull):
                                x0, y0 = p
                                x1, y1 = hull[i-1]
                                x2, y2 = hull[(i+1)%len(hull)]
                                d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / np.hypot((y2-y1),(x2-x1))
                                if min_dist[0] > d:
                                    min_dist = [d,p]
                            hull.remove(min_dist[1])

                        hull = sorted(hull, key=lambda x: x[0])
                        top = (hull[0],hull[3])
                        bot = (hull[1],hull[2])
                        dist_top = np.hypot(top[0][0]-top[1][0], top[0][1]-top[1][1])
                        dist_bot = np.hypot(bot[0][0]-bot[1][0], bot[0][1]-bot[1][1])
                        diff_hex_ratio = 100 - 100*(hex_ratio - dist_top/dist_bot)

                        if diff_hex_ratio < min_hex_ratio or diff_solidity < min_solidity:
                            continue
                        
                        avg_diff = (diff_hex_ratio + diff_coverage + diff_solidity) / 3
                        if avg_diff > best_diff:
                            best_hull = hull
                            best_diff = avg_diff

                    if best_hull != 0:        
                        
                        pts1 = np.array(best_hull, np.float32)
                        left, right = pts1[0], pts1[3]

                        y_scale = -(2 * (left[1] / frame.shape[0]) - 1)
                        d1 =(kTargetHeightIn - kCameraHeightIn) / np.tan(
                            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))
                        
                        y_scale = -(2 * (right[1] / frame.shape[0]) - 1)
                        d2 =(kTargetHeightIn - kCameraHeightIn) / np.tan(
                            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

                        angle1 = law_of_cosines(a=max([d1,d2]), b=40, c=min([d1,d2]))
                        cd = law_of_cosines(a=max([d1,d2]),b=20,opp_angle=angle1)

                        final = law_of_cosines(a=cd, b=20, c=max([d1,d2]))
            
                        x_rel = cd * np.cos(np.radians(final))
                        y_rel = cd * np.sin(np.radians(final))
                        if d2 < d1: x_rel *= -1

                        x,y = [(left[0] + right[0])/2, (left[1] + right[1])/2]
                    
                        x_scale = 2 * (x / frame.shape[1]) - 1
                        y_scale = -(2 * (y / frame.shape[0]) - 1)

                        azimuth = x_scale * kHorizontalFOVDeg / 2.0
                        distance = (kTargetHeightIn - kCameraHeightIn) / np.tan(
                            np.radians(y_scale * (kVerticalFOVDeg / 2.0) + kCameraPitchDeg))

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    conn.send(bytes(str((distance,azimuth,x_rel,y_rel))+"\n","UTF-8"))
    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print("connection lost... retrying")
    
vid.release()
cv2.destroyAllWindows()
