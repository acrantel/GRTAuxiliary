from flask import Flask, render_template, request, jsonify
import threading
import random

app = Flask(__name__)

def parse_xy (string):
    arr = string.split(" ")
    return {"x":arr[0], "y":arr[1]}

robLocation = ""

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def random_xy():
    global robLocation
    pos_string = str(random.randint(1, 648)) + " " + str(random.randint(1, 324))
    print(pos_string)
    robLocation = parse_xy(pos_string)

set_interval(random_xy, 2)

# A person wants to become a client
@app.route("/")
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

# The client is updating you with its robot requested location (mouse event) information.
@app.route('/locationpost', methods=['POST'])
def locpost():
    data = request.get_json()
    print(data)
    return "Location Updated" # Python wants you to return something

# The client is asking you to give it the robot's current location information.
@app.route('/locationget', methods=['POST'])
def locget():
    return jsonify(robLocation) # Send updated robot location information to the client

if __name__ == '__main__':
        app.run(debug=True)


