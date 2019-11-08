from flask import Flask, render_template, request, jsonify
import json
import threading
import random

app = Flask(__name__)

# A person wants to become a client
@app.route("/") 
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

lidar_data = []
scale = 1.7
robot_pos = [648*scale/2,324*scale/2]

@app.route('/getlidardata/', methods = ['POST'])
def lidardata():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)
        global lidar_data
        lidar_data = params
        return ""

# these two conenct to java
@app.route('/getposdata/', methods = ['POST'])
def posdata():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)
        global robot_pos
        robot_pos = params
        return ""

@app.route('/givealldata', methods=['POST'])
def posget():
    return jsonify([robot_pos, lidar_data]) # Send updated robot location information to the client

if __name__ == '__main__':
    app.run(debug=True)
