#__init__.py tells this is a package and not just a random folder

import os
import time
import shelve

#import RaspberryPi GPIO framework
from RaspberryPi_GPIO import GPIO_Commands

#import framework
from flask import Flask, g, render_template, make_response, request, redirect, url_for
from flask_restful import Resource, Api, reqparse
from flask_socketio import SocketIO, emit

# Create instance of Flask
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "RaspberryPi"

# Create instance of API
api = Api(app)

# Create Instance of SocketIO Connection
socketio = SocketIO(app, manage_session=False)

# Raspiberry Pi Class in RaspberryPi_GPIO
rpi = GPIO_Commands()

# --------------- Calls to the database ------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("Database/devices.db", writeback=True)
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Login Route to access the Homepage (GUI-Interface)
@app.route("/", methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'anthony' or request.form['password'] != 'kuregian':
            error = "Invalid Credentials, Please Try Again."
        else:
            return render_template("Homepage.html")
    return render_template('Login.html')

@socketio.on('update_time')
def SendArduinoTime(data):
    rpi.SendCurrentTime()
    emit('update_response', 'updated_time')

# -------------------- SOCKETED CONNECTIONS ------------------------------
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
    device_name = shelf[data]["device_name"]

    # Convert the hex Address of type string into a list of int's
    pipe_address_list = []
    for (first, second) in zip(pipe_address[2::2], pipe_address[3::2]):
        new_value = "0x"+first+second
        int_value = int(new_value, 16)
        pipe_address_list.append(int_value)

    rpi.CommunicateWithArduino(data[-1], device_name, pipe_address_list, str(status))

# -------------------- Methods = [GET, POST] - On Devices ------------------------------
class DeviceList(Resource):
    # GET's all the devices stores in the database
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        devices = []

        for key in keys:
            devices.append(shelf[key])

        return { "data" : devices }

    def post(self):
        # Request Parser
        parser = reqparse.RequestParser()

        # Arguments for database, basically the table structure
        parser.add_argument('identifier', required=True)
        parser.add_argument('device_name', required=True)
        parser.add_argument('device_type', required=True)
        parser.add_argument('writing_pipe_address', required=True)
        parser.add_argument('GPIO_Pin', required=True, type=int)
        parser.add_argument('status', required=True, type=int, help="Type must be a Integer and only a 0 or 1", choices=[0, 1])

        args = parser.parse_args()

        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message' : 'Device Registered', 'data' : args }, 201

# -------------------- Methods = [GET, DELETE, PUT] - On Specific Devices -----------------
class Device(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message type=[GET]:': 'Device not found', 'data': identifier}, 404
        
        headers = {'Content-Type': 'text/html'}
        shelf.close()
        return make_response(render_template("ChangeDeviceName.html"), 200, headers)

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message type=[DELETE]': 'Device not found', 'data': {}}, 404

        del shelf[identifier]

        return '', 204

    def post(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message type=[POST]': 'Device not found', 'data': identifier}, 404

        results = request.form['new_name']

        shelf[identifier]['device_name'] = results
        shelf.close()

        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("Homepage.html"), 200, headers)

# Class is tied to a specified URL-Endpoint
api.add_resource(DeviceList, '/devices')
api.add_resource(Device, '/devices/<string:identifier>/')