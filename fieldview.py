from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

robLocation = {"x":10,"y":20} # todo: update this variable when you recieve latest robot coords

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

pos_string = "12.2 30.2"
