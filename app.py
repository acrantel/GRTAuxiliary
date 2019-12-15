from flask import Flask, render_template, request, jsonify, Response
import json
from importlib import import_module
import os
import camera_opencv

Camera = camera_opencv.Camera

app = Flask(__name__)

# homepage
@app.route("/") 
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

def gen(camera, source):
    """Video streaming generator function."""
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
    # change to 1 once get webcam
    return Response(gen(Camera(), 0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

lidar_data = []

# start robot pos at middle of field
# pos will be given in mm
robot_pos = [4115, 8230]

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

# Start app
if __name__ == '__main__':
    app.run(debug=True)
