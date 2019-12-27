from flask import Flask, render_template, request, jsonify, Response
import json
from importlib import import_module
import os
import camera_opencv
from waitress import serve

Camera = camera_opencv.Camera

app = Flask(__name__)

# homepage
@app.route("/") 
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

# generator for camera frames
def gen(camera, source):
    """Video streaming generator function."""
    # source refers to OpenCV video capture source, 0 is usually computer webcam
    camera.set_video_source(source)
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera(), 0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/other_video_feed')
def other_video_feed():
    return Response(gen(Camera(), 1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Data in form [[theta,r,Q],[theta,r,Q]...]
lidar_data = []

# Java connects to this to send lidar data
@app.route('/getlidar/', methods = ['POST'])
def lidardata():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))   
        global lidar_data
        lidar_data = data
        # have to return some value
        return ''

# start robot pos at middle of field
# pos will be given in mm
# Data in form [x,y]
robot_pos = [6000, 3000]

# Java connects to this to send position data
@app.route('/getpos/', methods = ['POST'])
def posdata():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))   
        global robot_pos
        robot_pos = data
        return ''

# Javascript connects to this to get all data for drawing 
@app.route('/giveall/', methods=['GET'])
def posget():
    if request.method == 'GET':
        return jsonify([robot_pos, lidar_data]) # Send updated robot location information to the client

button_clicked = ''

# Javascript connects to this to send button click events
# Java connects to this to get button click events
@app.route('/buttondata/', methods = ['POST','GET'])
def buttondata():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))   
        global button_clicked
        button_clicked = data
        return ''
    elif request.method == 'GET':
        return button_clicked

canvas_click = ''

# Javascript connects to this to send canvas click events
# Java connects to this to get canvas click events
@app.route('/canvasdata/', methods = ['POST','GET'])
def clickdata():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        global canvas_click
        canvas_click = data
        return ''
    elif request.method == 'GET':
        return canvas_click

# use python[3] app.py to start

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)