from flask import Flask, render_template, request, jsonify
import json
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

# A person wants to become a client
@app.route("/")
def index():
    return render_template("index.html") # Fetch index.html (and all it's subfiles) and give them out

@app.route('/getfield/', methods = ['POST'])
def get_field():
    if request.method == 'POST':
        decoded_data = request.data.decode('utf-8')
        params = json.loads(decoded_data)   
        print("hi")
        return "i got to java"

if __name__ == '__main__':
    app.run(debug=True)
