from flask import Flask, render_template, request, jsonify
import json
import threading
import random

app = Flask(__name__)

# homepage
@app.route("/") 
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

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
