from flask import Flask, render_template, request, jsonify, Response
import json
import os
from waitress import serve

app = Flask(__name__)

# homepage
@app.route("/") 
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

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

swerve_working = {
    "fl":1,
    "fr":1,
    "bl":1,
    "br":1
}

# Javascript connects to this to get which swerves are working
@app.route('/swervedata/', methods=['GET','POST'])
def swerveget():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))   
        global swerve_working
        swerve_working = data
        return ''
    elif request.method == 'GET':
        return jsonify(swerve_working) # Send updated robot location information to the client

lemon_count = 0

@app.route('/lemondata/', methods=['GET','POST'])
def lemonget():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))   
        global lemon_count
        lemon_count = data
        return ''
    elif request.method == 'GET':
        return jsonify(lemon_count) # Send updated robot location information to the client

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

timer_started = 'false';

# Java connects to this to send when to start timer (when game starts)
# Javascript connects to this to know when to start the timer
@app.route('/starttimer/', methods = ['POST','GET'])
def start_timer():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))  
        global timer_started
        timer_started = data
        return ''
    elif request.method == 'GET':
        return jsonify(timer_started)

# use python[3] app.py to start

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)