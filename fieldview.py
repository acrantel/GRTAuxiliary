from flask import Flask, render_template, request, jsonify
import json
import threading
import random

app = Flask(__name__)

robLocation = ""

def parse_xy (string):
    arr = string.split(" ")
    return {"x":arr[0], "y":arr[1]}

# A person wants to become a client
@app.route("/") 
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

lidar_data = "no data"

@app.route('/getlidar/', methods = ['POST'])
def get_field():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)
        global lidar_data
        lidar_data = params
        return ""

@app.route('/locationget', methods=['POST'])
def locget():
    return jsonify(lidar_data) # Send updated robot location information to the client

if __name__ == '__main__':
    app.run(debug=True)
