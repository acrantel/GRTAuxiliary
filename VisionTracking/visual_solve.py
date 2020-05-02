import cv2
import numpy as np
import json

# basic config reader, treats first word as key, everything else as value strings


def read_config(config_file):
    options = {}
    for l in config_file.readlines():
        # allow for comments that start with #
        if l[0] != '#':
            s = l.strip().split(' ')
            # combine back any spaces that were split up
            # also using slice notation avoids index out of range errors
            options[s[0]] = ' '.join(s[1:])
    return options


# read from range text file so easy to start off where left off
ranges = open(
    'VisionTracking/range_output.txt', 'r')
lower_range_start = list(json.loads(ranges.readline()))
upper_range_start = list(json.loads(ranges.readline()))

config = open(
    'VisionTracking/config.txt', 'r')
c = read_config(config)

verbose_printing = c['verbose_printing'] == 'True'
verbose_drawing = c['verbose_drawing'] == 'True'

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

# load camera matrix, distortion coeffs - they will be stored as a json object
camera_matrix = np.array(json.loads(c['camera_mtx']))
dist_coeffs = np.array(json.loads(c['dist_coeffs']))

# the points of the target on a completely flat 2D surface, with center being center of hex
# all units in inches
obj_points = []
obj_points.append([-19.631, 0, 0])  # top left
obj_points.append([-9.816, -17, 0])  # bottom left
obj_points.append([9.816, -17, 0])  # bottom right
obj_points.append([19.631, 0, 0])  # top right

obj_points = np.array(obj_points, np.float32)


# OpenCV requires that some function be called when a trackbar is changed


def nothing(x): pass


# create main display window that is scaled to be small so always fits
cv2.namedWindow('Output', cv2.WINDOW_NORMAL)

# trackbars that control the HSV mask, make very easy to tune
cv2.createTrackbar('H_min', 'Output', lower_range_start[0], 255, nothing)
cv2.createTrackbar('H_max', 'Output', upper_range_start[0], 255, nothing)
cv2.createTrackbar('S_min', 'Output', lower_range_start[1], 255, nothing)
cv2.createTrackbar('S_max', 'Output', upper_range_start[1], 255, nothing)
cv2.createTrackbar('V_min', 'Output', lower_range_start[2], 255, nothing)
cv2.createTrackbar('V_max', 'Output', upper_range_start[2], 255, nothing)

# decide whether a contour is actually vision target
# is this even necessary at all with good exposure and mask? probably not


def valid_hex_contour(cnt):
    area = cv2.contourArea(cnt)

    if area < min_area:
        return 0

    if verbose_printing:
        print('GOT PAST AREA CHECK WITH ', area)

    # minimum bounding rotated rectangle
    rect = cv2.minAreaRect(cnt)
    # convert to list of points so that it essentially becomes a contour
    box = np.int0(cv2.boxPoints(rect))
    rect_area = cv2.contourArea(box)

    # coverage metric scaled to max at 100 and decrease linearly
    diff_coverage = 100 - 100 * abs(area/rect_area - coverage_area)

    if diff_coverage < min_coverage:
        return 0

    if verbose_printing:
        print('GOT PAST COVERAGE CHECK WITH ', diff_coverage)

    # find the smallest polygon that forms a convex shape around contour
    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)

    solidity = float(area)/hull_area
    # solidity metric scaled to max at 100 and decrease linearly
    diff_solidity = 100 - 100 * abs(solidity - solidity_expect)

    if diff_solidity < min_solidity:
        return 0

    if verbose_printing:
        print('GOT PAST SOLIDITY CHECK WITH ', diff_solidity)

    # points are in an annoying format so make into nice 2D list
    hull_points = list(map(lambda x: x[0], hull.tolist()))

    # go through all hull points and eliminate ones that are closest to neighbors until only have 4 points
    # will end up getting 4 corners
    while len(hull_points) > 4:
        min_dist = [10000, 0]
        for i, p in enumerate(hull_points):
            x0, y0 = p
            x1, y1 = hull_points[i-1]
            x2, y2 = hull_points[(i+1) % len(hull_points)]
            # distance between point (x0) and a line (x1 - x2)
            d = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1) / \
                np.hypot((y2-y1), (x2-x1))
            if min_dist[0] > d:
                min_dist = [d, p]
        hull_points.remove(min_dist[1])

    # # TODO: test if this will work and don't need to do method above
    # # represents precision, higher = less precise
    # epsilon = 0.01*cv2.arcLength(hull, True)
    # # approximates contour to shape with number of vertices depending on precision
    # # always want to get 4 points or solvePNP will not work
    # approx = cv2.approxPolyDP(hull, epsilon, True)

    # sort by x-coordinate so know which corner each point is
    hull_points = sorted(hull_points, key=lambda x: x[0])

    if verbose_printing:
        print('4 APPROXIMATED POINTS ', hull_points)

    # order of points by x will go upper left, lower left, lower right, upper right
    top = (hull_points[0], hull_points[3])
    bot = (hull_points[1], hull_points[2])

    # distance between 2 top points and 2 bottom points, then compared
    dist_top = np.hypot(top[0][0]-top[1][0], top[0][1]-top[1][1])
    dist_bot = np.hypot(bot[0][0]-bot[1][0], bot[0][1]-bot[1][1])
    # hex ratio metric scaled to max at 100 and decrease linearly
    diff_hex_ratio = 100 - 100*abs(hex_ratio - dist_top/dist_bot)

    if diff_hex_ratio < min_hex_ratio:
        return 0

    if verbose_printing:
        print('GOT PAST HEX RATIO CHECK WITH ', diff_hex_ratio)

    return (hull_points, hull)


def get_position(frame):
    if verbose_printing:
        print('---------------------NEW FRAME---------------------')
    # user HSV because it is a lot easier than RGB to mask on because of its roundness
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # take values for mask from trackbars
    lower_range = np.array([cv2.getTrackbarPos('H_min', 'Output'), cv2.getTrackbarPos(
        'S_min', 'Output'), cv2.getTrackbarPos('V_min', 'Output')])
    upper_range = np.array([cv2.getTrackbarPos('H_max', 'Output'), cv2.getTrackbarPos(
        'S_max', 'Output'), cv2.getTrackbarPos('V_max', 'Output')])

    # create a binary mask of which pixels are in the specified range
    mask = cv2.inRange(hsv, lower_range, upper_range)
    # add that to image, and all pixels not in range will become 0, or black
    res = cv2.bitwise_and(frame, frame, mask=mask)

    # taking contours requires a black and white image, for that need to start with gray image
    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

    structure_element = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))

    # move all contours in by 4 pixels, move them out by 4 pixels
    # eliminates tiny flakes but anything larger than 4 pixels on each side will not be affected
    morphed = cv2.dilate(
        cv2.erode(imgray, structure_element), structure_element)

    # split image into black and white depending on whether its grayscale high is high enough
    ret, thresh = cv2.threshold(morphed, 64, 255, 0)

    # find all contours in image
    # RETR_EXTERNAL means to ignore contours inside other contours, vision target contour won't be inside another
    # CHAIN_APPROX_SIMPLE saves memory by only saving a couple of points per line instead of all of them
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    best_points = 0
    best_hull = 0
    best_poly = 0

    # sort contours by area so biggest ones are handled first
    contours = reversed(sorted(contours, key=cv2.contourArea))

    for cnt in contours:
        points = valid_hex_contour(cnt)
        if points != 0:
            best_points = points[0]
            best_hull = points[1]
            # once one matching contour is found, can ignore all others
            break

    # validation function returns 0 if contour failed validation
    if best_points != 0:

        if verbose_drawing:
            cv2.drawContours(res, [best_hull], 0, (255, 255, 0), thickness=3)
            for p in best_points:
                cv2.drawMarker(res, tuple(p), (0, 128, 255), thickness=4)

        # where the magic happens :)
        # takes in camera intrinsics and 2D points, and spits out 3D localization of camera
        # needs arrays to be in np array format
        retval, revec, tvec, inliers = cv2.solvePnPRansac(
            obj_points, np.array(best_points, np.float32), camera_matrix, dist_coeffs)

        # Rotation is given through revec
        print('ESTIMATED POSITION ROTATION ', np.degrees(revec[0][0]), np.degrees(
            revec[1][0]), np.degrees(revec[2][0]))

        # Translation is given through revec
        print('ESTIMATED POSITION TRANSLATION ',
              tvec[0][0], tvec[1][0], tvec[2][0])

    # res is original picture with mask
    cv2.imshow('Output', res)

    # if button q is pressed, end everything
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return 'done'


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('Error opening stream')

while True:
    _, frame = cap.read()
    o = get_position(frame)
    if o == 'done':
        break

# print out hsv range values to text file
# 3rd param specifies buffering mode, 1 means line buffered so don't have to flush
f = open('VisionTracking/range_output.txt', 'w', 1)

f.write(str([cv2.getTrackbarPos('H_min', 'Output'), cv2.getTrackbarPos(
    'S_min', 'Output'), cv2.getTrackbarPos('V_min', 'Output')]))
f.write('\n')
f.write(str([cv2.getTrackbarPos('H_max', 'Output'), cv2.getTrackbarPos(
    'S_max', 'Output'), cv2.getTrackbarPos('V_max', 'Output')]))
f.close()

cv2.destroyAllWindows()
