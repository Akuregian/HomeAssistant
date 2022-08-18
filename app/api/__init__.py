#__init__.py tells this is a package and not just a random folder

import os
import shelve

#import RaspberryPi GPIO framework
from RaspberryPi_GPIO import GPIO_Commands

#import framework
from flask import Flask, g, render_template, make_response
from flask_restful import Resource, Api, reqparse
from flask_session import Session
from flask_socketio import SocketIO, emit

# Create instance of Flask
app = Flask(__name__, template_folder="../templates", static_folder="../static")
# Create instance of API
api = Api(app)

Session(app)

socketio = SocketIO(app, manage_session=False)

# Raspiberry Pi Class in RaspberryPi_GPIO
rpi = GPIO_Commands()

# --------------- Calls to the database ------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("devices.db", writeback=True)
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# -------------------- Display README.md at homepage ------------------------------
@app.route("/")
def HomePage():
    return render_template('Homepage.html')

# When a button is pressed, the socket sends a message
# containg the devices name, which we use to update the database status
@socketio.on('status_update_db')
def update_status(data):
   # # Grab the database
    shelf = get_db()

   # If the key does not exist in the data store, return a 404 error.
    if not (data in shelf):
        return {'message': 'Device not found', 'data': {}}, 404

   # Change Status in the API
    if(shelf[data]['status'] == 0):
        shelf[data]['status'] = 1
    else:
        shelf[data]['status'] = 0

    status = shelf[data]['status']

    pipe_address = shelf[data]['writing_pipe_address']

    # Convert the hex Address of type string into a list of int's
    pipe_address_list = []
    for (first, second) in zip(pipe_address[2::2], pipe_address[3::2]):
        new_value = "0x"+first+second
        int_value = int(new_value, 16)
        pipe_address_list.append(int_value)

    rpi.CommunicateWithArduino(data, pipe_address_list, str(status))
    emit('Response', "Database Update for " + data + " " + str(status))

# -------------------- Toggle State Of Device [TESTING PURPOSES]  ------------------------------
@app.route('/devices/<string:identifier>/<int:status>')
def Toggle_Pin(identifier, status):

    # Grab the database
    shelf = get_db()

    # If the key does not exist in the data store, return a 404 error.
    if not (identifier in shelf):
        return {'message': 'Device not found', 'data': {}}, 404

    # Change Status in the API
    shelf[identifier]['status'] = status

    # Grab the Device's Writing_Pipe_Address
    pipe_address = shelf[identifier]['writing_pipe_address']

    # Conver the hex Address of type string into a list of int's
    pipe_address_list = []
    for (first, second) in zip(pipe_address[2::2], pipe_address[3::2]):
        new_value = "0x"+first+second
        int_value = int(new_value, 16)
        pipe_address_list.append(int_value)

    # Prepare the 'status' of type string into a char array to be sent
    status_to_char_arr = []
    status_to_char_arr.append(str(status))

    # Send the correct arduino a message to toggle a pin
    rpi.CommunicateWithArduino(pipe_address_list, status_to_char_arr)

    headers = {'Content-Type': 'text/html'}
    return make_response(render_template("Homepage.html"), 200, headers)


# -------------------- Methods = [GET, POST] - On Devices ------------------------------
class DeviceList(Resource):
    # GET's all the devices stores in the database
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        devices = []

        for key in keys:
            devices.append(shelf[key])

        return { 'message': 'Success', 'data': devices }

    def post(self):
        # Request Parser
        parser = reqparse.RequestParser()

        # Arguments for database, basically the table structure
        parser.add_argument('identifier', required=True, help="Type must be a String")
        parser.add_argument('device_type', required=True, help="Type must be a String")
        parser.add_argument('writing_pipe_address', required=True, help="Type must be a Integer")
        parser.add_argument('reading_pipe_address', required=True, help="Type must be a Integer")
        parser.add_argument('GPIO_Pin', required=True, type=int, help="Type must be a Integer")
        parser.add_argument('status', required=True, type=int, help="Type must be a Integer and only a 0 or 1", choices=[0, 1])

        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message' : 'Device Registered', 'data' : args }, 201

# -------------------- Methods = [GET, DELETE] - On Specific Devices ------------------------------
class Device(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404
        
        device_status = shelf[identifier]["status"]

        return { "status" : device_status }, 200

        #return {'message': 'Device found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Device not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204


api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/devices/<string:identifier>')