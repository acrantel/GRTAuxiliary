from flask import Flask, render_template, request, jsonify
import threading
import random

app = Flask(__name__)

# non-blocking implementation of setInterval
def setInterval(interval, times = -1):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1
            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap

robLocation = ""

def parse_xy (string):
    arr = string.split(" ")
    return {"x":arr[0], "y":arr[1]}

# make a new coord every 2 seconds
@setInterval(2)
def random_xy():
    global robLocation
    pos_string = str(random.randint(1, 648)) + " " + str(random.randint(1, 324))
    robLocation = parse_xy(pos_string)

stopper = random_xy()


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


