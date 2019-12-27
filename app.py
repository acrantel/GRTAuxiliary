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
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(), 0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/other_video_feed')
def other_video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(), 1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

lidar_data = []

# start robot pos at middle of field
# pos will be given in mm
robot_pos = [6000, 3000]

# Java connects to this to send lidar data
# Data in form [[theta,r,Q],[theta,r,Q]...]
@app.route('/getlidardata/', methods = ['POST'])
def lidardata():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)   
        global lidar_data
        lidar_data = params
        # have to return some value
        return ""

# Java connects to this to send position data
# Data in form [x,y]
@app.route('/getposdata/', methods = ['POST'])
def posdata():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)
        global robot_pos
        robot_pos = params
        return ""

# Javascript connects to this to get all data for drawing 
@app.route('/givealldata', methods=['POST'])
def posget():
    return jsonify([robot_pos, lidar_data]) # Send updated robot location information to the client

button_clicked = ''

# Javascript connects to this to send button click events
@app.route('/getbuttondata/', methods = ['POST'])
def buttondata():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)
        global button_clicked
        button_clicked = params
        return ''

# Java connects to this to get button click events
@app.route('/givebuttondata/', methods = ['GET'])
def buttongive():
    if request.method == 'GET':
        return button_clicked

canvas_click = ''

# Javascript connects to this to send canvas click events
@app.route('/getclickdata/', methods = ['POST'])
def clickdata():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)
        global canvas_click
        canvas_click = params
        return ''

# Java connects to this to get canvas click events
@app.route('/givecanvasclick/', methods = ['GET'])
def clickgive():
    if request.method == 'GET':
        return canvas_click

# use python[3] app.py to start

# # of workers needs to be >= camera streams from different threaded videos can be used
if __name__ == '__main__':
    #app.run(debug=True)
    serve(app, host='0.0.0.0', port=5000)
